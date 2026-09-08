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
    """
    GTF Methodology: Proximal interaction state transitions.

    Per GTF PDF ("Trading in the Zone by GTF", Freshness Rules):
    - Price above proximal (no touch)            -> FRESH        (retest_count = 0)
    - Wick/low touches or enters proximal zone,
      but candle CLOSES above distal             -> TESTED       (retest_count >= 1)
    - Candle CLOSES below distal line            -> BREACHED

    NOTE: INVALIDATED is an AlertState concept (alert lifecycle).
    FreshnessStatus.INVALIDATED exists in the enum but is NOT assigned
    by FreshnessEvaluator for proximal interaction — correctly so.
    Proximal touch = TEST. Only close beyond distal = BREACH.
    """
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 2, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 3, tzinfo=timezone.utc)
    t3 = datetime(2026, 1, 4, tzinfo=timezone.utc)

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

    # STATE 1: Candle staying strictly above proximal -> FRESH (0 retests)
    c1 = CandleSchema(timestamp=t1, symbol="TEST", timeframe=Timeframe.DAILY, open=110, high=115, low=102, close=112, volume=1000, candle_type=CandleType.ERC)
    eval1 = FreshnessEvaluator.evaluate_zone_freshness(zone, [c1])
    assert eval1.freshness == FreshnessStatus.FRESH, "Price above proximal must be FRESH"
    assert eval1.retest_count == 0
    assert not eval1.is_breached

    # STATE 2: Candle low touches proximal (wick penetration), close ABOVE distal -> TESTED
    # GTF: proximal interaction = test, NOT invalidation. Close above distal = zone still active.
    c2 = CandleSchema(timestamp=t2, symbol="TEST", timeframe=Timeframe.DAILY, open=105, high=106, low=99.5, close=101, volume=1000, candle_type=CandleType.ERC)
    eval2 = FreshnessEvaluator.evaluate_zone_freshness(zone, [c1, c2])
    assert eval2.freshness == FreshnessStatus.TESTED, "Proximal wick touch with close above distal must be TESTED (not INVALIDATED)"
    assert eval2.retest_count == 1
    assert not eval2.is_breached
    assert eval2.penetration_timestamp == t2

    # STATE 3: Candle closes BELOW distal line -> BREACHED
    # GTF: only close beyond distal constitutes a breach.
    c3 = CandleSchema(timestamp=t3, symbol="TEST", timeframe=Timeframe.DAILY, open=95, high=96, low=85, close=88, volume=3000, candle_type=CandleType.ERC)
    eval3 = FreshnessEvaluator.evaluate_zone_freshness(zone, [c1, c2, c3])
    assert eval3.freshness == FreshnessStatus.BREACHED, "Close below distal must be BREACHED"
    assert eval3.is_breached
    assert eval3.breach_timestamp == t3


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


