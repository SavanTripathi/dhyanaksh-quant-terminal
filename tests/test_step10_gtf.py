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

def test_gtf_13_point_odds_enhancer_scorecard():
    # High Conviction Type 1 Limit Entry (>= 11.5)
    odds_t1 = gtf_engine.score_gtf_13_point_odds(
        departure_strength=3.5,  # 2.0
        basing_candle_count=2,   # 2.0
        is_fresh=True,           # 3.0
        achievements=3,          # 3.0
        curve_location="VERY_LOW_ON_CURVE", # 3.0
        direction=ZoneDirection.DEMAND
    )
    assert odds_t1["gtf_odds_score"] == 13.0
    assert "TYPE_1_LIMIT_ENTRY" in odds_t1["gtf_entry_type"]

    # Confirmation Entry (9.0 to 11.0)
    odds_t2 = gtf_engine.score_gtf_13_point_odds(
        departure_strength=1.5,  # 1.5
        basing_candle_count=4,   # 1.0
        is_fresh=True,           # 3.0
        achievements=2,          # 2.0
        curve_location="EQUILIBRIUM", # 1.5
        direction=ZoneDirection.DEMAND
    )
    assert 9.0 <= odds_t2["gtf_odds_score"] <= 11.0
    assert "TYPE_2_CONFIRMATION_ENTRY" in odds_t2["gtf_entry_type"]

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
