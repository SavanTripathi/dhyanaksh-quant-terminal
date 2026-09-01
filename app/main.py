import asyncio
import datetime
import pytz
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func

from app.core.config import settings
from app.core.database import engine, Base, init_db, get_db_context
from app.domain.models import SystemMetaModel, TradePlanModel
from app.api.v1.router import router as api_v1_router
from app.engine.universe_scanner import UniverseScannerEngine
from app.engine.scheduler import init_eod_scheduler, shutdown_scheduler
from app.engine.quote_sync import sync_and_overwrite_all_cmps_in_db
from app.engine.alert_engine import flush_and_generate_live_universe_alerts

IST = pytz.timezone("Asia/Kolkata")


async def run_universe_scan_with_date_lock(today_ist_str: str):
    """Executes the universe scan and updates the last scan date."""
    print("=" * 70)
    print(f"[SCAN ENGINE] Starting Full NIFTY 500 Universe Scan for {today_ist_str}...")
    print("=" * 70)
    
    engine_instance = UniverseScannerEngine()
    results = await engine_instance.run_full_universe_scan_async(
        lookback_days=180,
        min_achievements=2
    )
    
    async with get_db_context() as db:
        stmt = select(SystemMetaModel).where(SystemMetaModel.key == "last_scan_date")
        res = await db.execute(stmt)
        meta_record = res.scalar_one_or_none()
        if meta_record:
            meta_record.value = today_ist_str
        else:
            db.add(SystemMetaModel(key="last_scan_date", value=today_ist_str))
        await db.commit()
        
    print(f"[SCAN COMPLETE] Persisted {len(results)} qualifying setups into production_scanner.db")


async def check_and_run_first_launch_scan():
    """Checks if today has already been scanned; if not or if DB has < 10 setups, triggers the scan."""
    await asyncio.sleep(0.5)
    today_ist_str = datetime.datetime.now(IST).strftime("%Y-%m-%d")
    
    async with get_db_context() as db:
        meta_stmt = select(SystemMetaModel).where(SystemMetaModel.key == "last_scan_date")
        meta_res = await db.execute(meta_stmt)
        meta_record = meta_res.scalar_one_or_none()
        
        count_stmt = select(func.count(TradePlanModel.id))
        count_res = await db.execute(count_stmt)
        existing_count = count_res.scalar() or 0
        last_date = meta_record.value if meta_record else None

    # Condition: Date changed OR database is empty/unhydrated (< 10 records)
    if last_date != today_ist_str or existing_count < 10:
        print(f"[STARTUP AUDIT] First launch of date {today_ist_str} (DB plans: {existing_count}). Triggering auto-scan.")
        await run_universe_scan_with_date_lock(today_ist_str)
    else:
        print(f"[STARTUP AUDIT] Date {today_ist_str} already verified. Loaded {existing_count} setups from cache.")

    # Also ensure screener_shortlist_cache has cached multi-timeframe setups
    try:
        import sqlite3, os
        db_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "production_scanner.db")
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS screener_shortlist_cache (symbol TEXT PRIMARY KEY, data TEXT NOT NULL, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cur.execute("SELECT COUNT(*) FROM screener_shortlist_cache")
        cached_count = cur.fetchone()[0]
        conn.close()
        if cached_count < 10:
            print(f"[STARTUP CACHE AUDIT] screener_shortlist_cache has {cached_count} items. Running background universe scan...")
            from app.engine.full_batch_scanner import execute_live_universe_scan
            asyncio.create_task(asyncio.to_thread(execute_live_universe_scan, 10))
    except Exception as e:
        print(f"[STARTUP CACHE WARNING] {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize Database Tables
    await init_db()
    
    # 2. Start 16:30 IST Post-Market Scheduler
    init_eod_scheduler()
    
    # 3. Fire first-launch scan and alerts asynchronously with delay
    async def delayed_startup_workers():
        await asyncio.sleep(2.0)
        try:
            await check_and_run_first_launch_scan()
            await flush_and_generate_live_universe_alerts()
        except Exception as e:
            print(f"[STARTUP WORKER WARNING] {e}")

    asyncio.create_task(delayed_startup_workers())
    
    yield
    
    # Clean shutdown
    shutdown_scheduler()
    print("[SYSTEM] Shutting down Dhyanaksh background services.")


app = FastAPI(
    title="Dhyanaksh — HTF Supply & Demand Quant Terminal",
    description="Institutional Supply and Demand Multi-Timeframe Zone Scanner with Strict Fresh Spatial Overlap (Achievements > 1)",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Dhyanaksh — HTF Supply & Demand Quant Terminal API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
