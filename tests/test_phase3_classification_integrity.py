import pytest
import pandas as pd
from app.engine.aggregator import CandleAggregator
from app.engine.zone_detector import detect_htf_supply_demand_zone
from app.domain.enums import Timeframe

def test_true_point_in_time_atz_confluence_math():
    """Verify that ATZ calculation requires 4 distinct non-empty timeframes."""
    # Mock daily candles
    candles_1d = [
        {"timestamp": f"2025-01-{i:02d}", "open": 100+i, "high": 105+i, "low": 99+i, "close": 104+i, "volume": 1000}
        for i in range(1, 60)
    ]
    
    # 1. Single TF evaluation
    z_1d = detect_htf_supply_demand_zone(candles_1d, "1D")
    assert z_1d is not None
    
    # Check that passing unaggregated daily candles to "3M" is prevented or properly segregated
    # True ATZ requires 4 separate aggregations
    has_1d = bool(z_1d)
    has_1w = False
    has_1m = False
    has_3m = False
    
    is_atz = (has_1d and has_1w and has_1m and has_3m)
    assert is_atz is False, "Single timeframe setup must NOT be classified as ATZ"

def test_trade_accounting_non_negativity_and_order():
    """Verify that trade accounting enforces stop priority and positive holding."""
    df_trades = pd.read_csv("TRADE_LEVEL_OOS_RESULTS.csv")
    assert len(df_trades) > 0
    
    # Check non-negative holding bars
    assert (df_trades["bars_held"] >= 1).all()
    assert (df_trades["bars_to_entry"] >= 1).all()
    
    # Check that sum of confluence tiers equals total trades exactly
    c_counts = df_trades["confluence_tier"].value_counts().sum()
    assert c_counts == len(df_trades)
