"""
Alert Deduplication & Throttling Engine.
Ensures:
- Idempotent dispatches: Zero duplicate notifications for the same stock, trade plan, alert type on the same date.
- State transitions (e.g. APPROACHING -> ZONE_HIT) are permitted on the same date.
"""
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.enums import AlertType, AlertChannel
from app.domain.models import AlertNotificationModel


class AlertDeduplicator:
    """
    Guarantees idempotency and prevents notification spam across trading sessions.
    """

    @staticmethod
    def get_today_iso() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    @classmethod
    async def is_duplicate(
        cls,
        db: AsyncSession,
        symbol: str,
        trade_plan_id: Optional[int],
        alert_type: AlertType,
        channel: AlertChannel,
        date_iso: Optional[str] = None
    ) -> bool:
        """
        Returns True if an alert with identical (symbol, trade_plan_id, alert_type, channel, date_iso)
        was already recorded/dispatched.
        """
        if date_iso is None:
            date_iso = cls.get_today_iso()

        query = select(AlertNotificationModel).where(
            AlertNotificationModel.symbol == symbol,
            AlertNotificationModel.trade_plan_id == trade_plan_id,
            AlertNotificationModel.alert_type == alert_type,
            AlertNotificationModel.channel == channel,
            AlertNotificationModel.date_iso == date_iso,
            AlertNotificationModel.dispatch_status.in_(["SENT", "PENDING"])
        )

        res = await db.execute(query)
        existing = res.scalars().first()
        return existing is not None
