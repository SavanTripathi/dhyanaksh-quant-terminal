"""
Independent GTF Golden Reference Test Suite.

Methodology Authority: docs/tradinginthezonebygtf.pdf
Architectural Principle: Strict Test Independence
Every test follows:
INDEPENDENT OHLCV FIXTURE -> INDEPENDENT EXPECTED RESULT -> PRODUCTION IMPLEMENTATION -> ASSERTION
"""
import pytest
from datetime import datetime, timedelta
from app.domain.enums import Timeframe, ZoneDirection, ZoneStructure, CandleType, FreshnessStatus
from app.domain.schemas import CandleSchema, ZoneSchema, SpatialOverlapCluster
from app.engine.zone_detector import ZoneDetector
from app.engine.gtf_engine import gtf_engine
from app.engine.freshness import FreshnessEvaluator
from app.engine.trade_engine import TradeEngine
from app.engine.aggregator import CandleAggregator

detector = ZoneDetector(max_base_candles=5)
trade_engine = TradeEngine()


def make_candle(
    idx: int,
    open_p: float,
    high: float,
    low: float,
    close: float,
    timeframe: Timeframe = Timeframe.DAILY,
    symbol: str = "GTFTEST"
) -> CandleSchema:
    """Creates an independent CandleSchema from raw OHLCV."""
    tr = high - low
    br = abs(open_p - close)
    ratio = br / tr if tr > 0 else 0.0
    ctype = CandleType.ERC if ratio > 0.50 else CandleType.NRC

    return CandleSchema(
        timestamp=datetime(2026, 1, 1) + timedelta(days=idx),
        open=open_p,
        high=high,
        low=low,
        close=close,
        volume=1000.0,
        timeframe=timeframe,
        symbol=symbol,
        candle_type=ctype,
        body_range=br,
        total_range=tr,
        body_ratio=ratio
    )


# =========================================================================
# 1. Valid RBR Demand
# =========================================================================
def test_01_valid_rbr_demand():
    candles = [
        make_candle(1, 100.0, 110.0, 99.0, 109.0),   # Leg-in: Exciting Bullish (Body 9 / Range 11 = 0.818 > 0.5)
        make_candle(2, 109.0, 111.0, 107.0, 108.0),  # Base: Boring NRC (Body 1 / Range 4 = 0.25 < 0.5)
        make_candle(3, 108.0, 120.0, 107.0, 119.0)   # Leg-out: Exciting Bullish (Body 11 / Range 13 = 0.846 > 0.5)
    ]
    zones = detector.detect_zones(candles)
    assert len(zones) == 1
    z = zones[0]
    assert z.direction == ZoneDirection.DEMAND
    assert z.structure == ZoneStructure.RBR
    assert z.proximal_price == 109.0
    assert z.distal_price == 107.0


# =========================================================================
# 2. Valid DBR Demand
# =========================================================================
def test_02_valid_dbr_demand():
    candles = [
        make_candle(1, 110.0, 111.0, 99.0, 100.0),   # Leg-in: Exciting Bearish (Body 10 / Range 12 = 0.833 > 0.5)
        make_candle(2, 100.0, 102.0, 98.0, 101.0),   # Base: Boring NRC (Body 1 / Range 4 = 0.25 < 0.5)
        make_candle(3, 101.0, 115.0, 100.0, 114.0)   # Leg-out: Exciting Bullish (Body 13 / Range 15 = 0.866 > 0.5)
    ]
    zones = detector.detect_zones(candles)
    assert len(zones) == 1
    z = zones[0]
    assert z.direction == ZoneDirection.DEMAND
    assert z.structure == ZoneStructure.DBR
    assert z.proximal_price == 101.0
    assert z.distal_price == 98.0


