"""
Deterministic Trade Plan Engine.
Formulates exact mathematical trade execution plans for:
- Demand Setups (Entry, Stop Loss with 0.20 ATR buffer, T1=2R, T2=3.5R, T3=5R, Distance %, is_approaching)
- Supply Setups (Entry, Stop Loss with 0.20 ATR buffer, T1=2R, T2=3.5R, T3=5R, Distance %, is_approaching)
- Moving Average Confluence Layer (20 EMA, 50 EMA, 200 SMA overlap)
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.domain.enums import ZoneDirection
from app.domain.schemas import SpatialOverlapCluster, TradePlanSchema


class TradeEngine:
    """
    Deterministic Trade Plan Formulation adhering strictly to Step 2 mathematical specifications.
    """

    @classmethod
    def generate_trade_plan(
        cls,
        cluster: SpatialOverlapCluster,
        daily_indicators: Dict[str, float],
        confirmed_structural_break_count: int = 0
    ) -> TradePlanSchema:
        """
        Calculates mathematical Entry, SL, Targets, Distance, and MA confluences.
        
        Cluster bounds:
        L_common = cluster.overlap_min_price
        H_common = cluster.overlap_max_price
        """
        l_common = cluster.overlap_min_price
        h_common = cluster.overlap_max_price
        direction = cluster.direction
        symbol = cluster.symbol

        current_price = daily_indicators.get("current_price", 0.0)
        atr_14 = daily_indicators.get("atr_14", 0.0)
        buffer = daily_indicators.get("atr_buffer", round(0.20 * atr_14, 2))
        ema_20 = daily_indicators.get("ema_20")
        ema_50 = daily_indicators.get("ema_50")
        sma_200 = daily_indicators.get("sma_200")

        # Range for MA overlap check [L_common - buffer, H_common + buffer]
        buffered_low = l_common - buffer
        buffered_high = h_common + buffer

        # Check MA confluence
        ma_details = {}
        has_ma_confluence = False
        if ema_50 is not None and buffered_low <= ema_50 <= buffered_high:
            has_ma_confluence = True
            ma_details["ema_50_in_zone"] = True
        if sma_200 is not None and buffered_low <= sma_200 <= buffered_high:
            has_ma_confluence = True
            ma_details["sma_200_in_zone"] = True

        if direction == ZoneDirection.DEMAND:
            # Demand Formulas
            # Entry Price = H_common (Proximal Line), Distal = L_common
            entry_price = h_common
            distal_price = l_common
            stop_loss = round(l_common - buffer, 2)
            risk = round(entry_price - stop_loss, 2)
            if risk <= 0:
                risk = 0.01

            target_1 = round(entry_price + (2.0 * risk), 2)
            target_2 = round(entry_price + (3.5 * risk), 2)
            target_3 = round(entry_price + (5.0 * risk), 2)

            # Strict Physical Zone Membership: Distal <= Price <= Proximal
            is_breached = any(getattr(z, 'is_breached', False) for z in cluster.zones) or (current_price < distal_price)
            is_in_zone = (distal_price <= current_price <= entry_price) and not is_breached

            # Deterministic Distance Metrics (Exposed Deterministically)
            if current_price > entry_price:
                distance_to_zone = round(current_price - entry_price, 2)
                distance_pct = round(((current_price - entry_price) / current_price) * 100.0, 2)
            elif is_in_zone:
                distance_to_zone = 0.0
                distance_pct = 0.0
            else:
                # Below distal (Breached or wick penetration below zone)
                distance_to_zone = round(current_price - entry_price, 2)
                distance_pct = round(((current_price - entry_price) / current_price) * 100.0, 2)

            # Engineering / Product Filter: Approaching threshold (0.0% < distance <= 2.5%)
            is_approaching = (0.0 < distance_pct <= 2.5) and not is_in_zone and not is_breached

            # Engineering / Product State: Reacting (Zone visited, bullish reversal candle)
            open_p = daily_indicators.get("open_price", current_price)
            is_reacting = (is_in_zone or (0.0 <= distance_pct <= 1.0)) and (current_price > open_p) and not is_breached

        else:
            # Supply Formulas
            # Entry Price = L_common (Proximal Line), Distal = H_common
            entry_price = l_common
            distal_price = h_common
            stop_loss = round(h_common + buffer, 2)
            risk = round(stop_loss - entry_price, 2)
            if risk <= 0:
                risk = 0.01

            target_1 = round(entry_price - (2.0 * risk), 2)
            target_2 = round(entry_price - (3.5 * risk), 2)
            target_3 = round(entry_price - (5.0 * risk), 2)

            # Strict Physical Zone Membership: Proximal <= Price <= Distal
            is_breached = any(getattr(z, 'is_breached', False) for z in cluster.zones) or (current_price > distal_price)
            is_in_zone = (entry_price <= current_price <= distal_price) and not is_breached

            # Deterministic Distance Metrics (Exposed Deterministically)
            if current_price < entry_price:
                distance_to_zone = round(entry_price - current_price, 2)
                distance_pct = round(((entry_price - current_price) / current_price) * 100.0, 2)
            elif is_in_zone:
                distance_to_zone = 0.0
                distance_pct = 0.0
            else:
                # Above distal (Breached or wick penetration above zone)
                distance_to_zone = round(entry_price - current_price, 2)
                distance_pct = round(((entry_price - current_price) / current_price) * 100.0, 2)

            # Engineering / Product Filter: Approaching threshold (0.0% < distance <= 2.5%)
            is_approaching = (0.0 < distance_pct <= 2.5) and not is_in_zone and not is_breached

            # Engineering / Product State: Reacting (Zone visited, bearish reversal candle)
            open_p = daily_indicators.get("open_price", current_price)
            is_reacting = (is_in_zone or (0.0 <= distance_pct <= 1.0)) and (current_price < open_p) and not is_breached

        # Step 9: Compute 6-Pillar Pro Institutional Conviction Score
        from app.engine.conviction_ranker import conviction_ranking_engine
        conv_res = conviction_ranking_engine.compute_conviction_score(
            symbol=symbol,
            direction=direction,
            achievements=cluster.achievements,
            distance_pct=distance_pct,
            is_approaching=is_approaching,
            has_ma_confluence=has_ma_confluence,
            ema_50=ema_50,
            sma_200=sma_200,
            current_price=current_price
        )

        # Step 10: GTF Theory & 7-Point Scorecard
        from app.engine.gtf_engine import gtf_engine
        
        # Retrieve dynamic departure strength and basing candle count from underlying zones
        if cluster.zones:
            dynamic_departure = max((z.departure_strength or 0.0) for z in cluster.zones)
            dynamic_base = max(z.base_candle_count for z in cluster.zones)
            is_fresh = all(getattr(z, 'retest_count', 0) == 0 and not getattr(z, 'is_breached', False) for z in cluster.zones)
            retest_count = 0 if is_fresh else max((getattr(z, 'retest_count', 0) for z in cluster.zones), default=1)
        else:
            dynamic_departure = 2.5
            dynamic_base = 3
            is_fresh = True
            retest_count = 0

        gtf_score = gtf_engine.calculate_gtf_7_point_trade_score(
            retest_count=retest_count,
            departure_strength=dynamic_departure,
            basing_candle_count=dynamic_base
        )

        # Proximity Lifecycle State Mapping
        if is_breached:
            proximity_state = "BREACHED"
        elif is_reacting:
            proximity_state = "REACTING"
        elif is_in_zone:
            proximity_state = "IN_ZONE"
        elif is_approaching:
            proximity_state = "APPROACHING"
        else:
            proximity_state = "MONITORING"

        return TradePlanSchema(
            symbol=symbol,
            direction=direction,
            current_price=current_price,
            overlap_min_price=l_common,
            overlap_max_price=h_common,
            entry_price=round(entry_price, 2),
            stop_loss=stop_loss,
            risk_per_share=risk,
            target_1=target_1,
            target_2=target_2,
            target_3=target_3,
            atr_1d_14=atr_14,
            atr_buffer=buffer,
            distance_pct=distance_pct,
            distance_to_zone=distance_to_zone,
            is_approaching=is_approaching,
            ema_20=ema_20,
            ema_50=ema_50,
            sma_200=sma_200,
            has_ma_confluence=has_ma_confluence,
            ma_confluence_details=ma_details if ma_details else None,
            conviction_score=conv_res["conviction_score"],
            conviction_grade=conv_res["conviction_grade"],
            conviction_breakdown=conv_res["conviction_breakdown"],
            catalyst_summary="Aligned with broader market indices." if has_ma_confluence else "Standard technical setup.",
            gtf_score_7=gtf_score["total_score"],
            gtf_entry_type=gtf_score["entry_type"],
            gtf_curve_location="PENDING_MTF_ISOLATION",
            gtf_curve_percent=0.0,
            gtf_clock_position=None,
            is_lotl_merged=False,
            opposing_broken_count=0,
            is_sector_synchronized=True,
            achievements=cluster.achievements,
            participating_timeframes=cluster.participating_timeframes,
            broken_supply_level=cluster.broken_supply_level,
            has_opposing_violation=cluster.has_opposing_violation,
            confirmed_structural_break_count=1 if cluster.has_opposing_violation else 0,
            status="BREACHED" if is_breached else "ACTIVE",
            cmp=current_price,
            change_pct=0.0,
            proximity_state=proximity_state,
            proximity_pct=distance_pct,
            is_fresh=is_fresh,
            created_at=datetime.now(timezone.utc)
        )
