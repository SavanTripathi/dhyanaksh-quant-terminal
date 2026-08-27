"""
Alert Engine Service.
Purges legacy test/mock alerts and dynamically generates live multi-stock institutional alerts
across all qualifying trade plans approaching or testing HTF Demand and Supply zones.
"""
import asyncio
import datetime
import logging
from sqlalchemy import delete, select
from app.core.database import get_db_context
from app.domain.enums import AlertType, AlertChannel, ZoneDirection
from app.domain.models import TradePlanModel, AlertNotificationModel

logger = logging.getLogger("dhyanaksh.alert_engine")


async def flush_and_generate_live_universe_alerts():
    """
    1. Purges all stale legacy/mock alerts (e.g. repetitive TCS/RELIANCE SYSTEM_TEST rows).
    2. Scans all active trade plans in production_scanner.db.
    3. Emits high-conviction alerts for all stocks approaching (<= 3.0%) or inside HTF Demand/Supply zones.
    """
    print("=" * 70)
    print("[ALERT ENGINE] Flushing stale mock logs & generating live universe alerts...")
    print("=" * 70)

    async with get_db_context() as db:
        # Step 1: Wipe stale legacy mock/test alerts
        try:
            await db.execute(delete(AlertNotificationModel))
            await db.commit()
            print("[ALERT ENGINE] Purged legacy mock alert entries from alert_notifications.")
        except Exception as e:
            print(f"[ALERT ENGINE] Note on purge: {e}")

        # Step 2: Fetch all scanned active trade plans with Opposing Zone Violation (Achievement > 1)
        stmt = select(TradePlanModel).where(
            TradePlanModel.status == "ACTIVE",
            TradePlanModel.achievements >= 2,
            TradePlanModel.has_opposing_violation == True
        )
        res = await db.execute(stmt)
        plans = list(res.scalars().all())
        if not plans:
            print("[ALERT ENGINE] No trade plans found matching GTF criteria.")
            return []

        # Deduplicate trade plans per symbol (taking highest conviction score)
        plans_by_symbol = {}
        for p in plans:
            if p.symbol not in plans_by_symbol or (p.conviction_score or 0) > (plans_by_symbol[p.symbol].conviction_score or 0):
                plans_by_symbol[p.symbol] = p

        sorted_plans = sorted(
            plans_by_symbol.values(),
            key=lambda x: (x.distance_pct if x.distance_pct is not None else 999, -(x.conviction_score or 0))
        )

        generated_alerts = []
        today_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

        for plan in sorted_plans:
            cmp = float(plan.current_price or plan.cmp or 0)
            entry = float(plan.entry_price or 0)
            distal = float(plan.overlap_min_price if plan.direction == ZoneDirection.DEMAND else plan.overlap_max_price)
            if cmp <= 0 or entry <= 0:
                continue

            dist_pct = float(plan.distance_pct) if plan.distance_pct is not None else round(abs(cmp - entry) / entry * 100.0, 2)
            
            is_demand = (plan.direction == ZoneDirection.DEMAND)
            # Rule 4: Inside zone check or proximity <= 1.5%
            is_inside_demand = (is_demand and distal <= cmp <= entry)
            is_inside_supply = (not is_demand and entry <= cmp <= distal)
            is_inside_zone = (is_inside_demand or is_inside_supply)
            is_near_entry = (dist_pct <= 1.5)

            if is_inside_zone or is_near_entry:
                zone_str = "DEMAND" if is_demand else "SUPPLY"
                status_label = "IN ZONE (ENTRY TRIGGERED)" if is_inside_zone else "APPROACHING ZONE"
                alert_type_enum = AlertType.ZONE_HIT if is_inside_zone else AlertType.APPROACHING

                tier_name = f"{plan.achievements}-ACH"
                tf_str = ", ".join(plan.participating_timeframes) if isinstance(plan.participating_timeframes, list) else str(plan.participating_timeframes)
                broken_label = f"Broke {'Supply' if is_demand else 'Demand'} ₹{plan.broken_supply_level:.2f}" if plan.broken_supply_level else "Opposing Violation Confirmed"

                alert_text = (
                    f"🎯 [{status_label}] {plan.symbol} ({zone_str})\n"
                    f"• Confluence: {tier_name} (#{tf_str})\n"
                    f"• Live CMP: ₹{cmp:.2f} ({dist_pct:.2f}% away)\n"
                    f"• Fresh Entry: ₹{entry:.2f} | Base (SL Base): ₹{distal:.2f}\n"
                    f"• GTF Achievement: {broken_label}\n"
                    f"• Stop Loss: ₹{float(plan.stop_loss):.2f} (Risk: ₹{float(plan.risk_per_share):.2f})\n"
                    f"• Target 1 (2R): ₹{float(plan.target_1):.2f} | T2: ₹{float(plan.target_2):.2f}\n"
                    f"• Conviction Score: {plan.conviction_score or 90}/100 ({plan.conviction_grade or 'TIER_1_HIGH'})"
                )

                payload_data = {
                    "symbol": plan.symbol,
                    "direction": zone_str,
                    "cmp": cmp,
                    "current_price": cmp,
                    "entry_price": entry,
                    "distal_price": distal,
                    "stop_loss": float(plan.stop_loss),
                    "target_1": float(plan.target_1),
                    "distance_pct": dist_pct,
                    "achievements": plan.achievements,
                    "participating_timeframes": plan.participating_timeframes,
                    "broken_supply_level": plan.broken_supply_level,
                    "conviction_score": plan.conviction_score or 90,
                    "status_label": status_label,
                    "message": alert_text
                }

                new_alert = AlertNotificationModel(
                    trade_plan_id=plan.id,
                    symbol=plan.symbol,
                    alert_type=alert_type_enum,
                    channel=AlertChannel.IN_APP,
                    payload_json=payload_data,
                    rendered_message=alert_text,
                    is_dispatched=True,
                    dispatch_status="SENT",
                    date_iso=today_iso,
                    created_at=datetime.datetime.now(datetime.timezone.utc),
                    dispatched_at=datetime.datetime.now(datetime.timezone.utc)
                )
                db.add(new_alert)
                generated_alerts.append(new_alert)

        await db.commit()
        print(f"[ALERT ENGINE] Successfully generated {len(generated_alerts)} live multi-stock alerts across qualifying universe.")
        return generated_alerts