# =========================================================================
# 3. Valid RBD Supply
# =========================================================================
def test_03_valid_rbd_supply():
    candles = [
        make_candle(1, 100.0, 112.0, 99.0, 110.0),   # Leg-in: Exciting Bullish (Body 10 / Range 13 = 0.769 > 0.5)
        make_candle(2, 110.0, 112.0, 108.0, 111.0),  # Base: Boring NRC (Body 1 / Range 4 = 0.25 < 0.5)
        make_candle(3, 111.0, 112.0, 95.0, 96.0)     # Leg-out: Exciting Bearish (Body 15 / Range 17 = 0.882 > 0.5)
    ]
    zones = detector.detect_zones(candles)
    assert len(zones) == 1
    z = zones[0]
    assert z.direction == ZoneDirection.SUPPLY
    assert z.structure == ZoneStructure.RBD
    assert z.proximal_price == 110.0
    assert z.distal_price == 112.0


# =========================================================================
# 4. Valid DBD Supply
# =========================================================================
def test_04_valid_dbd_supply():
    candles = [
        make_candle(1, 120.0, 121.0, 109.0, 110.0),  # Leg-in: Exciting Bearish (Body 10 / Range 12 = 0.833 > 0.5)
        make_candle(2, 110.0, 113.0, 109.0, 111.0),  # Base: Boring NRC (Body 1 / Range 4 = 0.25 < 0.5)
        make_candle(3, 111.0, 112.0, 95.0, 96.0)     # Leg-out: Exciting Bearish (Body 15 / Range 17 = 0.882 > 0.5)
    ]
    zones = detector.detect_zones(candles)
    assert len(zones) == 1
    z = zones[0]
    assert z.direction == ZoneDirection.SUPPLY
    assert z.structure == ZoneStructure.DBD
    assert z.proximal_price == 110.0
    assert z.distal_price == 121.0


# =========================================================================
# 5. Invalid Demand Leg-Out
# =========================================================================
def test_05_invalid_demand_leg_out():
    candles = [
        make_candle(1, 100.0, 110.0, 99.0, 109.0),   # Leg-in: Exciting Bullish
        make_candle(2, 109.0, 111.0, 107.0, 108.0),  # Base: Boring NRC
        make_candle(3, 108.0, 113.0, 107.0, 110.0)   # Leg-out: Boring candle! (Body 2 / Range 6 = 0.333 < 0.5)
    ]
    zones = detector.detect_zones(candles)
    assert len(zones) == 0


# =========================================================================
# 6. Invalid Supply Leg-Out
# =========================================================================
def test_06_invalid_supply_leg_out():
    candles = [
        make_candle(1, 120.0, 121.0, 109.0, 110.0),  # Leg-in: Exciting Bearish
        make_candle(2, 110.0, 113.0, 109.0, 111.0),  # Base: Boring NRC
        make_candle(3, 111.0, 112.0, 108.0, 109.0)   # Leg-out: Boring candle! (Body 2 / Range 4 = 0.50, not > 0.5)
    ]
    zones = detector.detect_zones(candles)
    assert len(zones) == 0


# =========================================================================
# 7. Exactly 50% Candle
# =========================================================================
def test_07_exactly_50_percent_candle():
    c = make_candle(1, 100.0, 110.0, 100.0, 105.0)  # Body = 5, Range = 10 -> ratio = 0.50
    assert c.body_ratio == 0.50
    # GTF Engineering Interpretation: Base candle (must be strictly > 0.50 to be ERC)
    assert not detector._is_bullish_erc(c)
    assert not detector._is_bearish_erc(c)


# =========================================================================
# 8. Fresh Zone from Historical OHLCV
# =========================================================================
def test_08_fresh_zone_from_ohlcv():
    zone = ZoneSchema(
        symbol="GTFTEST",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR,
        proximal_price=101.0,
        distal_price=98.0,
        creation_timestamp=datetime(2026, 1, 3),
        base_candle_count=1
    )
    # Price stays completely above proximal 101.0
    subsequent = [
        make_candle(4, 114.0, 120.0, 112.0, 118.0),  # Low 112 > 101
        make_candle(5, 118.0, 125.0, 115.0, 122.0)   # Low 115 > 101
    ]
    evaluated = FreshnessEvaluator.evaluate_zone_freshness(zone, subsequent)
    assert evaluated.freshness == FreshnessStatus.FRESH
    assert evaluated.retest_count == 0
    assert evaluated.is_breached is False

    score = gtf_engine.calculate_gtf_7_point_trade_score(retest_count=evaluated.retest_count)
    assert score["score_freshness"] == 3.0


