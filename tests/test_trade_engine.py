"""
Unit tests for Deterministic Trade Engine:
- Exact mathematical formulas for Demand Setup (Entry, SL, Targets, R, Distance %, Approaching flag)
- Exact mathematical formulas for Supply Setup (Entry, SL, Targets, R, Distance %, Approaching flag)
- Moving Average Confluence Layer (50 EMA & 200 SMA inside zone)
"""
from datetime import datetime
import pytest
from app.domain.enums import Timeframe, ZoneDirection, FreshnessStatus, ZoneStructure
from app.domain.schemas import SpatialOverlapCluster, ZoneSchema
from app.engine.trade_engine import TradeEngine


def test_trade_engine_demand_setup_math():
    """
    Given:
    Cluster: Demand [1000.0, 1050.0] -> L_common=1000.0, H_common=1050.0
    ATR_1D(14) = 25.0 -> Buffer = 0.20 * 25.0 = 5.0
    Current Price = 1060.0

    Expected Demand Formulas:
    - Entry = H_common = 1050.0
    - SL = L_common - buffer = 1000.0 - 5.0 = 995.0
    - R = Entry - SL = 1050.0 - 995.0 = 55.0
    - Target 1 (2.0R) = 1050.0 + (2.0 * 55.0) = 1160.0
    - Target 2 (3.5R) = 1050.0 + (3.5 * 55.0) = 1242.5
    - Target 3 (5.0R) = 1050.0 + (5.0 * 55.0) = 1325.0
    - Distance % = ((1060.0 - 1050.0) / 1060.0) * 100 = (10 / 1060) * 100 = 0.94%
    - Approaching Flag: 0.94% <= 2.5% -> True
    """
    cluster = SpatialOverlapCluster(
        symbol="RELIANCE",
        direction=ZoneDirection.DEMAND,
        overlap_min_price=1000.0,
        overlap_max_price=1050.0,
        achievements=3,
        participating_timeframes=[Timeframe.MONTHLY, Timeframe.WEEKLY, Timeframe.DAILY],
        zones=[]
    )

    indicators = {
        "current_price": 1060.0,
        "atr_14": 25.0,
        "atr_buffer": 5.0,
        "ema_20": 1070.0,
        "ema_50": 1025.0,  # Nested within [995.0, 1055.0] -> MA Confluence = True
        "sma_200": 950.0
    }

    plan = TradeEngine.generate_trade_plan(cluster, indicators)

    assert plan.symbol == "RELIANCE"
    assert plan.direction == ZoneDirection.DEMAND
    assert plan.entry_price == 1050.0
    assert plan.stop_loss == 995.0
    assert plan.risk_per_share == 55.0
    assert plan.target_1 == 1160.0
    assert plan.target_2 == 1242.5
    assert plan.target_3 == 1325.0
    assert plan.distance_pct == 0.94
    assert plan.is_approaching is True
    assert plan.has_ma_confluence is True
    assert plan.achievements == 3


def test_trade_engine_supply_setup_math():
    """
    Given:
    Cluster: Supply [2000.0, 2080.0] -> L_common=2000.0, H_common=2080.0
    ATR_1D(14) = 50.0 -> Buffer = 0.20 * 50.0 = 10.0
    Current Price = 1960.0

    Expected Supply Formulas:
    - Entry = L_common = 2000.0
    - SL = H_common + buffer = 2080.0 + 10.0 = 2090.0
    - R = SL - Entry = 2090.0 - 2000.0 = 90.0
    - Target 1 (2.0R) = 2000.0 - (2.0 * 90.0) = 1820.0
    - Target 2 (3.5R) = 2000.0 - (3.5 * 90.0) = 1685.0
    - Target 3 (5.0R) = 2000.0 - (5.0 * 90.0) = 1550.0
    - Distance % = ((2000.0 - 1960.0) / 1960.0) * 100 = (40 / 1960) * 100 = 2.04%
    - Approaching Flag: 2.04% <= 2.5% -> True
    """
    cluster = SpatialOverlapCluster(
        symbol="TCS",
        direction=ZoneDirection.SUPPLY,
        overlap_min_price=2000.0,
        overlap_max_price=2080.0,
        achievements=2,
        participating_timeframes=[Timeframe.WEEKLY, Timeframe.DAILY],
        zones=[]
    )

    indicators = {
        "current_price": 1960.0,
        "atr_14": 50.0,
        "atr_buffer": 10.0,
        "ema_20": 1980.0,
        "ema_50": 2040.0,  # Nested within [1990.0, 2090.0] -> MA Confluence = True
        "sma_200": 2200.0
    }

    plan = TradeEngine.generate_trade_plan(cluster, indicators)

    assert plan.symbol == "TCS"
    assert plan.direction == ZoneDirection.SUPPLY
    assert plan.entry_price == 2000.0
    assert plan.stop_loss == 2090.0
    assert plan.risk_per_share == 90.0
    assert plan.target_1 == 1820.0
    assert plan.target_2 == 1685.0
    assert plan.target_3 == 1550.0
    assert plan.distance_pct == 2.04
    assert plan.is_approaching is True
    assert plan.has_ma_confluence is True
    assert plan.achievements == 2


def test_trade_engine_not_approaching():
    """
    Distance % > 2.5% -> is_approaching must be False.
    """
    cluster = SpatialOverlapCluster(
        symbol="INFY",
        direction=ZoneDirection.DEMAND,
        overlap_min_price=1500.0,
        overlap_max_price=1520.0,
        achievements=2,
        participating_timeframes=[Timeframe.MONTHLY, Timeframe.DAILY],
        zones=[]
    )

    # Current Price is 1600.0 -> Distance = ((1600-1520)/1600)*100 = 5.0%
    indicators = {
        "current_price": 1600.0,
        "atr_14": 20.0,
        "atr_buffer": 4.0
    }

    plan = TradeEngine.generate_trade_plan(cluster, indicators)
    assert plan.distance_pct == 5.0
    assert plan.is_approaching is False
