import asyncio
from app.core.database import init_db
from app.engine.universe_scanner import UniverseScannerEngine

async def test_coforge():
    await init_db()
    scanner = UniverseScannerEngine()
    plans = await scanner.run_full_universe_scan_async(symbols=['COFORGE'])
    print(f"Total plans: {len(plans)}")
    for p in plans:
        if p.symbol == "COFORGE":
            print(f"Symbol: {p.symbol}")
            print(f"Direction: {p.direction}")
            print(f"Proximal Entry: {p.entry_price}")
            print(f"Distal Base: {p.overlap_min_price}")
            print(f"Broken Supply Level: {p.broken_supply_level}")
            print(f"Has Opposing Violation: {p.has_opposing_violation}")
            print(f"Timeframes: {p.participating_timeframes}")
            print(f"Achievements: {p.achievements}")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_coforge())
