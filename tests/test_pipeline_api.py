"""
Integration test for full Scanner Pipeline & API endpoints.
"""
from datetime import datetime, timedelta
import pytest
from httpx import AsyncClient, ASGITransport
import pandas as pd
import numpy as np

from app.main import app
from app.domain.enums import Timeframe
from app.engine.pipeline import ScannerPipeline
from app.engine.data_feed import generate_mock_nifty_data


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "achievements_threshold" in data


@pytest.mark.asyncio
async def test_scan_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "symbol": "RELIANCE",
            "lookback_days": 120,
            "min_achievements": 2
        }
        response = await ac.post("/api/v1/scan", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "RELIANCE"
        assert "clusters" in data
        for cluster in data["clusters"]:
            assert cluster["achievements"] >= 2
            assert len(cluster["participating_timeframes"]) >= 2
            assert cluster["is_fresh"] is True
