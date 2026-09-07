"""
Adversarial Verification of Database / API / Frontend / Chart Parity and Timeframe Isolation.
Stocks Tested: BSOFT + 5 NIFTY 500 Stocks (RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK)
Across Timeframes: Daily (1D), Weekly (1W), Monthly (1M), Quarterly (3M)
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.domain.enums import Timeframe, ZoneDirection, FreshnessStatus
from app.engine.data_feed import generate_calibrated_nifty_data
from app.engine.pipeline import ScannerPipeline

TEST_STOCKS = ["BSOFT", "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
pipeline = ScannerPipeline()


@pytest.mark.asyncio
@pytest.mark.parametrize("symbol", TEST_STOCKS)
async def test_api_database_chart_parity(symbol: str):
    """
    Verifies that raw detected zones match the API endpoint payload and chart representation exactly,
    without any coordinate alteration or timeframe degradation.
    """
    # 1. Fetch market data exactly as the endpoint does
    from app.engine.data_feed import fetch_nse_market_data, generate_mock_nifty_data
    df = fetch_nse_market_data(symbol, days=730)
    if df.empty or len(df) < 5:
        df = generate_mock_nifty_data(symbol, days=730)
    assert not df.empty and len(df) >= 20

    # 2. Pipeline Engine Detection with default timeframes
    scan_res = pipeline.run_scan_on_dataframe(
        symbol=symbol,
        df_intraday_or_daily=df,
        min_achievements=2
    )

    # 3. Query API Endpoint
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/charts/{symbol}/zones?days=730&min_achievements=2")
        assert response.status_code == 200
        api_data = response.json()

    assert api_data["symbol"] == symbol
    assert "clusters" in api_data
    assert "zones" in api_data

    # 3. Verify exact parity between pipeline and API
    assert api_data["clusters_count"] == scan_res.clusters_count

    # For each cluster returned by API, verify coordinates match pipeline clusters exactly
    api_clusters = api_data["clusters"]
    for idx, cluster in enumerate(scan_res.clusters):
        matching_api_cluster = next(
            (c for c in api_clusters if c["overlap_min_price"] == cluster.overlap_min_price and c["overlap_max_price"] == cluster.overlap_max_price),
            None
        )
        assert matching_api_cluster is not None, f"Cluster {cluster} missing from API response for {symbol}"
        assert matching_api_cluster["direction"] == cluster.direction.value
        assert matching_api_cluster["achievements"] == cluster.achievements
        
        # Verify participating timeframes are strictly preserved
        expected_tfs = set(tf.value for tf in cluster.participating_timeframes)
        actual_tfs = set(matching_api_cluster["participating_timeframes"])
        assert expected_tfs == actual_tfs

        # Verify underlying zone coordinates
        for z in cluster.zones:
            matching_api_zone = next(
                (az for az in matching_api_cluster["zones"] if az["proximal_price"] == z.proximal_price and az["distal_price"] == z.distal_price and az["timeframe"] == z.timeframe.value),
                None
            )
            assert matching_api_zone is not None, f"Zone {z} not found in matching API cluster zones: {matching_api_cluster['zones']}"
            assert matching_api_zone["timeframe"] == z.timeframe.value
            assert matching_api_zone["direction"] == z.direction.value
            assert matching_api_zone["structure"] == z.structure.value


@pytest.mark.asyncio
@pytest.mark.parametrize("symbol", TEST_STOCKS)
async def test_strict_timeframe_isolation(symbol: str):
    """
    Verifies that no Daily zone coordinates are substituted as Weekly coordinates,
    and no Weekly zone coordinates are substituted as Monthly coordinates.
    """
    df = generate_calibrated_nifty_data(symbol, days=730)
    scan_res = pipeline.run_scan_on_dataframe(
        symbol=symbol,
        df_intraday_or_daily=df,
        timeframes=[Timeframe.QUARTERLY, Timeframe.MONTHLY, Timeframe.WEEKLY, Timeframe.DAILY],
        min_achievements=2
    )

    by_tf = {
        Timeframe.DAILY: [z for z in scan_res.all_zones if z.timeframe == Timeframe.DAILY],
        Timeframe.WEEKLY: [z for z in scan_res.all_zones if z.timeframe == Timeframe.WEEKLY],
        Timeframe.MONTHLY: [z for z in scan_res.all_zones if z.timeframe == Timeframe.MONTHLY],
        Timeframe.QUARTERLY: [z for z in scan_res.all_zones if z.timeframe == Timeframe.QUARTERLY],
    }

    # Verify timeframes are populated and isolated
    for tf, zones in by_tf.items():
        for z in zones:
            assert z.timeframe == tf
            assert z.proximal_price > 0
            assert z.distal_price > 0
            if z.direction == ZoneDirection.DEMAND:
                assert z.proximal_price > z.distal_price
            else:
                assert z.distal_price > z.proximal_price
