import asyncio
from app.engine.batch_scanner import BatchScannerEngine
from app.core.database import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        scanner = BatchScannerEngine()
        res = await scanner.execute_batch_scan(db, lookback_days=730, min_achievements=2)
        print(f"Universe: {res.universe_count} | Scanned: {res.scanned_count} | Plans: {res.trade_plans_generated}")

if __name__ == "__main__":
    asyncio.run(main())
