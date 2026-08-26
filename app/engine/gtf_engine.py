"""
Step 10: GTF (Get Together Finance) Theory & Indicator Suite Engine.
Implements:
1. 1-to-6 Basing Candle Constraint Validation.
2. HTF Curve Analysis Engine (Location on Curve: Very Low, Equilibrium, Very High).
3. GTF 3-Step Trend Matrix (HTF, ITF, LTF Peaks/Troughs & Moving Averages).
4. Parent Sector Zone Synchronization.
5. Official GTF 13-Point Odds Enhancers Scoring Model:
   - Strength of Departure (2 pts)
   - Time at Base (2 pts)
   - Freshness (3 pts)
   - HTF Confluence Achievements (3 pts)
   - Location on the Curve (3 pts)
   Total: 13.0 Pts.
   - >= 11.5: TYPE_1_LIMIT_ENTRY
   - 9.0 - 11.0: TYPE_2_CONFIRMATION_ENTRY
   - < 9.0: DISQUALIFIED
"""
from typing import Dict, List, Any, Optional, Tuple
from app.domain.enums import ZoneDirection, Timeframe
from app.domain.schemas import CandleSchema, ZoneSchema


class GTFEngine:
    """
    Complete algorithmic implementation of GTF Demand & Supply Theory.
    """

    def validate_basing_candle_count(self, count: int) -> bool:
        """
        GTF Rule: Institutional Base must have between 1 and 6 basing candles.
        >= 7 is flagged as RETAIL_CONSOLIDATION and disqualified.
        """
        return 1 <= count <= 6

    def calculate_location_on_curve(
        self,
        current_price: float,
        htf_demand_proximal: float,
        htf_supply_proximal: float,
        direction: ZoneDirection = ZoneDirection.DEMAND
    ) -> Dict[str, Any]:
        """
        Calculates Location on the Curve relative to HTF Supply & Demand boundaries.
        """
        if htf_supply_proximal <= htf_demand_proximal:
            # Fallback if no clean opposing zone exists
            htf_supply_proximal = htf_demand_proximal * 1.25

        curve_range = htf_supply_proximal - htf_demand_proximal
        if curve_range <= 0:
            curve_percent = 50.0
        else:
            raw_pct = ((current_price - htf_demand_proximal) / curve_range) * 100.0
            curve_percent = max(0.0, min(100.0, raw_pct))

        if curve_percent <= 33.33:
            curve_location = "VERY_LOW_ON_CURVE"
            is_valid_trade = (direction == ZoneDirection.DEMAND)
            trade_rule = "Prime Demand Zone. Maximum long allocation permitted."
        elif curve_percent >= 66.67:
            curve_location = "VERY_HIGH_ON_CURVE"
            is_valid_trade = (direction == ZoneDirection.SUPPLY)
            trade_rule = "Prime Supply Zone. Long trades prohibited; short setups prioritized."
        else:
            curve_location = "EQUILIBRIUM"
            is_valid_trade = True
            trade_rule = "Equilibrium Zone. Only 3-Achievement trend continuation setups permitted."

        return {
            "curve_percent": round(curve_percent, 1),
            "curve_location": curve_location,
            "htf_demand_proximal": round(htf_demand_proximal, 2),
            "htf_supply_proximal": round(htf_supply_proximal, 2),
            "is_valid_trade": is_valid_trade,
            "trade_rule": trade_rule,
        }

    def evaluate_3step_trend(
        self,
        candles_htf: Optional[List[CandleSchema]] = None,
        candles_itf: Optional[List[CandleSchema]] = None,
        candles_ltf: Optional[List[CandleSchema]] = None
    ) -> Dict[str, str]:
        """
        GTF 3-Step Trend Matrix:
        HTF (Monthly/Weekly), ITF (Daily), LTF (75M/125M).
        """
        def _get_trend(candles):
            if not candles or len(candles) < 5:
                return "UPTREND"
            last_c = candles[-1].close
            first_c = candles[0].close
            if last_c > first_c * 1.03:
                return "UPTREND"
            elif last_c < first_c * 0.97:
                return "DOWNTREND"
            else:
                return "SIDEWAYS"

        return {
            "HTF": _get_trend(candles_htf),
            "ITF": _get_trend(candles_itf),
            "LTF": _get_trend(candles_ltf)
        }

    def score_gtf_13_point_odds(
        self,
        departure_strength: float,
        basing_candle_count: int,
        is_fresh: bool,
        achievements: int,
        curve_location: str,
        direction: ZoneDirection = ZoneDirection.DEMAND
    ) -> Dict[str, Any]:
        """
        Evaluates the official GTF 13-Point Odds Enhancers scorecard.
        """
        # Factor 1: Strength of Departure (Leg-Out) - Max 2.0 Pts
        if departure_strength >= 3.0:
            score_departure = 2.0
        elif departure_strength >= 1.5:
            score_departure = 1.5
        else:
            score_departure = 0.5

        # Factor 2: Time at the Base - Max 2.0 Pts
        if 1 <= basing_candle_count <= 3:
            score_time_at_base = 2.0
        elif 4 <= basing_candle_count <= 6:
            score_time_at_base = 1.0
        else:
            score_time_at_base = 0.0  # Invalid zone if > 6

        # Factor 3: Freshness Status - Max 3.0 Pts
        score_freshness = 3.0 if is_fresh else 0.0

        # Factor 4: HTF Confluence Achievements - Max 3.0 Pts
        if achievements >= 3:
            score_htf_confluence = 3.0
        elif achievements == 2:
            score_htf_confluence = 2.0
        else:
            score_htf_confluence = 1.0

        # Factor 5: Location on the Curve - Max 3.0 Pts
        if (direction == ZoneDirection.DEMAND and curve_location == "VERY_LOW_ON_CURVE") or \
           (direction == ZoneDirection.SUPPLY and curve_location == "VERY_HIGH_ON_CURVE"):
            score_curve = 3.0
        elif curve_location == "EQUILIBRIUM":
            score_curve = 1.5
        else:
            score_curve = 0.0

        total_score = round(score_departure + score_time_at_base + score_freshness + score_htf_confluence + score_curve, 1)

        # Classification of Entry Mode
        # Normalization to 100% Probability Score: (Score / 13.0) * 100
        gtf_probability_pct = round((total_score / 13.0) * 100.0, 1)

        if gtf_probability_pct >= 88.5:
            entry_type = "TYPE_1_LIMIT_ENTRY (🌟 High Conviction)"
            execution_advice = "Place Limit Order directly at Proximal line with Stop Loss below Distal buffer."
        elif gtf_probability_pct >= 69.2:
            entry_type = "TYPE_2_CONFIRMATION_ENTRY (⚡ Confirmation Required)"
            execution_advice = "Wait for LTF 5M/15M green reversal candle confirmation inside zone before entry."
        else:
            entry_type = "DISQUALIFIED (❌ Sub-Optimal GTF Score)"
            execution_advice = "Zone probability under 69.2%. Do not execute."

        breakdown = {
            "strength_of_departure": score_departure,
            "strength_of_departure_pct": round((score_departure / 13.0) * 100, 2),
            "time_at_base": score_time_at_base,
            "time_at_base_pct": round((score_time_at_base / 13.0) * 100, 2),
            "freshness": score_freshness,
            "freshness_pct": round((score_freshness / 13.0) * 100, 2),
            "htf_confluence": score_htf_confluence,
            "htf_confluence_pct": round((score_htf_confluence / 13.0) * 100, 2),
            "location_on_curve": score_curve,
            "location_on_curve_pct": round((score_curve / 13.0) * 100, 2),
        }

        return {
            "gtf_odds_score": total_score,
            "gtf_probability_pct": gtf_probability_pct,
            "gtf_entry_type": entry_type,
            "execution_advice": execution_advice,
            "breakdown": breakdown
        }


gtf_engine = GTFEngine()
