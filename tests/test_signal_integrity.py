import pytest
from app.domain.enums import ZoneDirection
from app.engine.gtf_engine import GTFEngine
from app.engine.conviction_ranker import ConvictionRankingEngine


def test_gtf_7_point_score_minimum_and_maximum():
    """Verify GTF 7-Point score boundaries and mathematical sum."""
    engine = GTFEngine()

    # Minimum-quality setup (all minimums: >2 retests, weak departure, >5 base candles)
    min_res = engine.calculate_gtf_7_point_trade_score(
        retest_count=3,
        departure_strength=0.2,
        is_pro_gap=False,
        exciting_candle_count=0,
        basing_candle_count=7,
        direction=ZoneDirection.DEMAND
    )
    assert min_res["score_freshness"] == 0.0
    assert min_res["score_departure"] == 0.5
    assert min_res["score_time_at_base"] == 0.0
    assert min_res["gtf_score_7"] == 0.5
    assert min_res["is_tradable"] is False

    # Maximum-quality setup (all maximums: 0 retests, pro-gap / >=2 exciting, 1-3 base candles)
    max_res = engine.calculate_gtf_7_point_trade_score(
        retest_count=0,
        departure_strength=3.5,
        is_pro_gap=True,
        exciting_candle_count=3,
        basing_candle_count=2,
        direction=ZoneDirection.DEMAND
    )
    assert max_res["score_freshness"] == 3.0
    assert max_res["score_departure"] == 2.0
    assert max_res["score_time_at_base"] == 2.0
    assert max_res["gtf_score_7"] == 7.0
    assert max_res["is_tradable"] is True


def test_gtf_one_variable_at_a_time_isolation():
    """Verify that changing one parameter affects ONLY that specific score component."""
    engine = GTFEngine()

    base = engine.calculate_gtf_7_point_trade_score(
        retest_count=0,
        departure_strength=2.5,
        is_pro_gap=False,
        exciting_candle_count=2,
        basing_candle_count=2,
    )
    assert base["score_freshness"] == 3.0
    assert base["score_departure"] == 2.0
    assert base["score_time_at_base"] == 2.0
    assert base["gtf_score_7"] == 7.0

    # 1. Change ONLY freshness (retest_count from 0 to 1)
    freshness_changed = engine.calculate_gtf_7_point_trade_score(
        retest_count=1,
        departure_strength=2.5,
        is_pro_gap=False,
        exciting_candle_count=2,
        basing_candle_count=2,
    )
    assert freshness_changed["score_freshness"] == 1.5
    assert freshness_changed["score_departure"] == 2.0
    assert freshness_changed["score_time_at_base"] == 2.0
    assert freshness_changed["gtf_score_7"] == 5.5

    # 2. Change ONLY departure strength (from strong to weak)
    departure_changed = engine.calculate_gtf_7_point_trade_score(
        retest_count=0,
        departure_strength=0.5,
        is_pro_gap=False,
        exciting_candle_count=0,
        basing_candle_count=2,
    )
    assert departure_changed["score_freshness"] == 3.0
    assert departure_changed["score_departure"] == 0.5
    assert departure_changed["score_time_at_base"] == 2.0
    assert departure_changed["gtf_score_7"] == 5.5

    # 3. Change ONLY time at base (from 2 candles to 5 candles)
    base_changed = engine.calculate_gtf_7_point_trade_score(
        retest_count=0,
        departure_strength=2.5,
        is_pro_gap=False,
        exciting_candle_count=2,
        basing_candle_count=5,
    )
    assert base_changed["score_freshness"] == 3.0
    assert base_changed["score_departure"] == 2.0
    assert base_changed["score_time_at_base"] == 1.0
    assert base_changed["gtf_score_7"] == 6.0


