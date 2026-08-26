import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.engine.conviction_ranker import conviction_ranking_engine
from app.domain.enums import ZoneDirection

def test_conviction_scoring_calculation():
    # Triple Confluence + Leading + Put Wall + Golden Cross + Approaching
    res_high = conviction_ranking_engine.compute_conviction_score(
        symbol="RELIANCE",
        direction=ZoneDirection.DEMAND,
        achievements=3,
        distance_pct=1.5,
        is_approaching=True,
        has_ma_confluence=True,
        ema_50=1320.0,
        sma_200=1280.0,
        current_price=1300.0,
        is_sector_leading=True,
        is_fo_put_wall_aligned=True,
        is_fii_supportive=True
    )

    assert res_high["conviction_score"] >= 85
    assert "PRO_SUPER_HIGH" in res_high["conviction_grade"]
    assert res_high["conviction_breakdown"]["p1_zone_quality"] == 35
    assert res_high["conviction_breakdown"]["p2_sector_momentum"] == 20
    assert res_high["conviction_breakdown"]["p5_proximity"] == 10

    # Dual Confluence + Moderate Proximity
    res_med = conviction_ranking_engine.compute_conviction_score(
        symbol="INFY",
        direction=ZoneDirection.SUPPLY,
        achievements=2,
        distance_pct=4.0,
        is_approaching=False,
        has_ma_confluence=False,
        is_sector_leading=False,
        is_fo_put_wall_aligned=False,
        is_fii_supportive=False
    )
    assert res_med["conviction_score"] < 85
    assert res_med["conviction_breakdown"]["p1_zone_quality"] == 25


@pytest.mark.asyncio
async def test_top_picks_and_analysis_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Top Picks limit=3
        res3 = await ac.get("/api/v1/screener/top-picks?limit=3&min_score=70")
        assert res3.status_code == 200
        data3 = res3.json()
        assert len(data3["plans"]) <= 3
        if data3["plans"]:
            assert data3["plans"][0]["conviction_score"] >= 70

        # 2. Top Picks limit=5
        res5 = await ac.get("/api/v1/screener/top-picks?limit=5&min_score=70")
        assert res5.status_code == 200
        data5 = res5.json()
        assert len(data5["plans"]) <= 5

        # 3. Stock Analysis
        res_analysis = await ac.get("/api/v1/screener/analysis/RELIANCE")
        assert res_analysis.status_code == 200
        analysis_data = res_analysis.json()
        assert analysis_data["symbol"] == "RELIANCE"
        assert "breakdown" in analysis_data
        assert "hit_rate_probability" in analysis_data