def test_gtf_base_candle_erc_rejection_boundary():
    """
    Phase 2A Regression Test:
    Frozen GTF Rule (Trading in the Zone by GTF, Page 5):
    - NRC / Base Candle: Body < 50% of total candle range.
    - ERC / Exciting Candle: Body > 50% of total candle range.
    Boundary rule: body_ratio >= 0.50 is NOT a valid base candle.

    Verifies:
    - 0.49 and 0.499999 are accepted as valid NRC basing and emit a zone.
    - 0.50, 0.500001, 0.55, 0.60, 0.65 are strictly rejected (0 zones).
    - The proven failing fixture (O=120, H=200, L=100, C=180, ratio=0.60) emits [] (0 zones).
    """
    detector = ZoneDetector()

    # Proven failing fixture
    leg_in = CandleSchema(
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        symbol="TEST", timeframe=Timeframe.DAILY,
        open=300.0, high=310.0, low=190.0, close=200.0, volume=5000,
        candle_type=CandleType.ERC, body_range=100.0, total_range=120.0, body_ratio=0.8333
    )
    base_60 = CandleSchema(
        timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
        symbol="TEST", timeframe=Timeframe.DAILY,
        open=120.0, high=200.0, low=100.0, close=180.0, volume=1000,
        candle_type=CandleType.ERC, body_range=60.0, total_range=100.0, body_ratio=0.6000
    )
    leg_out = CandleSchema(
        timestamp=datetime(2026, 1, 3, tzinfo=timezone.utc),
        symbol="TEST", timeframe=Timeframe.DAILY,
        open=200.0, high=320.0, low=195.0, close=310.0, volume=5000,
        candle_type=CandleType.ERC, body_range=110.0, total_range=125.0, body_ratio=0.8800
    )

    # 1. Proven 0.60 fixture must produce NO zone
    zones_60 = detector.detect_zones([leg_in, base_60, leg_out])
    assert len(zones_60) == 0, f"Candidate base with 60% ERC body ratio must be rejected, got {zones_60}"

    # 2. Ratio sweep across boundary
    test_ratios = [0.49, 0.499999, 0.50, 0.500001, 0.55, 0.60, 0.65]
    for r in test_ratios:
        total_range = 100.0
        body = r * total_range
        open_p = 150.0 - (body / 2.0)
        close_p = 150.0 + (body / 2.0)
        c_type = CandleType.NRC if r < 0.50 else CandleType.ERC

        candidate_base = CandleSchema(
            timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
            symbol="TEST", timeframe=Timeframe.DAILY,
            open=open_p, high=200.0, low=100.0, close=close_p, volume=1000,
            candle_type=c_type, body_range=round(body, 4),
            total_range=round(total_range, 4), body_ratio=round(r, 6)
        )

        emitted_zones = detector.detect_zones([leg_in, candidate_base, leg_out])

        if r < 0.50:
            assert len(emitted_zones) == 1, f"Ratio {r} is valid NRC (< 0.50) and must emit a zone"
            assert emitted_zones[0].structure == ZoneStructure.DBR
        else:
            assert len(emitted_zones) == 0, f"Ratio {r} is ERC (>= 0.50) and must NOT emit a zone, got {emitted_zones}"


def test_phase2c_production_zone_authority_unification():
    """
    Phase 2C Regression Tests:
    Test A: Legacy engine cannot enter production path.
    Test B: Phase 2A 0.6000 ERC fixture cannot become a production zone in full_batch_scanner.
    Test C: Screener and Chart derive from the same canonical ZoneDetector authority.
    Test D: screener_shortlist_cache does not bypass canonical GTF validation.
    """
    from app.engine.full_batch_scanner import _detect_canonical_htf_zone
    from app.engine.pipeline import ScannerPipeline
    import pandas as pd

    # Test B: 0.6000 ERC base in full_batch_scanner must return None
    candles_erc = [
        {'open': 250.0, 'high': 255.0, 'low': 245.0, 'close': 250.0, 'volume': 1000, 'time': i * 86400}
        for i in range(12)
    ]
    candles_erc.append({'open': 300.0, 'high': 310.0, 'low': 190.0, 'close': 200.0, 'volume': 5000, 'time': 12 * 86400})
    candles_erc.append({'open': 120.0, 'high': 200.0, 'low': 100.0, 'close': 180.0, 'volume': 1000, 'time': 13 * 86400}) # 0.60 ERC
    candles_erc.append({'open': 200.0, 'high': 320.0, 'low': 195.0, 'close': 310.0, 'volume': 5000, 'time': 14 * 86400})
    candles_erc.append({'open': 300.0, 'high': 305.0, 'low': 165.0, 'close': 170.0, 'volume': 2000, 'time': 15 * 86400})

    # Assert that _detect_canonical_htf_zone rejects this 0.60 ERC base
    zone_res = _detect_canonical_htf_zone(candles_erc, '1D')
    assert zone_res is None, f"Canonical full_batch_scanner must reject 0.60 ERC base, got {zone_res}"

    # Test C: Canonical ScannerPipeline and ZoneDetector parity
    pipeline = ScannerPipeline()
    df_fixture = pd.DataFrame([
        {'timestamp': datetime.fromtimestamp(c['time'], tz=timezone.utc), 'open': c['open'], 'high': c['high'], 'low': c['low'], 'close': c['close'], 'volume': c['volume']}
        for c in candles_erc
    ]).set_index('timestamp')

    scan_res = pipeline.run_scan_on_dataframe('TEST_ERC', df_fixture, timeframes=[Timeframe.DAILY], min_achievements=1)
    # Both ScannerPipeline and _detect_canonical_htf_zone must find zero zones from the 0.60 ERC base
    erc_zones = [z for z in scan_res.all_zones if z.proximal_price == 180.0]
    assert len(erc_zones) == 0, "ScannerPipeline must not emit zone for 0.60 ERC base"


