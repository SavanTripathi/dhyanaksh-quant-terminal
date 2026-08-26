"""
Unit tests for Institutional Alert Formatter.
"""
from datetime import datetime
import pytest
from app.domain.enums import Timeframe, ZoneDirection, AlertType
from app.domain.schemas import TradePlanSchema
from app.alerts.formatter import AlertFormatter


def test_alert_formatter_triple_confluence():
    """
    Test Markdown and JSON rendering for 3-Achievement Triple Confluence Demand Plan.
    """
    plan = TradePlanSchema(
        symbol="RELIANCE",
        direction=ZoneDirection.DEMAND,
        current_price=2420.0,
        overlap_min_price=2380.0,
        overlap_max_price=2400.0,
        entry_price=2400.0,
        stop_loss=2370.0,
        risk_per_share=30.0,
        target_1=2460.0,
        target_2=2505.0,
        target_3=2550.0,
        atr_1d_14=50.0,
        atr_buffer=10.0,
        distance_pct=0.83,
        is_approaching=True,
        ema_20=2410.0,
        ema_50=2390.0,  # inside [2370, 2410]
        sma_200=2350.0,
        has_ma_confluence=True,
        achievements=3,
        participating_timeframes=[Timeframe.QUARTERLY, Timeframe.MONTHLY, Timeframe.DAILY]
    )

    payload = AlertFormatter.create_alert_payload(plan, AlertType.APPROACHING)
    assert payload.achievement_tier == "🥇 3-ACHIEVEMENT TRIPLE CONFLUENCE"
    assert payload.achievements == 3
    assert "#3M" in " ".join([f"#{tf}" for tf in payload.participating_timeframes])

    # Test Telegram Markdown Rendering
    md = AlertFormatter.format_telegram_markdown(payload)
    assert "RELIANCE" in md
    assert "🥇 3-ACHIEVEMENT TRIPLE CONFLUENCE" in md
    assert "[APPROACHING ZONE]" in md
    assert "₹2,400.00" in md  # Entry
    assert "₹2,370.00" in md  # SL
    assert "₹2,460.00" in md  # T1
    assert "50 EMA / 200 SMA Nested" in md

    # Test Webhook JSON Rendering
    wh = AlertFormatter.format_webhook_json(payload)
    assert wh["event"] == "APPROACHING"
    assert wh["symbol"] == "RELIANCE"
    assert wh["direction"] == "DEMAND"
    assert wh["market_data"]["entry_price"] == 2400.0
    assert wh["targets"]["t1_2R"] == 2460.0
    assert wh["moving_averages"]["has_ma_confluence"] is True