# =========================================================================
# 9. One-Tested Zone from Historical OHLCV
# =========================================================================
def test_09_one_tested_zone_from_ohlcv():
    zone = ZoneSchema(
        symbol="GTFTEST",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR,
        proximal_price=101.0,
        distal_price=98.0,
        creation_timestamp=datetime(2026, 1, 3),
        base_candle_count=1
    )
    subsequent = [
        make_candle(4, 114.0, 116.0, 105.0, 115.0),  # Above
        make_candle(5, 115.0, 115.0, 100.0, 106.0),  # Test 1: Low 100.0 <= 101.0, Close 106.0 > 101.0
        make_candle(6, 106.0, 112.0, 104.0, 110.0)   # Leaves zone
    ]
    evaluated = FreshnessEvaluator.evaluate_zone_freshness(zone, subsequent)
    assert evaluated.freshness == FreshnessStatus.TESTED
    assert evaluated.retest_count == 1
    assert evaluated.is_breached is False

    score = gtf_engine.calculate_gtf_7_point_trade_score(retest_count=evaluated.retest_count)
    assert score["score_freshness"] == 1.5


# =========================================================================
# 10. Twice-Tested Zone from Historical OHLCV
# =========================================================================
def test_10_twice_tested_zone_from_ohlcv():
    zone = ZoneSchema(
        symbol="GTFTEST",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR,
        proximal_price=101.0,
        distal_price=98.0,
        creation_timestamp=datetime(2026, 1, 3),
        base_candle_count=1
    )
    subsequent = [
        make_candle(4, 114.0, 116.0, 105.0, 115.0),  # Above
        make_candle(5, 115.0, 115.0, 100.0, 106.0),  # Test 1: Low 100 <= 101, Close 106 > 101
        make_candle(6, 106.0, 112.0, 104.0, 110.0),  # Exits zone (Low 104 > 101)
        make_candle(7, 110.0, 111.0, 99.5, 107.0),   # Test 2: Low 99.5 <= 101, Close 107 > 101
        make_candle(8, 107.0, 115.0, 105.0, 114.0)   # Leaves zone
    ]
    evaluated = FreshnessEvaluator.evaluate_zone_freshness(zone, subsequent)
    assert evaluated.freshness == FreshnessStatus.TESTED
    assert evaluated.retest_count == 2
    assert evaluated.is_breached is False

    score = gtf_engine.calculate_gtf_7_point_trade_score(retest_count=evaluated.retest_count)
    assert score["score_freshness"] == 0.0


# =========================================================================
# 11. Demand Proximal Penetration (Test, Not Breach)
# =========================================================================
def test_11_demand_proximal_penetration():
    zone = ZoneSchema(
        symbol="GTFTEST",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR,
        proximal_price=100.0,
        distal_price=90.0,
        creation_timestamp=datetime(2026, 1, 3),
        base_candle_count=1
    )
    # Price penetrates proximal (low 95.0 < 100.0) but does NOT breach distal (close 98.0 >= 90.0)
    subsequent = [
        make_candle(4, 105.0, 106.0, 95.0, 98.0)
    ]
    evaluated = FreshnessEvaluator.evaluate_zone_freshness(zone, subsequent)
    assert evaluated.is_breached is False
    assert evaluated.freshness == FreshnessStatus.TESTED
    assert evaluated.retest_count == 1


# =========================================================================
# 12. Demand Distal Wick Penetration (Wick beyond distal, Close within -> NOT Breached)
# =========================================================================
def test_12_demand_distal_wick_penetration():
    zone = ZoneSchema(
        symbol="GTFTEST",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR,
        proximal_price=100.0,
        distal_price=90.0,
        creation_timestamp=datetime(2026, 1, 3),
        base_candle_count=1
    )
    # Wick dips to 88.0 (< distal 90.0), BUT Close is 92.0 (>= distal 90.0)
    subsequent = [
        make_candle(4, 95.0, 96.0, 88.0, 92.0)
    ]
    evaluated = FreshnessEvaluator.evaluate_zone_freshness(zone, subsequent)
    assert evaluated.is_breached is False
    assert evaluated.freshness == FreshnessStatus.TESTED
    assert evaluated.retest_count == 1


