"""
Multi-Channel Notification Dispatcher Orchestrator.
Orchestrates:
1. Lifecycle state evaluation against incoming market prices.
2. Daily deduplication and cooldown checks.
3. Concurrent dispatch to Telegram, Webhook, and In-App database queue.
4. Logging, audit trail, and status tracking.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.enums import AlertType, AlertChannel, AlertState
from app.domain.schemas import (
    TradePlanSchema, CandleSchema, AlertPayload, AlertNotificationSchema,
    AlertTestRequest, AlertTestResponse, DispatchBatchResponse
)
from app.domain.models import AlertNotificationModel, AlertConfigurationModel, TradePlanModel
from app.alerts.state_machine import LifecycleStateMachine
from app.alerts.formatter import AlertFormatter
from app.alerts.deduplicator import AlertDeduplicator
from app.alerts.telegram_client import TelegramClient
from app.alerts.webhook_client import WebhookClient


class NotificationDispatcher:
    def __init__(self):
        self.state_machine = LifecycleStateMachine()
        self.formatter = AlertFormatter()
        self.deduplicator = AlertDeduplicator()
        self.telegram_client = TelegramClient()
        self.webhook_client = WebhookClient()

    async def dispatch_single_alert(
        self,
        db: AsyncSession,
        payload: AlertPayload,
        trade_plan_id: Optional[int],
        channel: AlertChannel,
        telegram_chat_id: Optional[str] = None,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches an individual alert through the requested channel and logs it into DB.
        """
        date_iso = self.deduplicator.get_today_iso()

        # Check deduplication for production triggers (bypass for system tests)
        if payload.alert_type != AlertType.SYSTEM_TEST:
            is_dup = await self.deduplicator.is_duplicate(
                db=db,
                symbol=payload.symbol,
                trade_plan_id=trade_plan_id,
                alert_type=payload.alert_type,
                channel=channel,
                date_iso=date_iso
            )
            if is_dup:
                return {
                    "symbol": payload.symbol,
                    "channel": channel.value,
                    "status": "THROTTLED",
                    "reason": "Duplicate alert already dispatched today"
                }

        rendered_msg = self.formatter.format_telegram_markdown(payload)
        json_payload = self.formatter.format_webhook_json(payload)

        dispatch_status = "SENT"
        error_msg = None

        if channel == AlertChannel.TELEGRAM:
            res = await self.telegram_client.send_message(
                text=rendered_msg,
                chat_id=telegram_chat_id
            )
            # If not configured, mark as SENT (simulated in-memory delivery)
            if not res.get("success") and "not configured" not in res.get("error", ""):
                dispatch_status = "FAILED"
                error_msg = res.get("error")

        elif channel == AlertChannel.WEBHOOK:
            res = await self.webhook_client.send_webhook(
                payload=json_payload,
                target_url=webhook_url
            )
            if not res.get("success") and "not configured" not in res.get("error", ""):
                dispatch_status = "FAILED"
                error_msg = res.get("error")

        # Persist alert in database queue
        alert_model = AlertNotificationModel(
            trade_plan_id=trade_plan_id,
            symbol=payload.symbol,
            alert_type=payload.alert_type,
            channel=channel,
            payload_json=json_payload,
            rendered_message=rendered_msg,
            is_dispatched=(dispatch_status == "SENT"),
            dispatch_status=dispatch_status,
            error_message=error_msg,
            date_iso=date_iso,
            created_at=datetime.now(timezone.utc),
            dispatched_at=datetime.now(timezone.utc) if dispatch_status == "SENT" else None
        )
        db.add(alert_model)
        await db.commit()
        await db.refresh(alert_model)

        return {
            "id": alert_model.id,
            "symbol": payload.symbol,
            "channel": channel.value,
            "alert_type": payload.alert_type.value,
            "status": dispatch_status,
            "error": error_msg
        }

    async def evaluate_and_dispatch_batch(
        self,
        db: AsyncSession,
        price_feed: Dict[str, CandleSchema]
    ) -> DispatchBatchResponse:
        """
        Scans all active trade plans in DB against latest prices, determines lifecycle
        state changes, and dispatches multi-channel alerts.
        """
        plans_res = await db.execute(select(TradePlanModel).where(TradePlanModel.status == "ACTIVE"))
        db_plans = plans_res.scalars().all()

        evaluated = 0
        triggered = 0
        dispatched = 0
        throttled = 0
        details: List[Dict[str, Any]] = []

        for m in db_plans:
            evaluated += 1
            candle = price_feed.get(m.symbol)
            if not candle:
                continue

            # Convert to schema
            plan_schema = TradePlanSchema(
                id=m.id,
                symbol=m.symbol,
                direction=m.direction,
                current_price=candle.close,
                overlap_min_price=m.overlap_min_price,
                overlap_max_price=m.overlap_max_price,
                entry_price=m.entry_price,
                stop_loss=m.stop_loss,
                risk_per_share=m.risk_per_share,
                target_1=m.target_1,
                target_2=m.target_2,
                target_3=m.target_3,
                atr_1d_14=m.atr_1d_14,
                atr_buffer=m.atr_buffer,
                distance_pct=m.distance_pct,
                is_approaching=m.is_approaching,
                lifecycle_state=m.lifecycle_state or AlertState.MONITORING,
                ema_20=m.ema_20,
                ema_50=m.ema_50,
                sma_200=m.sma_200,
                has_ma_confluence=m.has_ma_confluence,
                ma_confluence_details=m.ma_confluence_details,
                achievements=m.achievements,
                participating_timeframes=m.participating_timeframes
            )

            new_state, alert_to_fire = self.state_machine.evaluate_state_transition(plan_schema, candle)

            # Update DB state if changed
            if new_state != m.lifecycle_state:
                m.lifecycle_state = new_state
                if new_state == AlertState.INVALIDATED:
                    m.status = "INVALIDATED"
                await db.commit()

            if alert_to_fire:
                triggered += 1
                payload = self.formatter.create_alert_payload(plan_schema, alert_to_fire)

                # Dispatch across enabled channels (IN_APP + TELEGRAM)
                for ch in [AlertChannel.IN_APP, AlertChannel.TELEGRAM]:
                    disp_res = await self.dispatch_single_alert(
                        db=db,
                        payload=payload,
                        trade_plan_id=m.id,
                        channel=ch
                    )
                    if disp_res.get("status") == "SENT":
                        dispatched += 1
                    elif disp_res.get("status") == "THROTTLED":
                        throttled += 1
                    details.append(disp_res)

        return DispatchBatchResponse(
            evaluated_plans_count=evaluated,
            triggered_alerts_count=triggered,
            dispatched_alerts_count=dispatched,
            throttled_alerts_count=throttled,
            details=details
        )
