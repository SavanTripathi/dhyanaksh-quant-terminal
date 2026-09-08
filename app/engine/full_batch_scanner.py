"""
Full NIFTY 500 Batch Scanner Facade.
Delegates directly to the authoritative canonical BatchScannerEngine to prevent competing production scanners.
Preserves _detect_canonical_htf_zone for test backwards-compatibility.
"""
import logging
from typing import Dict, List, Optional

from app.engine.batch_scanner import (
    BatchScannerEngine,
    detect_canonical_htf_zone as _detect_canonical_htf_zone,
    evaluate_stock_canonical,
    _ensure_tables as _ensure_cache_table
)

logger = logging.getLogger(__name__)


def evaluate_stock_all_timeframes(sym: str, name: str) -> Optional[Dict]:
    """
    Delegates to canonical evaluation for 1D, 1W, 1M, 3M.
    """
    setup, _ = evaluate_stock_canonical(sym, name)
    return setup


def execute_live_universe_scan(max_workers: int = 10) -> List[Dict]:
    """
    Executes authoritative canonical scan and returns list of qualifying setups.
    """
    engine = BatchScannerEngine()
    run_res = engine.run_canonical_scan(max_workers=max_workers)
    
    # Read back synchronized cached setups
    import sqlite3
    import json
    from app.core.database import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM screener_shortlist_cache ORDER BY symbol")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        try:
            results.append(json.loads(r[0]))
        except Exception:
            continue
            
    print(f"[OK] Canonical scan populated database with {len(results)} active NIFTY 500 setups.")
    return results


def run_full_nifty500_scanner(max_workers: int = 10):
    """
    Background worker entrypoint calling authoritative canonical scanner.
    """
    return execute_live_universe_scan(max_workers=max_workers)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    execute_live_universe_scan()
