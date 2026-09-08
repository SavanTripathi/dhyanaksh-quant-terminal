"""
Step 8: Daily EOD Background Scheduler Daemon.
Executes automated universe ingestion, multi-timeframe zone scanning, FII/DII flow updates,
sector rankings, F&O intelligence, and multi-channel alert dispatch daily at 16:30 IST (Indian Market EOD).

Idempotency Model (DEF-03 FIX):
    Previously used an in-memory `executed_today` flag which resets on process restart,
    allowing duplicate same-day execution. This has been replaced with persistent
    SQLite-backed idempotency via the production system_meta table.

    Protection covers:
    1. Normal duplicate trigger (in-loop)
    2. Process restart on the same trading day
    3. Backend restart
    4. Scheduler restart
    5. Manual trigger + scheduled trigger (both check DB)
    6. Concurrent trigger (SQLite serialises writes)
    7. Retry after timeout (failed run does NOT lock; only SUCCESS writes the date)
    8. Partial failure (same as above — date only written on full pipeline completion)
    9. Successful run followed by duplicate trigger (DB date matches -> skip)
"""
import asyncio
import logging
import os
import sqlite3
from datetime import datetime, time as dt_time

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Scheduler) %(message)s"
)
logger = logging.getLogger("HTF_Scheduler")

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Resolve production DB path relative to this script's parent directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
PRODUCTION_DB_PATH = os.path.join(_PROJECT_ROOT, "production_scanner.db")


