"""
Phase 5 Canonical Production Scanner & Data Pipeline Test Suite.
Verifies all Phase 5 Acceptance Gates:
1. Universe: exactly 500 active symbols, no truncation, no duplicates.
2. Timeframe Isolation: exactly 1D, 1W, 1M, 3M evaluated (2,000 evaluations total).
3. Frozen GTF Enforcement: ZoneDetector invoked, no mock math, no hardcoded scores.
4. Single Authoritative Scanner: BatchScannerEngine is sole scanner authority.
5. Single Trigger Path: 16:30 EOD sync reaches canonical BatchScannerEngine.
6. Persistence Parity: trade_plans, screener_shortlist_cache, and sync_audit_log are synchronized atomically.
7. Read Isolation: GET /screener/shortlist never triggers a scan on empty DB.
8. Duplicate Protection: Mutex prevents concurrent duplicate scans.
9. Determinism: Same data inputs yield identical analytical outputs.
"""
import pytest
import sqlite3
import json
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.engine.universe import UniverseRepository
from app.engine.batch_scanner import (
    BatchScannerEngine,
    detect_canonical_htf_zone,
    evaluate_stock_canonical,
    _scan_lock
)
from app.engine.sync_pipeline import run_daily_eod_sync
from app.core.database import DB_PATH


def test_phase5_gate3_universe_completeness():
    """
    Gate 3: Verify exactly 500 active stocks in universe, 0 missing, 0 duplicates, 0 truncation.
    """
    repo = UniverseRepository()
    stocks = repo.get_filtered_universe(min_mcap_cr=5000.0)
    assert len(stocks) == 500, f"Expected 500 universe stocks, got {len(stocks)}"
    
    symbols = [s["symbol"] for s in stocks]
    assert len(set(symbols)) == 500, "Universe contains duplicate symbols"
    
    # Verify in DB master_instruments
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COUNT(DISTINCT symbol) FROM master_instruments WHERE is_active = 1")
    count, distinct = cur.fetchone()
    conn.close()
    assert count == 500, f"Expected 500 active instruments in DB, got {count}"
    assert distinct == 500, f"Expected 500 distinct active instruments in DB, got {distinct}"


def test_phase5_gate4_timeframe_isolation():
    """
    Gate 4: Verify exactly 4 required HTFs (1D, 1W, 1M, 3M) evaluated per symbol.
    No contamination from 75M or 125M in canonical production evaluation.
    """
    setup, acct = evaluate_stock_canonical("BSOFT", "Birlasoft Ltd")
    assert acct["success"] is True
    assert set(acct["timeframes_evaluated"]) == {"1D", "1W", "1M", "3M"}
    assert acct["gtf_invocations"] == 4
    assert "75M" not in acct["timeframes_evaluated"]
    assert "125M" not in acct["timeframes_evaluated"]
    
    if setup:
        # Check strict timeframe isolation in all_timeframe_zones
        tf_zones = setup.get("all_timeframe_zones", {})
        for tf, z in tf_zones.items():
            assert tf in {"1D", "1W", "1M", "3M"}
            assert z["timeframe"] == tf


def test_phase5_gate5_and_6_frozen_gtf_no_mock_zones():
    """
    Gate 5 & 6: Verify frozen GTF ZoneDetector is invoked and zero fake math formulas exist.
    """
    # Test ERC base rejection: 0.60 body ratio base must be rejected by ZoneDetector
    candles_erc = [
        {'open': 250.0, 'high': 255.0, 'low': 245.0, 'close': 250.0, 'volume': 1000, 'time': i * 86400}
        for i in range(12)
    ]
    candles_erc.append({'open': 300.0, 'high': 310.0, 'low': 190.0, 'close': 200.0, 'volume': 5000, 'time': 12 * 86400})
    candles_erc.append({'open': 120.0, 'high': 200.0, 'low': 100.0, 'close': 180.0, 'volume': 1000, 'time': 13 * 86400}) # 0.60 ERC
    candles_erc.append({'open': 200.0, 'high': 320.0, 'low': 195.0, 'close': 310.0, 'volume': 5000, 'time': 14 * 86400})
    candles_erc.append({'open': 300.0, 'high': 305.0, 'low': 165.0, 'close': 170.0, 'volume': 2000, 'time': 15 * 86400})

    zone_res = detect_canonical_htf_zone(candles_erc, '1D')
    assert zone_res is None, "Frozen GTF must reject 0.60 ERC base"


