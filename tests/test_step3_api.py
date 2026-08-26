"""
Integration tests for Step 3 Alert Endpoints (/alerts/test, /alerts/history, /alerts/dispatch-batch).
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.domain.enums import AlertChannel, AlertType


@pytest.mark.asyncio
async def test_alert_test_endpoint_telegram():
    """
    Test POST /api/v1/alerts/test with Telegram channel.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "channel": "TELEGRAM",
            "symbol": "RELIANCE",
            "alert_type": "SYSTEM_TEST"
        }
        response = await ac.post("/api/v1/alerts/test", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["channel"] == "TELEGRAM"
        assert "RELIANCE" in data["rendered_message"]


@pytest.mark.asyncio
async def test_alert_test_endpoint_webhook():
    """
    Test POST /api/v1/alerts/test with Webhook channel.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "channel": "WEBHOOK",
            "symbol": "TCS",
            "alert_type": "SYSTEM_TEST"
        }
        response = await ac.post("/api/v1/alerts/test", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["channel"] == "WEBHOOK"


@pytest.mark.asyncio
async def test_alert_history_endpoint():
    """
    Test GET /api/v1/alerts/history.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/alerts/history?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "total_alerts" in data
        assert "alerts" in data


@pytest.mark.asyncio
async def test_dispatch_batch_alerts_endpoint():
    """
    Test POST /api/v1/alerts/dispatch-batch.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First ensure batch scan exists
        await ac.post("/api/v1/batch/run?lookback_days=60&min_achievements=2&symbols=RELIANCE&symbols=TCS")

        # Trigger alert evaluation
        response = await ac.post("/api/v1/alerts/dispatch-batch")
        assert response.status_code == 200
        data = response.json()
        assert "evaluated_plans_count" in data
        assert "dispatched_alerts_count" in data
