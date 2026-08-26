import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.engine.sector_rotation import sector_rotation_engine
from app.engine.institutional_flows import institutional_flows_engine
from app.engine.derivatives_intelligence import derivatives_intelligence_engine
from app.engine.institutional_scorer import institutional_scorer

def test_sector_rotation_mrs_and_quadrants():
    res = sector_rotation_engine.calculate_sector_rotation()
    assert res.total_sectors >= 8
    assert res.benchmark_symbol == "NIFTY50"
    
    # Check that quadrants are valid
    valid_quadrants = {
        "OUTPERFORMING_STRENGTHENING",
        "OUTPERFORMING_WEAKENING",
        "UNDERPERFORMING_IMPROVING",
        "UNDERPERFORMING_DETERIORATING"
    }
    for s in res.sectors:
        assert s.quadrant in valid_quadrants
        assert s.rank >= 1


def test_institutional_flows_regime_and_ls_ratio():
    res = institutional_flows_engine.get_market_regime()
    assert res.long_short_ratio > 0
    assert res.regime in [
        "HEAVILY_OVERSOLD",
        "BEARISH_DOMINANCE",
        "NEUTRAL_RANGEBOUND",
        "OVERBOUGHT_EXTENDED"
    ]
    assert res.fii_net_cash_cr != 0


def test_derivatives_fo_intelligence():
    res = derivatives_intelligence_engine.get_fo_intelligence("RELIANCE")
    assert res.symbol == "RELIANCE"
    assert res.spot_price > 0
    assert res.max_pain_strike > 0
    assert res.call_resistance_wall > 0
    assert res.put_support_floor > 0
    assert len(res.strikes) >= 10


def test_composite_institutional_scorer():
    score_res = institutional_scorer.score_setup(
        achievements=3,
        is_sector_leading_or_emerging=True,
        is_fii_supportive=True,
        is_fo_wall_aligned=True,
        has_ma_confluence=True
    )
    assert score_res.total_score == 100
    assert "INSTITUTIONAL_A_PLUS" in score_res.conviction_grade


@pytest.mark.asyncio
async def test_step7_context_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Market regime
        reg_res = await ac.get("/api/v1/context/market-regime")
        assert reg_res.status_code == 200
        assert "long_short_ratio" in reg_res.json()

        # 2. Sector rotation
        sec_res = await ac.get("/api/v1/context/sectors")
        assert sec_res.status_code == 200
        assert "sectors" in sec_res.json()

        # 3. F&O Intelligence
        fo_res = await ac.get("/api/v1/context/fo/RELIANCE")
        assert fo_res.status_code == 200
        assert "max_pain_strike" in fo_res.json()