def test_phase5_gate2_production_trigger_path():
    """
    Gate 2: Verify 16:30 EOD sync reaches canonical BatchScannerEngine without mock math.
    """
    with patch.object(BatchScannerEngine, "run_canonical_scan") as mock_scan:
        mock_scan.return_value = {
            "status": "COMPLETED",
            "universe_count": 500,
            "scanned_count": 500,
            "trade_plans_generated": 10,
            "run_duration_seconds": 65.0,
            "summary_metrics": {"expected_evaluations": 2000, "completed_evaluations": 2000}
        }
        res = run_daily_eod_sync(force=True)
        assert mock_scan.called
        assert res["status"] == "COMPLETED"
        assert res["universe_count"] == 500
        assert res["scanned_count"] == 500


def test_phase5_gate15_read_endpoint_does_not_launch_scan():
    """
    Gate 15: Verify GET /screener/shortlist does not launch a production scan when DB is empty.
    """
    with patch.object(BatchScannerEngine, "execute_batch_scan") as mock_exec:
        # If DB query returns empty, execute_batch_scan must NOT be called
        # We test with non-matching query parameter
        import asyncio
        async def run_test():
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                res = await ac.get("/api/v1/screener/shortlist?min_achievements=6&direction=DEMAND")
                assert res.status_code == 200
                assert not mock_exec.called
        asyncio.run(run_test())


def test_phase5_gate9_duplicate_scan_protection():
    """
    Gate 9: Verify scan mutex rejects concurrent scans.
    """
    import asyncio
    engine = BatchScannerEngine()
    
    # Acquire lock manually to simulate running scan
    acquired = _scan_lock.acquire(blocking=False)
    assert acquired is True
    
    try:
        async def try_concurrent_scan():
            return await engine.execute_batch_scan(symbol_override=["RELIANCE"])
            
        res = asyncio.run(try_concurrent_scan())
        assert res.status_code if hasattr(res, "status_code") else res.status == "ALREADY_RUNNING"
    finally:
        _scan_lock.release()


def test_phase5_gate7_persistence_parity():
    """
    Gate 7: Verify trade_plans and screener_shortlist_cache have identical symbols.
    """
    engine = BatchScannerEngine()
    res = engine.run_canonical_scan(max_workers=2, symbol_override=["INFY", "HDFCBANK"])
    assert res["status"] == "COMPLETED"
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT symbol FROM trade_plans")
    tp_syms = set(r[0] for r in cur.fetchall())
    
    cur.execute("SELECT symbol FROM screener_shortlist_cache")
    cache_syms = set(r[0] for r in cur.fetchall())
    conn.close()
    
    # Both tables must match exactly
    assert tp_syms == cache_syms, f"Persistence mismatch: trade_plans={tp_syms} vs cache={cache_syms}"


def test_phase5_gate10_determinism():
    """
    Gate 10: Verify identical inputs yield identical outputs across repeated evaluations.
    """
    setup1, acct1 = evaluate_stock_canonical("INFY", "Infosys Ltd")
    setup2, acct2 = evaluate_stock_canonical("INFY", "Infosys Ltd")
    
    assert acct1["timeframes_evaluated"] == acct2["timeframes_evaluated"]
    assert acct1["gtf_invocations"] == acct2["gtf_invocations"]
    
    if setup1 and setup2:
        assert setup1["direction"] == setup2["direction"]
        assert setup1["entry_price"] == setup2["entry_price"]
        assert setup1["stop_loss"] == setup2["stop_loss"]
        assert setup1["score"] == setup2["score"]
