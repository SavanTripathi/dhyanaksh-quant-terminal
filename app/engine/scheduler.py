import asyncio
import logging
import pytz
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.core.database import get_db_context
from app.domain.models import SystemMetaModel
from app.engine.universe_scanner import UniverseScannerEngine
from app.engine.quote_sync import sync_and_overwrite_all_cmps_in_db

logger = logging.getLogger("dhyanaksh.scheduler")

scheduler = AsyncIOScheduler()
IST = pytz.timezone("Asia/Kolkata")
scanner_engine = UniverseScannerEngine()


async def run_daily_eod_pipeline():
    """
    Automated Institutional EOD Scan & Hard Overwrite:
    1. Ingests daily NSE market data & settlement prices for universe.
    2. Recalculates HTF Demand/Supply zones.
    3. Executes hard SQL update on production_scanner.db with official settlement quotes.
    4. Sets system_meta.last_scan_date = today_ist.
    """
    today_ist_str = datetime.now(IST).strftime("%Y-%m-%d")
    print("=" * 70)
    print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}] [CRON 16:30] Initiating daily post-market scan & hard overwrite...")
    print("=" * 70)
    logger.info(f"[CRON 16:30] Initiating daily 16:30 IST NSE Scan for {today_ist_str}...")

    try:
        results = await scanner_engine.run_full_universe_scan_async(
            lookback_days=180,
            min_achievements=2
        )
        
        # Ensure immediate hard overwrite with official settlement quotes
        await sync_and_overwrite_all_cmps_in_db()

        async with get_db_context() as db:
            stmt = select(SystemMetaModel).where(SystemMetaModel.key == "last_scan_date")
            res = await db.execute(stmt)
            meta = res.scalar_one_or_none()
            if meta:
                meta.value = today_ist_str
            else:
                db.add(SystemMetaModel(key="last_scan_date", value=today_ist_str))
            await db.commit()

        print(f"[CRON 16:30 COMPLETE] Persisted and updated {len(results)} setups into production_scanner.db for {today_ist_str}.")
        logger.info(f"[CRON 16:30 COMPLETE] Persisted {len(results)} setups for {today_ist_str}.")
    except Exception as e:
        logger.error(f"[CRON 16:30 ERROR] {e}", exc_info=True)
        print(f"[CRON 16:30 ERROR] {e}")


def init_eod_scheduler():
    """
    Initializes and starts APScheduler for automated 16:30 IST post-market cron every Monday-Friday.
    """
    trigger = CronTrigger(
        day_of_week="mon-fri",
        hour=16,
        minute=30,
        timezone=IST
    )
    scheduler.add_job(
        run_daily_eod_pipeline,
        trigger=trigger,
        id="daily_eod_pipeline",
        name="Daily NSE EOD 16:30 IST Auto-Pipeline",
        replace_existing=True
    )
    if not scheduler.running:
        scheduler.start()
        logger.info("[SCHEDULER] Daily 16:30 IST EOD Scheduler initialized and active.")
        print("[SCHEDULER] Daily 16:30 IST EOD Scheduler initialized and active.")


def shutdown_scheduler():
    """
    Gracefully shuts down scheduler.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[SCHEDULER] EOD Scheduler shut down.")
