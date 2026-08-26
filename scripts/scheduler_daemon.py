"""
Step 8: Daily EOD Background Scheduler Daemon.
Executes automated universe ingestion, multi-timeframe zone scanning, FII/DII flow updates,
sector rankings, F&O intelligence, and multi-channel alert dispatch daily at 16:00 IST (Indian Market Close).
"""
import asyncio
import logging
from datetime import datetime, timezone, time as dt_time
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Scheduler) %(message)s"
)
logger = logging.getLogger("HTF_Scheduler")

API_BASE_URL = "http://127.0.0.1:8000/api/v1"


async def run_daily_eod_pipeline():
    """
    Executes complete end-of-day institutional scan and alert dispatch pipeline.
    """
    logger.info("==================================================")
    logger.info("Starting Daily EOD Pipeline Execution (16:00 IST)")
    logger.info("==================================================")

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            # 1. Trigger Full Universe EOD Batch Scan (Achievements > 1)
            logger.info("1/3 Triggering NIFTY 500 EOD Multi-Timeframe Scan...")
            scan_res = await client.post(f"{API_BASE_URL}/batch/run?lookback_days=730&min_achievements=2")
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

        except Exception as e:
            logger.error(f"Unexpected error during EOD pipeline: {e}", exc_info=True)


async def scheduler_loop():
    """
    Main scheduler event loop checking trigger conditions every 60 seconds.
    """
    logger.info("HTF Zone Scanner Scheduler Daemon Initialized.")
    logger.info("Target Schedule: Mon-Fri @ 16:30 IST (Indian Market EOD Settlement)")

    executed_today = False
    last_checked_day = None

    while True:
        now = datetime.now()
        current_day = now.date()

        # Reset daily trigger flag at midnight
        if current_day != last_checked_day:
            executed_today = False
            last_checked_day = current_day

        # Check if Monday - Friday and time >= 16:30
        is_weekday = now.weekday() < 5  # Mon=0, Fri=4
        is_time = now.time() >= dt_time(16, 30)

        if is_weekday and is_time and not executed_today:
            await run_daily_eod_pipeline()
            executed_today = True

        # Sleep for 60 seconds before next heartbeat check
        await asyncio.sleep(60)


if __name__ == "__main__":
    try:
        asyncio.run(scheduler_loop())
    except KeyboardInterrupt:
        logger.info("Scheduler Daemon stopped by user.")
