"""
Unit tests for Alert Deduplication and Throttling Engine.
"""
from datetime import datetime, timezone
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.enums import AlertType, AlertChannel
from app.domain.models import AlertNotificationModel
from app.alerts.deduplicator import AlertDeduplicator
from app.core.database import AsyncSessionLocal


@pytest.mark.asyncio
async def test_alert_deduplication_idempotency():
    """
    Verify:
    1. First alert is not a duplicate.
    2. Same alert on the same date is detected as duplicate.
    3. New alert type (e.g. ZONE_HIT vs APPROACHING) on same date is NOT duplicate.
    """
    async with AsyncSessionLocal() as session:
        today_iso = AlertDeduplicator.get_today_iso()
        symbol = "TEST_STOCK"
        plan_id = 999

        # Step 1: Initial check should be false
        is_dup_1 = await AlertDeduplicator.is_duplicate(
            db=session,
            symbol=symbol,
            trade_plan_id=plan_id,
            alert_type=AlertType.APPROACHING,
            channel=AlertChannel.TELEGRAM,
            date_iso=today_iso
        )
        assert is_dup_1 is False

        # Step 2: Insert notification record
        alert_rec = AlertNotificationModel(
            trade_plan_id=plan_id,
            symbol=symbol,
            alert_type=AlertType.APPROACHING,
            channel=AlertChannel.TELEGRAM,
            payload_json={"test": True},
            is_dispatched=True,
            dispatch_status="SENT",
            date_iso=today_iso,
            created_at=datetime.now(timezone.utc)
        )
        session.add(alert_rec)
        await session.commit()

        # Step 3: Second check with identical parameters must be True (Duplicate)
        is_dup_2 = await AlertDeduplicator.is_duplicate(
            db=session,
            symbol=symbol,
            trade_plan_id=plan_id,
            alert_type=AlertType.APPROACHING,
            channel=AlertChannel.TELEGRAM,
            date_iso=today_iso
        )
        assert is_dup_2 is True

        # Step 4: State transition to ZONE_HIT must NOT be throttled
        is_dup_3 = await AlertDeduplicator.is_duplicate(
            db=session,
            symbol=symbol,
            trade_plan_id=plan_id,
            alert_type=AlertType.ZONE_HIT,
            channel=AlertChannel.TELEGRAM,
            date_iso=today_iso
        )
        assert is_dup_3 is False
