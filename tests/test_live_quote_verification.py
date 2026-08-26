"""
Automated Live Price & Quote Verification Tests.
Verifies get_verified_nse_quote and /api/v1/charts/{symbol}/quote endpoints
adhere strictly to official live market quotes within ±1.0% variance.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.engine.data_feed import get_verified_nse_quote

BENCHMARK_TARGETS = [
    ("WIPRO", 178.00, 180.50),
    ("PNB", 115.80, 117.00),
    ("CHOLAFIN", 1880.00, 1895.00),
    ("GAIL", 173.50, 175.50),
    ("RELIANCE", 1305.00, 1318.00),
]


@pytest.mark.parametrize("symbol,min_price,max_price", BENCHMARK_TARGETS)
def test_direct_verified_quote_benchmark(symbol: str, min_price: float, max_price: float):
    """
    Test direct ingestion via get_verified_nse_quote returns CMP within ±1.0% of benchmark baseline.
    """
    quote = get_verified_nse_quote(symbol)
    assert quote["symbol"] == symbol
    assert quote["cmp"] > 0.0
    assert quote["prev_close"] > 0.0

    mid_ref = (min_price + max_price) / 2.0
    variance_pct = abs(quote["cmp"] - mid_ref) / mid_ref * 100.0
    
    in_range = min_price <= quote["cmp"] <= max_price
    in_tolerance = variance_pct <= 1.0
    
    assert in_range or in_tolerance, f"{symbol} CMP {quote['cmp']} out of range [{min_price}, {max_price}] and variance {variance_pct:.2f}% > 1.0%"


@pytest.mark.asyncio
@pytest.mark.parametrize("symbol,min_price,max_price", BENCHMARK_TARGETS)
async def test_quote_endpoint_benchmark(symbol: str, min_price: float, max_price: float):
    """
    Test REST endpoint /api/v1/charts/{symbol}/quote returns accurate CMP within ±1.0% variance.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/charts/{symbol}/quote")
        assert res.status_code == 200
        data = res.json()
        
        assert data["symbol"] == symbol
        assert data["cmp"] > 0.0
        assert "prev_close" in data or "previous_close" in data
        assert "change" in data
        assert "change_pct" in data
        
        mid_ref = (min_price + max_price) / 2.0
        variance_pct = abs(data["cmp"] - mid_ref) / mid_ref * 100.0
        
        in_range = min_price <= data["cmp"] <= max_price
        in_tolerance = variance_pct <= 1.0
        
        assert in_range or in_tolerance, f"{symbol} Endpoint CMP {data['cmp']} out of range [{min_price}, {max_price}] and variance {variance_pct:.2f}% > 1.0%"
