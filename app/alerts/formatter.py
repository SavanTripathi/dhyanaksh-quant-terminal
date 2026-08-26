"""
Institutional Alert Message Formatter.
Renders high-conviction institutional alert payloads into Telegram Markdown and Webhook JSON formats.
"""
from typing import Dict, Any
from app.domain.enums import ZoneDirection, AlertType
from app.domain.schemas import TradePlanSchema, AlertPayload


class AlertFormatter:
    """
    Formats trade plans and lifecycle events into structured institutional alert payloads.
    """

    @staticmethod
    def get_achievement_tier(achievements: int) -> str:
        if achievements >= 3:
            return "🥇 3-ACHIEVEMENT TRIPLE CONFLUENCE"
        elif achievements == 2:
            return "🥈 2-ACHIEVEMENT DUAL CONFLUENCE"
        else:
            return "🥉 1-ACHIEVEMENT ZONE"

    @classmethod
    def create_alert_payload(
        cls,
        plan: TradePlanSchema,
        alert_type: AlertType,
        notes: str = None
    ) -> AlertPayload:
        """
        Creates strongly-typed AlertPayload from TradePlanSchema.
        """
        tier_str = cls.get_achievement_tier(plan.achievements)
        tf_strings = [tf.value for tf in plan.participating_timeframes]

        return AlertPayload(
            symbol=plan.symbol,
            exchange="NSE",
            alert_type=alert_type,
            direction=plan.direction,
            achievement_tier=tier_str,
            achievements=plan.achievements,
            participating_timeframes=tf_strings,
            current_price=plan.current_price,
            distance_pct=plan.distance_pct,
            proximal_entry=plan.entry_price,
            distal_boundary=plan.overlap_min_price if plan.direction == ZoneDirection.DEMAND else plan.overlap_max_price,
            stop_loss=plan.stop_loss,
            target_1=plan.target_1,
            target_2=plan.target_2,
            target_3=plan.target_3,
            risk_per_share=plan.risk_per_share,
            atr_buffer=plan.atr_buffer,
            ema_20=plan.ema_20,
            ema_50=plan.ema_50,
            sma_200=plan.sma_200,
            has_ma_confluence=plan.has_ma_confluence,
            notes=notes
        )

    @classmethod
    def format_telegram_markdown(cls, payload: AlertPayload) -> str:
        """
        Renders rich Telegram message with institutional badges, metrics, and targets.
        """
        direction_emoji = "🟢" if payload.direction == ZoneDirection.DEMAND else "🔴"
        alert_emoji = "🚨"
        if payload.alert_type == AlertType.APPROACHING:
            alert_emoji = "👀 [APPROACHING ZONE]"
        elif payload.alert_type == AlertType.ZONE_HIT:
            alert_emoji = "🎯 [ZONE ENTRY HIT]"
        elif payload.alert_type == AlertType.TARGET_1_HIT:
            alert_emoji = "💰 [TARGET 1 (2.0R) ACHIEVED]"
        elif payload.alert_type == AlertType.TARGET_2_HIT:
            alert_emoji = "🚀 [TARGET 2 (3.5R) ACHIEVED]"
        elif payload.alert_type == AlertType.TARGET_3_HIT:
            alert_emoji = "🏆 [TARGET 3 (5.0R) ACHIEVED]"
        elif payload.alert_type == AlertType.INVALIDATED:
            alert_emoji = "❌ [ZONE INVALIDATED / SL HIT]"
        elif payload.alert_type == AlertType.SYSTEM_TEST:
            alert_emoji = "🔔 [SYSTEM TEST CONNECTIVITY]"

        tf_badges = " | ".join([f"#{tf}" for tf in payload.participating_timeframes])
        ma_status = "✅ 50 EMA / 200 SMA Nested" if payload.has_ma_confluence else "➖ None inside zone"

        msg = (
            f"{direction_emoji} *{payload.symbol}* ({payload.exchange}) — {alert_emoji}\n"
            f"*Setup:* FRESH {payload.direction.value}\n"
            f"*Confluence:* {payload.achievement_tier}\n"
            f"*Timeframes:* `{tf_badges}`\n\n"
            f"📊 *Execution Levels:*\n"
            f"• *Current Price:* ₹{payload.current_price:,.2f} ({payload.distance_pct:.2f}% away)\n"
            f"• *Proximal Entry:* ₹{payload.proximal_entry:,.2f}\n"
            f"• *Distal Boundary:* ₹{payload.distal_boundary:,.2f}\n"
            f"• *Stop Loss:* ₹{payload.stop_loss:,.2f} (Buffer: ₹{payload.atr_buffer:,.2f})\n"
            f"• *Risk / Share (1R):* ₹{payload.risk_per_share:,.2f}\n\n"
            f"🎯 *Deterministic Targets:*\n"
            f"• *T1 (2.0R):* ₹{payload.target_1:,.2f}\n"
            f"• *T2 (3.5R):* ₹{payload.target_2:,.2f}\n"
            f"• *T3 (5.0R):* ₹{payload.target_3:,.2f}\n\n"
            f"📈 *Trend Confluence:* {ma_status}\n"
            f"• 20 EMA: ₹{payload.ema_20:,.2f} | 50 EMA: ₹{payload.ema_50:,.2f} | 200 SMA: ₹{payload.sma_200:,.2f}"
        )
        return msg

    @classmethod
    def format_webhook_json(cls, payload: AlertPayload) -> Dict[str, Any]:
        """
        Renders structured JSON dictionary for outbound webhooks.
        """
        return {
            "event": payload.alert_type.value,
            "symbol": payload.symbol,
            "exchange": payload.exchange,
            "direction": payload.direction.value,
            "achievements": payload.achievements,
            "achievement_tier": payload.achievement_tier,
            "participating_timeframes": payload.participating_timeframes,
            "market_data": {
                "current_price": payload.current_price,
                "distance_pct": payload.distance_pct,
                "entry_price": payload.proximal_entry,
                "distal_boundary": payload.distal_boundary,
                "stop_loss": payload.stop_loss,
                "risk_per_share": payload.risk_per_share,
                "atr_buffer": payload.atr_buffer
            },
            "targets": {
                "t1_2R": payload.target_1,
                "t2_3_5R": payload.target_2,
                "t3_5R": payload.target_3
            },
            "moving_averages": {
                "ema_20": payload.ema_20,
                "ema_50": payload.ema_50,
                "sma_200": payload.sma_200,
                "has_ma_confluence": payload.has_ma_confluence
            }
        }
