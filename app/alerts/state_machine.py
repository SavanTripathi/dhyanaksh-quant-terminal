"""
Lifecycle Alert State Machine.
Tracks price progression against active higher-timeframe confluence trade plans:
1. MONITORING: Price > 2.5% away from Proximal Entry
2. APPROACHING: 0.0% <= Distance % <= 2.5% from Proximal Entry
3. INSIDE_ZONE / ZONE_HIT: Price penetrates proximal line into [L_common, H_common]
4. TARGET_HIT: Price touches T1, T2, or T3
5. INVALIDATED: Candle/Price breaches beyond Stop Loss / Distal Line
"""
from typing import Tuple, Optional
from app.domain.enums import ZoneDirection, AlertType, AlertState
from app.domain.schemas import TradePlanSchema, CandleSchema


class LifecycleStateMachine:
    """
    Evaluates lifecycle state transitions for Demand and Supply confluence plans.
    """

    @classmethod
    def evaluate_state_transition(
        cls,
        plan: TradePlanSchema,
        current_candle: CandleSchema
    ) -> Tuple[AlertState, Optional[AlertType]]:
        """
        Takes current price candle (High, Low, Close) and determines:
        - New lifecycle state (AlertState)
        - AlertType to fire (if state has transitioned), else None
        """
        high = current_candle.high
        low = current_candle.low
        close = current_candle.close
        direction = plan.direction

        l_common = plan.overlap_min_price
        h_common = plan.overlap_max_price
        entry = plan.entry_price
        sl = plan.stop_loss
        t1 = plan.target_1
        t2 = plan.target_2
        t3 = plan.target_3

        # 1. Invalidation Check (Highest Priority)
        if direction == ZoneDirection.DEMAND:
            if low <= sl or close <= sl:
                return AlertState.INVALIDATED, AlertType.INVALIDATED
        else:
            if high >= sl or close >= sl:
                return AlertState.INVALIDATED, AlertType.INVALIDATED

        # 2. Target Hit Checks
        if direction == ZoneDirection.DEMAND:
            if high >= t3:
                return AlertState.TARGET_3_HIT, AlertType.TARGET_3_HIT
            elif high >= t2:
                return AlertState.TARGET_2_HIT, AlertType.TARGET_2_HIT
            elif high >= t1:
                return AlertState.TARGET_1_HIT, AlertType.TARGET_1_HIT
        else:
            if low <= t3:
                return AlertState.TARGET_3_HIT, AlertType.TARGET_3_HIT
            elif low <= t2:
                return AlertState.TARGET_2_HIT, AlertType.TARGET_2_HIT
            elif low <= t1:
                return AlertState.TARGET_1_HIT, AlertType.TARGET_1_HIT

        # 3. Zone Hit / Inside Zone Check
        # For Demand: Entry is H_common. If Low <= H_common and Low >= SL -> Inside Zone
        # For Supply: Entry is L_common. If High >= L_common and High <= SL -> Inside Zone
        if direction == ZoneDirection.DEMAND:
            if low <= entry and low >= l_common:
                return AlertState.INSIDE_ZONE, AlertType.ZONE_HIT
        else:
            if high >= entry and high <= h_common:
                return AlertState.INSIDE_ZONE, AlertType.ZONE_HIT

        # 4. Approaching Check (0.0% <= Distance % <= 2.5%)
        # Calculate current distance based on current close
        if direction == ZoneDirection.DEMAND:
            distance_pct = round(((close - entry) / close) * 100.0, 2) if close > 0 else 0.0
            if 0.0 <= distance_pct <= 2.5:
                return AlertState.APPROACHING, AlertType.APPROACHING
        else:
            distance_pct = round(((entry - close) / close) * 100.0, 2) if close > 0 else 0.0
            if 0.0 <= distance_pct <= 2.5:
                return AlertState.APPROACHING, AlertType.APPROACHING

        # 5. Default State: Monitoring
        return AlertState.MONITORING, None
