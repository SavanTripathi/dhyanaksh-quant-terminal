import pytest
import pandas as pd
from datetime import datetime, timedelta
from app.engine.backtest_engine import BacktestEngine
from app.domain.enums import ZoneDirection

def test_backtest_engine_simulation_execution():
    engine = BacktestEngine()
    
    # Run backtest for RELIANCE
    res = engine.run_simulation(
        symbol="RELIANCE",
        lookback_days=730,
        min_achievements=2,
        account_size=500000.0,
        risk_per_trade_pct=1.0,
        run_id=999
    )
    
    assert res.run_id == 999
    assert res.symbol == "RELIANCE"
    assert res.total_trades >= 0
    assert 0.0 <= res.win_rate_t1 <= 100.0
    assert res.profit_factor >= 0.0
    assert len(res.tier_comparison) == 3


def test_backtest_tier_comparison_statistics():
    engine = BacktestEngine()
    res = engine.run_simulation(
        symbol="TCS",
        lookback_days=730,
        min_achievements=2
    )
    
    tier_names = [t.tier_name for t in res.tier_comparison]
    assert any("3-Achievement" in name for name in tier_names)
    assert any("2-Achievement" in name for name in tier_names)


from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_backtest_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "symbol": "RELIANCE",
            "lookback_days": 365,
            "min_achievements": 2,
            "account_size": 500000.0,
            "risk_per_trade_pct": 1.0
        }
        
        post_res = await ac.post("/api/v1/backtest/run", json=payload)
        assert post_res.status_code == 200
        data = post_res.json()
        assert "run_id" in data
        assert data["symbol"] == "RELIANCE"
        assert "tier_comparison" in data
        assert "equity_curve" in data
        assert "trades" in data
        
        run_id = data["run_id"]
        
        # Test GET /api/v1/backtest/results/{run_id}
        get_res = await ac.get(f"/api/v1/backtest/results/{run_id}")
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["run_id"] == run_id
        assert get_data["total_trades"] == data["total_trades"]
