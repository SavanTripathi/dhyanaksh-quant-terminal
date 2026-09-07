import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.engine.gtf_engine import gtf_engine
from app.domain.enums import ZoneDirection

def test_gtf_basing_candle_count_validation():
    # 1 to 6 basing candles are strictly valid
    assert gtf_engine.validate_basing_candle_count(1) is True
    assert gtf_engine.validate_basing_candle_count(3) is True
    assert gtf_engine.validate_basing_candle_count(6) is True
    
    # 0 or >= 7 candles are invalid / retail consolidation
    assert gtf_engine.validate_basing_candle_count(0) is False
    assert gtf_engine.validate_basing_candle_count(7) is False
    assert gtf_engine.validate_basing_candle_count(12) is False

def test_gtf_location_on_curve_calculation():
    # Very Low on Curve (Demand Area)
    res_low = gtf_engine.calculate_location_on_curve(
        current_price=1020.0,
        htf_demand_proximal=1000.0,
        htf_supply_proximal=1200.0,
        direction=ZoneDirection.DEMAND
    )
    assert res_low["curve_location"] == "VERY_LOW_ON_CURVE"
    assert res_low["curve_percent"] == 10.0
    assert res_low["is_valid_trade"] is True

    # Very High on Curve (Supply Area)
    res_high = gtf_engine.calculate_location_on_curve(
        current_price=1180.0,
        htf_demand_proximal=1000.0,
        htf_supply_proximal=1200.0,
        direction=ZoneDirection.DEMAND
    )
    assert res_high["curve_location"] == "VERY_HIGH_ON_CURVE"
    assert res_high["curve_percent"] == 90.0
    assert res_high["is_valid_trade"] is False  # Buying high on curve is prohibited

def test_gtf_7_point_trade_score():
    # High Conviction Type 1 Set & Forget Limit Entry (7.0 / 7.0)
    score_t1 = gtf_engine.calculate_gtf_7_point_trade_score(
        retest_count=0,          # 3.0
        departure_strength=3.5,  # 2.0
        basing_candle_count=2,   # 2.0
        direction=ZoneDirection.DEMAND
    )
    assert score_t1["gtf_score_7"] == 7.0
    assert "Type 1" in score_t1["entry_type"]
    assert score_t1["is_tradable"] is True

    # Type 2 Confirmation Entry (5.0 - 6.5)
    score_t2 = gtf_engine.calculate_gtf_7_point_trade_score(
        retest_count=1,          # 1.5
        departure_strength=2.5,  # 2.0
        basing_candle_count=2,   # 2.0
        direction=ZoneDirection.DEMAND
    )
    assert score_t2["gtf_score_7"] == 5.5
    assert "Type 2" in score_t2["entry_type"]
    assert score_t2["is_tradable"] is True

    # Disqualified Setup (< 5.0)
    score_disq = gtf_engine.calculate_gtf_7_point_trade_score(
        retest_count=2,          # 0.0
        departure_strength=0.5,
        exciting_candle_count=0, # 0.5
        basing_candle_count=5,   # 1.0
        direction=ZoneDirection.DEMAND
    )
    assert score_disq["gtf_score_7"] == 1.5
    assert score_disq["is_tradable"] is False

@pytest.mark.asyncio
async def test_gtf_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. GTF Odds Enhancers
        res_odds = await ac.get("/api/v1/gtf/odds-enhancers/RELIANCE")
        assert res_odds.status_code == 200
        data_odds = res_odds.json()
        assert "gtf_odds_score" in data_odds
        assert "gtf_entry_type" in data_odds
        assert "breakdown" in data_odds

        # 2. GTF Curve Analysis
        res_curve = await ac.get("/api/v1/gtf/curve-analysis/RELIANCE")
        assert res_curve.status_code == 200
        data_curve = res_curve.json()
        assert "curve_analysis" in data_curve
        assert "curve_location" in data_curve["curve_analysis"]
