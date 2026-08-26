import asyncio
import os
import sys
import datetime
import pytz
from sqlalchemy import select

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.engine.universe_scanner import UniverseScannerEngine
from app.core.database import init_db, get_db_context
from app.domain.models import SystemMetaModel, TradePlanModel

IST = pytz.timezone("Asia/Kolkata")


async def main():
    print("=" * 70)
    print("DHYANAKSH QUANT TERMINAL -- MANUAL FULL UNIVERSE SCANNER")
    print("=" * 70)
    await init_db()
    
    engine = UniverseScannerEngine()
    results = await engine.run_full_universe_scan_async(lookback_days=180, min_achievements=2)
    
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
    for plan in results[:30]:  # Show top 30
        direction_val = plan.direction.value if hasattr(plan.direction, "value") else str(plan.direction)
        print(f" * {plan.symbol:<12} | {direction_val:<7} | ACH: {plan.achievements} | Score: {int(plan.conviction_score):>3}/100 | Entry: Rs. {plan.entry_price:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
