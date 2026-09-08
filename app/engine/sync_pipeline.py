"""
Canonical EOD Synchronization Pipeline.
Triggered at 16:30 IST by GitHub Actions or manual dispatch.
Invokes the single authoritative canonical BatchScannerEngine across the entire NIFTY 500 universe (500 symbols x 4 HTFs = 2,000 evaluations).
Eliminates universe truncation (symbols[:30]) and all fake mock zone calculations.
"""
import os
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict

from app.services.holiday_calendar import is_trading_day
from app.engine.batch_scanner import BatchScannerEngine

logger = logging.getLogger(__name__)


def run_daily_eod_sync(force: bool = False) -> Dict:
    """
    Executes authoritative 16:30 IST market scan and sync:
    1. Validates trading session via holiday calendar.
    2. Invokes canonical BatchScannerEngine across 500 NIFTY equities.
    3. Evaluates 1D, 1W, 1M, 3M via frozen GTF engine (2,000 evaluations).
    4. Persists trade plans, cache, and audit log atomically.
    """
    run_id = str(uuid.uuid4())[:8]
    start_time = datetime.now(timezone.utc)
    sync_date = start_time.strftime("%Y-%m-%d")

    print(f"[{run_id}] Starting 16:30 IST Canonical Market Sync Pipeline for {sync_date} (force={force})...")

    if not force and not is_trading_day():
        print(f"[{run_id}] Non-trading day or market holiday. Exiting cleanly.")
        return {
            "run_id": run_id,
            "status": "SKIPPED_HOLIDAY",
            "message": "Today is a non-trading session or holiday."
        }

    engine = BatchScannerEngine()
    scan_result = engine.run_canonical_scan(max_workers=10)

    print(f"[{run_id}] Canonical scan complete: {scan_result.get('status', 'UNKNOWN')} in {scan_result.get('run_duration_seconds', 0)}s.")
    return {
        "run_id": run_id,
        "status": scan_result.get("status", "COMPLETED"),
        "sync_date": sync_date,
        "universe_count": scan_result.get("universe_count", 500),
        "scanned_count": scan_result.get("scanned_count", 500),
        "trade_plans_generated": scan_result.get("trade_plans_generated", 0),
        "run_duration_seconds": scan_result.get("run_duration_seconds", 0.0),
        "summary_metrics": scan_result.get("summary_metrics", {})
    }


if __name__ == "__main__":
    run_daily_eod_sync(force=True)