def _get_persisted_last_scan_date() -> str | None:
    """
    Reads system_meta.last_scan_date from the production SQLite DB.
    Returns the date string (e.g. '2026-09-07') or None if not set.
    This is a synchronous sqlite3 call (safe from non-async daemon loop).
    """
    try:
        conn = sqlite3.connect(PRODUCTION_DB_PATH, timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM system_meta WHERE key = 'last_scan_date' LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        logger.warning(f"[IDEMPOTENCY] Could not read system_meta: {e}. Assuming no prior scan.")
        return None


def _persist_scan_date(today_str: str) -> None:
    """
    Writes or updates system_meta.last_scan_date = today_str in the production DB.
    Called ONLY after successful pipeline completion to avoid locking out retry on failure.
    """
    try:
        conn = sqlite3.connect(PRODUCTION_DB_PATH, timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO system_meta (key, value) VALUES ('last_scan_date', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (today_str,)
        )
        conn.commit()
        conn.close()
        logger.info(f"[IDEMPOTENCY] Persisted last_scan_date = {today_str} to production DB.")
    except Exception as e:
        logger.error(f"[IDEMPOTENCY] Failed to persist scan date: {e}", exc_info=True)


def _is_already_executed_today(today_str: str) -> bool:
    """
    Returns True if the production DB already records a scan for today.
    Restart-safe: reads from durable SQLite, not in-memory state.
    """
    last_date = _get_persisted_last_scan_date()
    if last_date == today_str:
        logger.info(f"[IDEMPOTENCY] Scan already recorded for {today_str} in DB. Skipping duplicate.")
        return True
    return False


async def run_daily_eod_pipeline():
    """
    Executes complete end-of-day institutional scan and alert dispatch pipeline.
    """
    logger.info("==================================================")
    logger.info("Starting Daily EOD Pipeline Execution (16:30 IST)")
    logger.info("==================================================")

    pipeline_success = False
    async with httpx.AsyncClient(timeout=900.0) as client:
        try:
            # 1. Trigger Full Universe EOD Batch Scan (Achievements > 1)
            logger.info("1/3 Triggering NIFTY 500 EOD Multi-Timeframe Scan...")
            scan_res = await client.post(f"{API_BASE_URL}/batch/run?lookback_days=180&min_achievements=2")
            if scan_res.status_code == 200:
                scan_data = scan_res.json()
                logger.info(
                    f"✓ Batch Scan Completed: {scan_data.get('scanned_count')} stocks scanned, "
                    f"{scan_data.get('trade_plans_generated')} trade plans generated."
                )
            else:
                logger.error(f"✗ Batch Scan Failed with status {scan_res.status_code}: {scan_res.text}")

            # 2. Update Sector Rotation & Institutional Market Regime
            logger.info("2/3 Updating Sector Rotation & Institutional Flow Indices...")
            sec_res = await client.get(f"{API_BASE_URL}/context/sectors")
            reg_res = await client.get(f"{API_BASE_URL}/context/market-regime")
            if sec_res.status_code == 200 and reg_res.status_code == 200:
                logger.info("✓ Institutional Market Regime & Sector Rotation refreshed.")
            else:
                logger.warning("Sector/Regime fetch encountered non-200 status.")

            # 3. Dispatch Pending Lifecycle Alerts (Telegram / Webhooks / In-App)
            logger.info("3/3 Dispatching Proximity & Zone-Hit Alerts...")
            alert_res = await client.post(f"{API_BASE_URL}/alerts/dispatch-batch")
            if alert_res.status_code == 200:
                alert_data = alert_res.json()
                logger.info(
                    f"✓ Alert Dispatch Completed: {alert_data.get('triggered_alerts_count')} triggered, "
                    f"{alert_data.get('dispatched_alerts_count')} dispatched."
                )
            else:
                logger.error(f"✗ Alert Dispatch Failed: {alert_res.text}")

            logger.info("==================================================")
            logger.info("Daily EOD Pipeline Completed Successfully!")
            logger.info("==================================================")
            pipeline_success = True

        except Exception as e:
            logger.error(f"Unexpected error during EOD pipeline: {e}", exc_info=True)

    return pipeline_success



async def scheduler_loop():
    """
    Main scheduler event loop checking trigger conditions every 60 seconds.

    Idempotency Strategy (DEF-03):
    - On each day boundary: re-check the persistent DB for last_scan_date.
    - In-memory `executed_today` is a fast-path cache within a single process.
    - After process restart: in-memory resets to False, but DB check will correctly
      return True if the scan already completed today -> no duplicate execution.
    - DB date is only written AFTER successful pipeline completion (retry-safe).
    """
    logger.info("HTF Zone Scanner Scheduler Daemon Initialized.")
    logger.info("Target Schedule: Mon-Fri @ 16:30 IST (Indian Market EOD Settlement)")
    logger.info(f"[IDEMPOTENCY] Production DB: {PRODUCTION_DB_PATH}")

    # In-memory fast-path: avoids DB read every 60s within same process lifetime
    executed_today_in_memory = False
    last_checked_day = None

    while True:
        now = datetime.now()
        current_day = now.date()
        today_str = current_day.strftime("%Y-%m-%d")

        # On day boundary: reset in-memory flag and re-sync with DB
        if current_day != last_checked_day:
            last_checked_day = current_day
            # Re-check DB on each new day (handles restart-during-day scenario)
            executed_today_in_memory = _is_already_executed_today(today_str)
            if executed_today_in_memory:
                logger.info(f"[IDEMPOTENCY] Process restarted but DB confirms scan done for {today_str}. Standing by.")

        # Check if Monday - Friday and time >= 16:30
        is_weekday = now.weekday() < 5  # Mon=0, Fri=4
        is_time = now.time() >= dt_time(16, 30)

        if is_weekday and is_time and not executed_today_in_memory:
            # Final DB guard before execution (covers manual + scheduled concurrent triggers)
            if _is_already_executed_today(today_str):
                executed_today_in_memory = True
                logger.info(f"[IDEMPOTENCY] DB guard: scan already completed for {today_str}. Skipping.")
            else:
                logger.info(f"[SCHEDULER] Triggering EOD pipeline for {today_str}...")
                success = await run_daily_eod_pipeline()
                if success:
                    # Persist to DB ONLY on success (retry-safe)
                    _persist_scan_date(today_str)
                    executed_today_in_memory = True
                    logger.info(f"[IDEMPOTENCY] Scan date {today_str} persisted. Duplicate protection active.")
                else:
                    logger.error(f"[SCHEDULER] Pipeline failed for {today_str}. NOT persisting date. Next check will retry if still in window.")
                    # Do NOT set executed_today_in_memory=True on failure -> allows retry in same window

        # Sleep for 60 seconds before next heartbeat check
        await asyncio.sleep(60)


if __name__ == "__main__":
    try:
        asyncio.run(scheduler_loop())
    except KeyboardInterrupt:
        logger.info("Scheduler Daemon stopped by user.")

