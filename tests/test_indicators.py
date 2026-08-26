"""
Unit tests for Indicator Engine (ATR-14, EMA-20, EMA-50, SMA-200, ATR buffer).
"""
import pytest
import pandas as pd
import numpy as np
from app.engine.indicators import IndicatorEngine


def test_indicator_engine_atr():
    """
    Test vectorized True Range and ATR calculation.
    """
    # Create known 20-day price series
    data = []
    base = 100.0
    for i in range(20):
        # Range of 5 points each day
        data.append({
            "timestamp": pd.Timestamp("2026-01-01") + pd.Timedelta(days=i),
            "open": base,
            "high": base + 4.0,
            "low": base - 1.0,
            "close": base + 2.0,
            "volume": 1000
        })
        base += 1.0

    df = pd.DataFrame(data).set_index("timestamp")
    atr_series = IndicatorEngine.calculate_atr(df, period=14)

    assert len(atr_series) == 20
    # True range for high-low=5, prev_close=102 vs high=105 -> 4 etc. Average should be ~5.0
    assert 4.0 <= atr_series.iloc[-1] <= 6.0


def test_indicator_engine_emas_and_smas():
    """
    Test EMA 20, EMA 50, and SMA 200 calculations.
    """
    dates = pd.date_range("2025-01-01", periods=250, freq="D")
    prices = np.linspace(100, 200, 250)
    df = pd.DataFrame({
        "open": prices,
        "high": prices + 2,
        "low": prices - 2,
        "close": prices,
        "volume": 5000
    }, index=dates)

    indicators = IndicatorEngine.compute_daily_indicators(df)

    assert indicators["current_price"] == 200.0
    assert indicators["atr_14"] > 0
    assert indicators["atr_buffer"] == round(0.20 * indicators["atr_14"], 2)
    assert indicators["ema_20"] < indicators["current_price"]  # In uptrend, EMA < Close
    assert indicators["ema_50"] < indicators["ema_20"]
    assert indicators["sma_200"] < indicators["ema_50"]