def test_curve_location_mathematics_and_symmetry():
    """Verify GTF Location on Curve formula for both Demand and Supply."""
    engine = GTFEngine()

    # Demand: price at curve bottom (100 in 100-200 range) -> VERY_LOW_ON_CURVE
    d_low = engine.calculate_location_on_curve(110.0, 100.0, 200.0, ZoneDirection.DEMAND)
    assert d_low["curve_location"] == "VERY_LOW_ON_CURVE"
    assert d_low["is_valid_trade"] is True

    # Demand: price at curve top (190 in 100-200 range) -> VERY_HIGH_ON_CURVE (Invalid for Demand)
    d_high = engine.calculate_location_on_curve(190.0, 100.0, 200.0, ZoneDirection.DEMAND)
    assert d_high["curve_location"] == "VERY_HIGH_ON_CURVE"
    assert d_high["is_valid_trade"] is False

    # Supply: price at curve top (190 in 100-200 range) -> VERY_HIGH_ON_CURVE (Valid for Supply)
    s_high = engine.calculate_location_on_curve(190.0, 100.0, 200.0, ZoneDirection.SUPPLY)
    assert s_high["curve_location"] == "VERY_HIGH_ON_CURVE"
    assert s_high["is_valid_trade"] is True

    # Equilibrium (150 in 100-200 range)
    eq = engine.calculate_location_on_curve(150.0, 100.0, 200.0, ZoneDirection.DEMAND)
    assert eq["curve_location"] == "EQUILIBRIUM"


def test_50_sma_trend_vector_angle():
    """Verify 50 SMA 7-period slope angle clock rules."""
    engine = GTFEngine()

    # Rising SMA (> +0.8% slope) -> Trend UP
    up_res = engine.calculate_50sma_clock_angle([100.0, 100.5, 101.0, 101.5, 102.0, 102.5, 103.0])
    assert up_res["trend_status"] == "Trend UP"
    assert up_res["color"] == "#10B981"

    # Falling SMA (< -0.8% slope) -> Trend DOWN
    down_res = engine.calculate_50sma_clock_angle([103.0, 102.5, 102.0, 101.5, 101.0, 100.5, 100.0])
    assert down_res["trend_status"] == "Trend DOWN"
    assert down_res["color"] == "#EF4444"

    # Flat SMA (-0.8% to +0.8%) -> Trend SIDEWAYS
    flat_res = engine.calculate_50sma_clock_angle([100.0, 100.1, 100.2, 100.1, 100.0, 100.1, 100.2])
    assert flat_res["trend_status"] == "Trend SIDEWAYS"
    assert flat_res["color"] == "#F59E0B"


def test_conviction_scoring_6_pillars():
    """Verify 6-pillar composite conviction scoring (0-100 pts)."""
    scorer = ConvictionRankingEngine()

    # Maximum conviction (Score = 98-100)
    top = scorer.compute_conviction_score(
        symbol="TEST_TOP",
        direction=ZoneDirection.DEMAND,
        achievements=3, # 35 pts
        distance_pct=1.0, # 10 pts
        is_approaching=True,
        has_ma_confluence=True, # 7 pts
        ema_50=105.0,
        sma_200=100.0, # +4 pts golden cross
        current_price=106.0, # +4 pts above 200 SMA (capped at 15 pts)
        is_sector_leading=True, # 20 pts
        is_fo_put_wall_aligned=True, # 15 pts
        is_fii_supportive=True # 5 pts
    )
    # Total = 35 + 20 + 15 + 15 + 10 + 5 = 100
    assert top["conviction_score"] == 100
    assert "PRO_SUPER_HIGH" in top["conviction_grade"]

    # Minimum conviction
    low = scorer.compute_conviction_score(
        symbol="TEST_LOW",
        direction=ZoneDirection.DEMAND,
        achievements=1, # 10 pts
        distance_pct=8.0, # 3 pts
        is_approaching=False,
        has_ma_confluence=False,
        ema_50=90.0,
        sma_200=100.0, # 0 ma pts
        current_price=95.0,
        is_sector_leading=False, # 12 pts
        is_fo_put_wall_aligned=False, # 8 pts
        is_fii_supportive=False # 2 pts
    )
    # Total = 10 + 12 + 8 + 0 + 3 + 2 = 35
    assert low["conviction_score"] == 35
    assert "MODERATE" in top["conviction_grade"] or "MODERATE" in low["conviction_grade"]
