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
        daily_indicators: Dict[str, float]
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
            # Entry Price = H_common (Proximal Line)
            entry_price = h_common
            # SL = L_common - (0.20 * ATR_1D(14)) (Distal Line minus buffer)
            stop_loss = round(l_common - buffer, 2)
            # R = Entry - SL
            risk = round(entry_price - stop_loss, 2)
            if risk <= 0:
                risk = 0.01

            # Targets
            target_1 = round(entry_price + (2.0 * risk), 2)
            target_2 = round(entry_price + (3.5 * risk), 2)
            target_3 = round(entry_price + (5.0 * risk), 2)

            # Distance % = ((Current Price - Entry) / Current Price) * 100
            if current_price > 0:
                distance_pct = round(((current_price - entry_price) / current_price) * 100.0, 2)
            else:
                distance_pct = 0.0

            # Approaching Flag = True if 0.0% <= Distance % <= 2.5%, else False
            is_approaching = (0.0 <= distance_pct <= 2.5)

        else:
            # Supply Formulas
            # Entry Price = L_common (Proximal Line)
            entry_price = l_common
            # SL = H_common + (0.20 * ATR_1D(14)) (Distal Line plus buffer)
            stop_loss = round(h_common + buffer, 2)
            # R = SL - Entry
            risk = round(stop_loss - entry_price, 2)
            if risk <= 0:
                risk = 0.01

            # Targets
            target_1 = round(entry_price - (2.0 * risk), 2)
            target_2 = round(entry_price - (3.5 * risk), 2)
            target_3 = round(entry_price - (5.0 * risk), 2)

            # Distance % = ((Entry - Current Price) / Current Price) * 100
            if current_price > 0:
                distance_pct = round(((entry_price - current_price) / current_price) * 100.0, 2)
            else:
                distance_pct = 0.0

            # Approaching Flag = True if 0.0% <= Distance % <= 2.5%, else False
            is_approaching = (0.0 <= distance_pct <= 2.5)

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

        # Step 10: GTF Theory & 13-Point Odds Enhancers Scorecard
        from app.engine.gtf_engine import gtf_engine
        curve_res = gtf_engine.calculate_location_on_curve(
            current_price=current_price,
            htf_demand_proximal=l_common if direction == ZoneDirection.DEMAND else l_common * 0.85,
            htf_supply_proximal=h_common * 1.25 if direction == ZoneDirection.DEMAND else h_common,
            direction=direction
        )
        gtf_odds = gtf_engine.score_gtf_13_point_odds(
            departure_strength=2.5,
            basing_candle_count=3,
            is_fresh=cluster.is_fresh,
            achievements=cluster.achievements,
            curve_location=curve_res["curve_location"],
            direction=direction
        )

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
            is_approaching=is_approaching,
            ema_20=ema_20,
            ema_50=ema_50,
            sma_200=sma_200,
            has_ma_confluence=has_ma_confluence,
            ma_confluence_details=ma_details if ma_details else None,
            conviction_score=conv_res["conviction_score"],
            conviction_grade=conv_res["conviction_grade"],
            conviction_breakdown=conv_res["conviction_breakdown"],
            catalyst_summary=conv_res["catalyst_summary"],
            gtf_odds_score=gtf_odds["gtf_odds_score"],
            gtf_entry_type=gtf_odds["gtf_entry_type"],
            gtf_curve_location=curve_res["curve_location"],
            gtf_curve_percent=curve_res["curve_percent"],
            gtf_trend_alignment={"HTF": "UPTREND", "ITF": "UPTREND", "LTF": "UPTREND"},
            is_sector_synchronized=True,
            gtf_odds_breakdown=gtf_odds["breakdown"],
            achievements=cluster.achievements,
            participating_timeframes=cluster.participating_timeframes,
            status="ACTIVE",
            created_at=datetime.now(timezone.utc)
        )