# =========================================================================
# 13. Demand Breach (Candle Close strictly below distal -> BREACHED)
# =========================================================================
def test_13_demand_breach():
    zone = ZoneSchema(
        symbol="GTFTEST",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR,
        proximal_price=100.0,
        distal_price=90.0,
        creation_timestamp=datetime(2026, 1, 3),
        base_candle_count=1
    )
    # Candle closes at 88.0 (< distal 90.0)
    subsequent = [
        make_candle(4, 92.0, 93.0, 85.0, 88.0)
    ]
    evaluated = FreshnessEvaluator.evaluate_zone_freshness(zone, subsequent)
    assert evaluated.is_breached is True
    assert evaluated.freshness == FreshnessStatus.BREACHED
    assert evaluated.breach_timestamp == subsequent[0].timestamp


# =========================================================================
# 14. Supply Proximal Penetration (Test, Not Breach)
# =========================================================================
def test_14_supply_proximal_penetration():
    zone = ZoneSchema(
        symbol="GTFTEST",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.SUPPLY,
        structure=ZoneStructure.DBD,
        proximal_price=100.0,
        distal_price=110.0,
        creation_timestamp=datetime(2026, 1, 3),
        base_candle_count=1
    )
    # High 105.0 penetrates proximal 100.0, but close 102.0 <= distal 110.0
    subsequent = [
        make_candle(4, 95.0, 105.0, 94.0, 102.0)
    ]
    evaluated = FreshnessEvaluator.evaluate_zone_freshness(zone, subsequent)
    assert evaluated.is_breached is False
    assert evaluated.freshness == FreshnessStatus.TESTED
    assert evaluated.retest_count == 1


# =========================================================================
# 15. Supply Distal Wick Penetration (Wick beyond distal, Close within -> NOT Breached)
# =========================================================================
def test_15_supply_distal_wick_penetration():
    zone = ZoneSchema(
        symbol="GTFTEST",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.SUPPLY,
        structure=ZoneStructure.DBD,
        proximal_price=100.0,
        distal_price=110.0,
        creation_timestamp=datetime(2026, 1, 3),
        base_candle_count=1
    )
    # High spikes to 113.0 (> distal 110.0), BUT Close is 108.0 (<= distal 110.0)
    subsequent = [
        make_candle(4, 104.0, 113.0, 103.0, 108.0)
    ]
    evaluated = FreshnessEvaluator.evaluate_zone_freshness(zone, subsequent)
    assert evaluated.is_breached is False
    assert evaluated.freshness == FreshnessStatus.TESTED
    assert evaluated.retest_count == 1


# =========================================================================
# 16. Supply Breach (Candle Close strictly above distal -> BREACHED)
# =========================================================================
def test_16_supply_breach():
    zone = ZoneSchema(
        symbol="GTFTEST",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.SUPPLY,
        structure=ZoneStructure.DBD,
        proximal_price=100.0,
        distal_price=110.0,
        creation_timestamp=datetime(2026, 1, 3),
        base_candle_count=1
    )
    # Candle closes at 112.0 (> distal 110.0)
    subsequent = [
        make_candle(4, 106.0, 115.0, 105.0, 112.0)
    ]
    evaluated = FreshnessEvaluator.evaluate_zone_freshness(zone, subsequent)
    assert evaluated.is_breached is True
    assert evaluated.freshness == FreshnessStatus.BREACHED
    assert evaluated.breach_timestamp == subsequent[0].timestamp


