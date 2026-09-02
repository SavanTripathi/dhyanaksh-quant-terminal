import pytest
from datetime import datetime, timezone
import pandas as pd
from app.domain.enums import Timeframe, ZoneDirection, ZoneStructure, CandleType, FreshnessStatus
from app.domain.schemas import CandleSchema, ZoneSchema, SpatialOverlapCluster
from app.engine.zone_detector import ZoneDetector, detect_htf_supply_demand_zone
from app.engine.aggregator import CandleAggregator
from app.engine.freshness import FreshnessEvaluator
from app.engine.trade_engine import TradeEngine
from app.engine.gtf_engine import GTFEngine


def test_zone_data_ohlc_aggregation_integrity():
    """Verify OHLC aggregation mathematical rules: Open=first, High=max, Low=min, Close=last."""
    data = [
        {"timestamp": "2026-01-01 09:15:00", "open": 100, "high": 105, "low": 98, "close": 102, "volume": 1000},
        {"timestamp": "2026-01-01 10:15:00", "open": 102, "high": 110, "low": 101, "close": 108, "volume": 1500},
        {"timestamp": "2026-01-01 11:15:00", "open": 108, "high": 109, "low": 95, "close": 96, "volume": 2000},
    ]
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")

    candles = CandleAggregator.aggregate_from_df(df, Timeframe.DAILY, "TEST_SYM")
    assert len(candles) == 1
    c = candles[0]
    assert c.open == 100.0  # first open
    assert c.high == 110.0  # max high
    assert c.low == 95.0    # min low
    assert c.close == 96.0  # last close
    assert c.volume == 4500.0  # sum volume


def test_demand_zone_geometry_and_boundaries():
    """Verify Demand Proximal > Distal and exact boundaries."""
    detector = ZoneDetector(max_base_candles=3)
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 2, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 3, tzinfo=timezone.utc)

    # Leg-in (Drop), Base (Narrow), Leg-out (Rally)
    leg_in = CandleSchema(timestamp=t0, symbol="TEST", timeframe=Timeframe.DAILY, open=110, high=111, low=95, close=96, volume=1000, candle_type=CandleType.ERC, body_ratio=0.8)
    basing = [CandleSchema(timestamp=t1, symbol="TEST", timeframe=Timeframe.DAILY, open=96, high=98, low=93, close=97, volume=500, candle_type=CandleType.NRC, body_ratio=0.2)]
    leg_out = CandleSchema(timestamp=t2, symbol="TEST", timeframe=Timeframe.DAILY, open=97, high=115, low=96, close=114, volume=2000, candle_type=CandleType.ERC, body_ratio=0.85)

    zone = detector._construct_demand_zone("TEST", Timeframe.DAILY, ZoneStructure.DBR, leg_in, basing, leg_out)
    assert zone is not None
    assert zone.direction == ZoneDirection.DEMAND
    assert zone.proximal_price == 97.0  # max of basing bodies (open 96, close 97)
    assert zone.distal_price == 93.0    # lowest low of basing
    assert zone.proximal_price > zone.distal_price


def test_supply_zone_geometry_and_boundaries():
    """Verify Supply Distal > Proximal and exact boundaries."""
    detector = ZoneDetector(max_base_candles=3)
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 2, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 3, tzinfo=timezone.utc)

    # Leg-in (Rally), Base (Narrow), Leg-out (Drop)
    leg_in = CandleSchema(timestamp=t0, symbol="TEST", timeframe=Timeframe.DAILY, open=90, high=105, low=89, close=104, volume=1000, candle_type=CandleType.ERC, body_ratio=0.8)
    basing = [CandleSchema(timestamp=t1, symbol="TEST", timeframe=Timeframe.DAILY, open=104, high=107, low=102, close=103, volume=500, candle_type=CandleType.NRC, body_ratio=0.2)]
    leg_out = CandleSchema(timestamp=t2, symbol="TEST", timeframe=Timeframe.DAILY, open=103, high=104, low=88, close=89, volume=2000, candle_type=CandleType.ERC, body_ratio=0.85)

    zone = detector._construct_supply_zone("TEST", Timeframe.DAILY, ZoneStructure.RBD, leg_in, basing, leg_out)
    assert zone is not None
    assert zone.direction == ZoneDirection.SUPPLY
    assert zone.proximal_price == 103.0  # lowest body (open 104, close 103)
    assert zone.distal_price == 107.0    # highest high
    assert zone.distal_price > zone.proximal_price


def test_freshness_evaluator_strict_transitions():
    """Verify that a zone transition to INVALIDATED occurs only when price touches/penetrates proximal."""
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 2, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 3, tzinfo=timezone.utc)

    zone = ZoneSchema(
        symbol="TEST",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR,
        proximal_price=100.0,
        distal_price=90.0,
        creation_timestamp=t0,
        base_candle_count=1,
        departure_strength=5.0
    )

    # Candle staying strictly above proximal -> FRESH
    c1 = CandleSchema(timestamp=t1, symbol="TEST", timeframe=Timeframe.DAILY, open=110, high=115, low=102, close=112, volume=1000, candle_type=CandleType.ERC)
    eval1 = FreshnessEvaluator.evaluate_zone_freshness(zone, [c1])
    assert eval1.freshness == FreshnessStatus.FRESH

    # Candle touching or penetrating proximal -> INVALIDATED
    c2 = CandleSchema(timestamp=t2, symbol="TEST", timeframe=Timeframe.DAILY, open=105, high=106, low=99.5, close=101, volume=1000, candle_type=CandleType.ERC)
    eval2 = FreshnessEvaluator.evaluate_zone_freshness(zone, [c1, c2])
    assert eval2.freshness == FreshnessStatus.INVALIDATED
    assert eval2.penetration_timestamp == t2


def test_trade_engine_mathematical_integrity():
    """Verify Entry, Stop Loss, Risk, Targets, and R:R ratios."""
    cluster = SpatialOverlapCluster(
        symbol="TEST",
        direction=ZoneDirection.DEMAND,
        participating_timeframes=[Timeframe.WEEKLY, Timeframe.DAILY],
        overlap_min_price=100.0,  # L_common
        overlap_max_price=110.0,  # H_common
        timeframe_count=2,
        achievements=2,
        departure_velocity=3.0,
        freshness_score=1.0,
        volume_imbalance_ratio=1.5,
        composite_score=85.0,
        zones=[]
    )

    daily_indicators = {
        "current_price": 112.0,
        "atr_14": 5.0,
        "atr_buffer": 1.0,  # 0.20 * 5.0
        "ema_50": 105.0,
        "sma_200": 102.0
    }

    plan = TradeEngine.generate_trade_plan(cluster, daily_indicators)
    assert plan.entry_price == 110.0  # H_common
    assert plan.stop_loss == 99.0     # L_common (100) - buffer (1.0)
    assert plan.risk_per_share == 11.0 # 110 - 99
    assert plan.target_1 == 132.0    # 110 + 2*11
    assert plan.target_2 == 148.5    # 110 + 3.5*11
    assert plan.target_3 == 165.0    # 110 + 5*11
    assert plan.is_approaching is True
    assert plan.has_ma_confluence is True
