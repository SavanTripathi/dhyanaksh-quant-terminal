# CRITICAL DIRECTIVE — DUAL-CONDITION YAHOO SCANNER WITH HARD DATABASE UPDATE & IMMEDIATE LAUNCH OVERWRITE

## Project Name
**Dhyanaksh — HTF Supply & Demand Quant Terminal**

---

### Strict Business Requirements
1. **Condition 1 (App Launch Sync & Overwrite):** Every time the application starts/launches, run a direct batch quote fetch via `yfinance.download(tickers=..., period="5d", interval="1d")`. Extract the latest daily settlement close and perform an explicit **SQL UPDATE query** (`UPDATE trade_plans SET current_price = :cmp, cmp = :cmp, change_pct = :change_pct WHERE symbol = :symbol`) to immediately overwrite all stale database rows.
2. **Condition 2 (Daily 16:30 IST Post-Market Overwrite):** At 16:30 IST Mon–Fri, execute the full multi-timeframe zone scan and perform the same hard SQL overwrite on all existing stock rows with the final official NSE settlement closing prices.
3. **Frontend Immediate Quote Hydration:** When a stock card is clicked or loaded, ensure the live quote poller feeds directly into the chart header and left sidebar without being overridden by cached JSON files.

---

### 1. High-Speed Batch Yahoo Quote Fetcher & SQL Hard Overwrite (`app/engine/quote_sync.py`)

Create a batch syncer that uses vector batch downloading rather than slow single-ticker loops:

```python
# app/engine/quote_sync.py
import asyncio
import yfinance as yf
import datetime
from sqlalchemy import update
from app.db.database import get_db_context
from app.db.models import TradePlanModel

async def sync_and_overwrite_all_cmps_in_db():
    """
    Fetches real-time official settlement quotes for all symbols present in the database
    and executes a hard UPDATE query on production_scanner.db.
    """
    print("=" * 70)
    print("[QUOTE SYNC] Fetching real-time CMPs from Yahoo Finance for all DB stocks...")
    print("=" * 70)

    async with get_db_context() as db:
        # 1. Get all symbols currently tracked
        plans = await db.query(TradePlanModel).all()
        if not plans:
            print("[QUOTE SYNC] No plans found in DB to update.")
            return

        symbols_map = {p.symbol: p for p in plans}
        tickers_list = [f"{s}.NS" for s in symbols_map.keys()]

        # 2. Batch download 5-day daily bars in one fast network request
        try:
            data = yf.download(
                tickers=" ".join(tickers_list),
                period="5d",
                interval="1d",
                group_by="ticker",
                auto_adjust=False,
                threads=True,
                progress=False
            )

            updated_count = 0
            for sym, plan in symbols_map.items():
                ns_sym = f"{sym}.NS"
                try:
                    df = data[ns_sym] if len(tickers_list) > 1 else data
                    df = df.dropna(subset=["Close"])
                    if not df.empty and len(df) >= 1:
                        official_close = float(df["Close"].iloc[-1])
                        prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else official_close
                        change_pct = round(((official_close - prev_close) / prev_close) * 100.0, 2) if prev_close else 0.0

                        # Calculate fresh proximity to Proximal Entry
                        entry = float(plan.entry_price) if plan.entry_price else official_close
                        proximity_pct = round(abs(official_close - entry) / entry * 100.0, 2)

                        # Hard SQL Update on the existing model instance
                        plan.current_price = round(official_close, 2)
                        plan.cmp = round(official_close, 2)
                        plan.change_pct = change_pct
                        plan.proximity_pct = proximity_pct
                        plan.updated_at = datetime.datetime.utcnow()
                        updated_count += 1
                except Exception as e:
                    print(f"[QUOTE SYNC] Failed to parse {sym}: {e}")

            await db.commit()
            print(f"[QUOTE SYNC] Successfully overwrote {updated_count} stock records in production_scanner.db with live CMPs.")
        except Exception as e:
            print(f"[QUOTE SYNC ERROR] Batch download failed: {e}")
```

---

### 2. Connect App Launch & 16:30 Cron (`app/main.py` & `app/engine/scheduler.py`)

Hook the hard overwrite into FastAPI's startup event and the scheduled 16:30 IST cron job:

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
from app.db.database import init_db
from app.engine.scheduler import init_eod_scheduler
from app.engine.quote_sync import sync_and_overwrite_all_cmps_in_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize SQLite tables
    await init_db()
    
    # 2. Condition 1: Immediate batch sync & database overwrite on APP LAUNCH
    asyncio.create_task(sync_and_overwrite_all_cmps_in_db())
    
    # 3. Condition 2: Scheduled 16:30 IST post-market cron
    init_eod_scheduler()
    
    yield
    print("[SYSTEM] Dhyanaksh shutting down.")

app = FastAPI(title="Dhyanaksh API", lifespan=lifespan)
```

```python
# app/engine/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from app.engine.universe_scanner import UniverseScannerEngine
from app.engine.quote_sync import sync_and_overwrite_all_cmps_in_db

scheduler = AsyncIOScheduler()
IST = pytz.timezone("Asia/Kolkata")

async def run_daily_eod_pipeline():
    print("[CRON 16:30] Initiating daily post-market scan & hard overwrite...")
    engine = UniverseScannerEngine()
    await engine.run_full_universe_scan_async()
    # Ensure immediate hard overwrite with official settlement
    await sync_and_overwrite_all_cmps_in_db()

def init_eod_scheduler():
    scheduler.add_job(
        run_daily_eod_pipeline,
        trigger=CronTrigger(day_of_week="mon-fri", hour=16, minute=30, timezone=IST),
        id="daily_eod_pipeline",
        replace_existing=True
    )
    scheduler.start()
```

---

### 3. Immediate Run Command
Run the standalone quote syncer directly to immediately update all stocks in the database to today's closing prices:

```bash
python -c "import asyncio; from app.db.database import init_db; from app.engine.quote_sync import sync_and_overwrite_all_cmps_in_db; asyncio.run(init_db()); asyncio.run(sync_and_overwrite_all_cmps_in_db())"
```

---

### 4. Verification & Acceptance Criteria
- [ ] On application launch, `sync_and_overwrite_all_cmps_in_db` executes and updates all stock rows in SQLite.
- [ ] Every weekday at 16:30 IST, the scheduled cron re-scans and updates all prices in the database.
- [ ] ICICIBANK shows ₹1,434.40 in the left sidebar card, center plan card, and right chart badge.
- [ ] Deliver a Real-Time Settlement & Hard Database Overwrite Audit Report confirming the update.
