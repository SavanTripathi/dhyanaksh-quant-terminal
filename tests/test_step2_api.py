"""
Integration tests for Step 2 Batch Scanner, Screener API, and Chart Data APIs.
"""
from datetime import datetime
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.domain.enums import Timeframe, ZoneDirection
from app.engine.universe import UniverseRepository


def test_universe_filtering():
    """
    Test NIFTY 500 equities are filtered strictly for Market Cap >= ₹5,000 Cr.
    """
    repo = UniverseRepository()
    filtered = repo.get_filtered_universe(min_mcap_cr=5000.0)
    all_stocks = repo.NIFTY_500_MOCK_UNIVERSE

    assert len(filtered) < len(all_stocks)
    for stock in filtered:
        assert stock["market_cap_cr"] >= 5000.0

    # Verify excluded smallcap is not present
    symbols = [s["symbol"] for s in filtered]
    assert "SMALLCAP_EXCLUDED" not in symbols


@pytest.mark.asyncio
async def test_batch_run_endpoint():
    """
    Test POST /api/v1/batch/run execution.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/batch/run?lookback_days=100&min_achievements=2")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"
        assert data["scanned_count"] >= 1
        assert "run_duration_seconds" in data


@pytest.mark.asyncio
async def test_screener_shortlist_endpoint():
    """
    Test GET /api/v1/screener/shortlist endpoint with filters.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/screener/shortlist?min_achievements=2")
        assert response.status_code == 200
        data = response.json()
        assert "total_plans" in data
        assert "plans" in data
        for plan in data["plans"]:
            assert plan["achievements"] >= 2
            assert plan["entry_price"] > 0
            assert plan["stop_loss"] > 0
            assert plan["risk_per_share"] > 0
            assert plan["target_1"] > 0
            assert plan["target_2"] > 0
            assert plan["target_3"] > 0
            assert "is_approaching" in plan


@pytest.mark.asyncio
async def test_chart_candles_endpoint():
    """
    Test GET /api/v1/charts/{symbol}/candles for different timeframes.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for tf in ["1D", "1W", "1M", "125M", "75M"]:
            response = await ac.get(f"/api/v1/charts/RELIANCE/candles?timeframe={tf}&days=60")
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "RELIANCE"
            assert data["timeframe"] == tf
            assert "candles" in data
            assert len(data["candles"]) > 0


@pytest.mark.asyncio
async def test_chart_zones_endpoint():
    """
    Test GET /api/v1/charts/{symbol}/zones endpoint.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/charts/RELIANCE/zones?days=120&min_achievements=2")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "RELIANCE"
        assert "clusters" in data
        for cluster in data["clusters"]:
            assert cluster["achievements"] >= 2
