import asyncio
import os
import sys
import datetime
import pytz
from sqlalchemy import select

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.engine.universe_scanner import UniverseScannerEngine
from app.engine.quote_sync import sync_and_overwrite_all_cmps_in_db
from app.engine.alert_engine import flush_and_generate_live_universe_alerts
from app.core.database import init_db, get_db_context
from app.domain.models import SystemMetaModel, TradePlanModel

IST = pytz.timezone("Asia/Kolkata")


async def main():
    print("=" * 80)
    print("[UNIVERSE REHYDRATION] Initializing Full NIFTY 500 GTF Achievement Scan...")
    print("=" * 80)
    await init_db()
    
    # 1. Run complete multi-timeframe zone scan with Opposing Violation checks
    engine = UniverseScannerEngine()
    results = await engine.run_full_universe_scan_async(lookback_days=180, min_achievements=2)
    
    # 2. Update System Scan Meta Date
    today_ist_str = datetime.datetime.now(IST).strftime("%Y-%m-%d")
    async with get_db_context() as db:
        stmt = select(SystemMetaModel).where(SystemMetaModel.key == "last_scan_date")
        res = await db.execute(stmt)
        meta = res.scalar_one_or_none()
        if meta:
            meta.value = today_ist_str
        else:
            db.add(SystemMetaModel(key="last_scan_date", value=today_ist_str))
        await db.commit()
        
    print(f"\n[SUMMARY] Successfully processed universe. Found {len(results)} qualifying setups:")
    for plan in results[:20]:
        direction_val = plan.direction.value if hasattr(plan.direction, "value") else str(plan.direction)
        broken_info = f" | Broken: Rs. {plan.broken_supply_level:.2f}" if getattr(plan, "broken_supply_level", None) else ""
        print(f" * {plan.symbol:<12} | {direction_val:<7} | ACH: {plan.achievements} | Score: {int(plan.conviction_score):>3}/100 | Entry: Rs. {plan.entry_price:.2f}{broken_info}")

    # 3. Synchronize verified continuous closing CMPs for all scanned stocks
    print("\n[UNIVERSE REHYDRATION] Step 2/3: Synchronizing live closing CMPs...")
    await sync_and_overwrite_all_cmps_in_db()

    # 4. Generate dynamic live multi-stock alerts across the universe
    print("\n[UNIVERSE REHYDRATION] Step 3/3: Generating dynamic universe alerts...")
    await flush_and_generate_live_universe_alerts()

    print("=" * 80)
    print("[UNIVERSE REHYDRATION COMPLETE] All stocks updated with GTF Achievements!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

