"""
Universe Scanner Engine.
Orchestrates full universe multi-timeframe scans, computes trade plans, and returns results.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import AsyncSessionLocal
from app.domain.models import TradePlanModel
from app.domain.schemas import TradePlanSchema
from app.engine.batch_scanner import BatchScannerEngine


class UniverseScannerEngine:
    def __init__(self):
        self.batch_scanner = BatchScannerEngine()

    async def run_full_universe_scan_async(
        self,
        lookback_days: int = 180,
        min_achievements: int = 2,
        min_mcap_cr: float = 5000.0,
        symbols: Optional[List[str]] = None
    ) -> List[TradePlanModel]:
        """
        Executes full NIFTY 500 universe scan across all session-aligned timeframes,
        populates production database, and returns all persisted qualifying TradePlanModel records.
        """
        async with AsyncSessionLocal() as db:
            await self.batch_scanner.execute_batch_scan(
                db=db,
                lookback_days=lookback_days,
                min_achievements=min_achievements,
                min_mcap_cr=min_mcap_cr,
                symbol_override=symbols
            )
            # Retrieve all freshly saved trade plans sorted by conviction_score descending
            stmt = select(TradePlanModel).order_by(desc(TradePlanModel.conviction_score))
            res = await db.execute(stmt)
            plans = list(res.scalars().all())
            return plans