# =========================================================================
# 17. Demand IN_ZONE Boundaries
# =========================================================================
def test_17_demand_in_zone_boundaries():
    cluster = SpatialOverlapCluster(
        symbol="GTFTEST",
        direction=ZoneDirection.DEMAND,
        overlap_min_price=90.0,  # Distal
        overlap_max_price=100.0, # Proximal
        achievements=2,
        participating_timeframes=[Timeframe.DAILY],
        zones=[]
    )
    indicators = {"atr_1d_14": 5.0, "atr_buffer": 1.0}

    # 1. Price inside zone (95.0) -> IN_ZONE
    indicators_inside = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 95.0}
    plan_inside = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators_inside)
    assert plan_inside.proximity_state == "IN_ZONE"
    assert plan_inside.distance_to_zone == 0.0
    assert plan_inside.distance_pct == 0.0

    # 2. Price at upper boundary (100.0) -> IN_ZONE
    indicators_upper = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 100.0}
    plan_upper = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators_upper)
    assert plan_upper.proximity_state == "IN_ZONE"

    # 3. Price at lower boundary (90.0) -> IN_ZONE
    indicators_lower = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 90.0}
    plan_lower = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators_lower)
    assert plan_lower.proximity_state == "IN_ZONE"

    # 4. Price above proximal (105.0) -> NOT IN_ZONE
    indicators_above = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 105.0}
    plan_above = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators_above)
    assert plan_above.proximity_state != "IN_ZONE"
    assert plan_above.distance_to_zone == 5.0

    # 5. Price below distal (85.0) -> NOT IN_ZONE (BREACHED)
    indicators_below = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 85.0}
    plan_below = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators_below)
    assert plan_below.proximity_state == "BREACHED"
    assert plan_below.status == "BREACHED"


# =========================================================================
# 18. Supply IN_ZONE Boundaries
# =========================================================================
def test_18_supply_in_zone_boundaries():
    cluster = SpatialOverlapCluster(
        symbol="GTFTEST",
        direction=ZoneDirection.SUPPLY,
        overlap_min_price=100.0, # Proximal
        overlap_max_price=110.0, # Distal
        achievements=2,
        participating_timeframes=[Timeframe.DAILY],
        zones=[]
    )
    indicators = {"atr_1d_14": 5.0, "atr_buffer": 1.0}

    # 1. Price inside zone (105.0) -> IN_ZONE
    indicators_inside = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 105.0}
    plan_inside = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators_inside)
    assert plan_inside.proximity_state == "IN_ZONE"
    assert plan_inside.distance_to_zone == 0.0

    # 2. Price at lower boundary (100.0) -> IN_ZONE
    indicators_lower = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 100.0}
    plan_lower = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators_lower)
    assert plan_lower.proximity_state == "IN_ZONE"

    # 3. Price at upper boundary (110.0) -> IN_ZONE
    indicators_upper = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 110.0}
    plan_upper = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators_upper)
    assert plan_upper.proximity_state == "IN_ZONE"

    # 4. Price below proximal (95.0) -> NOT IN_ZONE
    indicators_below = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 95.0}
    plan_below = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators_below)
    assert plan_below.proximity_state != "IN_ZONE"
    assert plan_below.distance_to_zone == 5.0

    # 5. Price above distal (115.0) -> NOT IN_ZONE (BREACHED)
    indicators_above = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 115.0}
    plan_above = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators_above)
    assert plan_above.proximity_state == "BREACHED"
    assert plan_above.status == "BREACHED"


# =========================================================================
# 19. Timeframe Isolation (Pipeline Data Path)
# =========================================================================
def test_19_timeframe_isolation():
    import pandas as pd
    aggregator = CandleAggregator()
    daily_candles = [
        make_candle(i, 100.0 + i, 105.0 + i, 98.0 + i, 104.0 + i, Timeframe.DAILY)
        for i in range(120)
    ]
    df = pd.DataFrame([c.model_dump() for c in daily_candles])
    
    # Verify aggregation preserves strict timeframe tags
    weekly = aggregator.aggregate_from_df(df, Timeframe.WEEKLY, "GTFTEST")
    monthly = aggregator.aggregate_from_df(df, Timeframe.MONTHLY, "GTFTEST")
    quarterly = aggregator.aggregate_from_df(df, Timeframe.QUARTERLY, "GTFTEST")

    assert all(c.timeframe == Timeframe.WEEKLY for c in weekly)
    assert all(c.timeframe == Timeframe.MONTHLY for c in monthly)
    assert all(c.timeframe == Timeframe.QUARTERLY for c in quarterly)

    # Prove distinct boundaries and no leakage
    assert len(weekly) < len(daily_candles)
    assert len(monthly) < len(weekly)
    assert len(quarterly) <= len(monthly)


# =========================================================================
# 20. BSOFT Multi-Timeframe Regression & Curve Isolation
# =========================================================================
def test_20_bsoft_regression():
    """
    Forensic proof that BSOFT Daily Supply does NOT equal Weekly or Monthly Demand,
    and cannot contaminate the HTF Location on the Curve.
    """
    # 1. Independent Monthly Demand Zone
    m_zone = ZoneSchema(
        symbol="BSOFT",
        timeframe=Timeframe.MONTHLY,
        direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.RBR,
        proximal_price=280.0,
        distal_price=250.0,
        creation_timestamp=datetime(2023, 5, 31),
        base_candle_count=2
    )

    # 2. Independent Weekly Demand Zone
    w_zone = ZoneSchema(
        symbol="BSOFT",
        timeframe=Timeframe.WEEKLY,
        direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR,
        proximal_price=330.0,
        distal_price=310.0,
        creation_timestamp=datetime(2024, 1, 15),
        base_candle_count=1
    )

    # 3. Independent Daily Supply Zone
    d_zone = ZoneSchema(
        symbol="BSOFT",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.SUPPLY,
        structure=ZoneStructure.DBD,
        proximal_price=450.0,
        distal_price=465.0,
        creation_timestamp=datetime(2026, 9, 4),
        base_candle_count=1
    )

    # Assert strict timeframe independence: Daily != Weekly != Monthly
    assert d_zone.timeframe != w_zone.timeframe
    assert w_zone.timeframe != m_zone.timeframe
    assert d_zone.proximal_price != w_zone.proximal_price != m_zone.proximal_price

    # Verify HTF Curve Isolation:
    # When calculating Location on Curve for Weekly Income trade,
    # the Location Timeframe MUST use Monthly boundaries [280 Demand, 600 Supply],
    # NOT the Daily Supply boundary [450.0].
    htf_curve = gtf_engine.calculate_location_on_curve(
        current_price=290.0,
        htf_demand_proximal=m_zone.proximal_price, # 280.0
        htf_supply_proximal=600.0,                  # HTF Monthly Supply
        direction=ZoneDirection.DEMAND
    )
    # (290 - 280) / (600 - 280) * 100 = 10 / 320 * 100 = 3.125% -> VERY_LOW_ON_CURVE
    assert htf_curve["curve_location"] == "VERY_LOW_ON_CURVE"
    assert htf_curve["curve_percent"] < 10.0
    assert htf_curve["is_valid_trade"] is True


# =========================================================================
# 21. Reacting State Determination (Engineering / Product State)
# =========================================================================
def test_21_reacting_state_determination():
    cluster = SpatialOverlapCluster(
        symbol="GTFTEST",
        direction=ZoneDirection.DEMAND,
        overlap_min_price=90.0,  # Distal
        overlap_max_price=100.0, # Proximal
        achievements=2,
        participating_timeframes=[Timeframe.DAILY],
        zones=[]
    )
    # Price inside zone with open at 94.0 and current price at 98.0 (Bullish reversal candle)
    indicators = {
        "atr_1d_14": 5.0,
        "atr_buffer": 1.0,
        "current_price": 98.0,
        "open_price": 94.0,
        "is_bullish_candle": True
    }
    plan = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators)
    assert plan.proximity_state == "REACTING"


# =========================================================================
# 22. Approaching Filter (Engineering / Product Filter)
# =========================================================================
def test_22_approaching_engineering_filter():
    cluster = SpatialOverlapCluster(
        symbol="GTFTEST",
        direction=ZoneDirection.DEMAND,
        overlap_min_price=90.0,
        overlap_max_price=100.0,
        achievements=2,
        participating_timeframes=[Timeframe.DAILY],
        zones=[]
    )
    indicators = {"atr_1d_14": 5.0, "atr_buffer": 1.0, "current_price": 102.0, "open_price": 102.0}
    # Current price 102.0 is 1.96% away from 100.0 (within 0.0% < distance <= 2.5%)
    plan = trade_engine.generate_trade_plan(cluster=cluster, daily_indicators=indicators)
    assert plan.is_approaching is True
    assert plan.proximity_state == "APPROACHING"
    assert plan.distance_to_zone == 2.0
    assert plan.distance_pct == 1.96
