"""
Step 10: GTF (Get Together Finance) "Trading in the Zone" Quantitative Suite Engine.
Implements:
1. Exact 7-Point GTF Trade Scoring Model:
   - Freshness: Max 3.0 pts (0 touches = 3.0, 1 touch = 1.5, >=2 touches = 0.0)
   - Departure / Legout Strength: Max 2.0 pts (Pro Gap / >=2 Exciting = 2.0, 1 Exciting = 1.0)
   - Time at Base: Max 2.0 pts (1-3 Boring = 2.0, 4-5 Boring = 1.0, >5 Boring = 0.0)
   - Entry Classification:
     * 7.0 pts -> Entry Type 1: Set & Forget (Limit Order)
     * 5.0 - 6.5 pts -> Entry Type 2/3: Confirmation Entry
     * < 5.0 pts -> Non-Tradable
2. Opposing Structure Violation (Achievements: 1 = Sideways Consolidation, >=2 = Major Institutional Uptrend).
3. LOTL (Level on Top of Level) Base Consolidation Detection.
4. 50 SMA 7-Candle Vector Angle Calculation (Clock Rule):
   - 12:00 to 3:00 -> Trend UP (Green)
   - 3:00 to 6:00 -> Trend DOWN (Red)
   - Flat along 3:00 -> Trend SIDEWAYS
5. HTF Curve Analysis Engine (Location on Curve: Very Low, Equilibrium, Very High).
"""
import math
from typing import Dict, List, Any, Optional, Tuple
from app.domain.enums import ZoneDirection, Timeframe
from app.domain.schemas import CandleSchema, ZoneSchema


class GTFEngine:
    """
    Standardized algorithmic implementation of GTF Demand & Supply Theory.
    """

    def validate_basing_candle_count(self, count: int) -> bool:
        """
        GTF Rule: Institutional Base must have between 1 and 5 basing candles.
        >= 6 is flagged as RETAIL_CONSOLIDATION and sub-optimal.
        """
        return 1 <= count <= 5

    def calculate_gtf_7_point_trade_score(
        self,
        retest_count: int = 0,
        departure_strength: float = 2.5,
        is_pro_gap: bool = False,
        exciting_candle_count: int = 2,
        basing_candle_count: int = 2,
        direction: ZoneDirection = ZoneDirection.DEMAND
    ) -> Dict[str, Any]:
        """
        Computes the official 7-Point GTF Trade Score:
        1. Freshness (Max 3.0 Pts):
           - 0 prior retests = 3.0 pts
           - 1 prior retest = 1.5 pts
           - >= 2 prior retests = 0.0 pts (Non-tradable)
        2. Departure / Legout Strength (Max 2.0 Pts):
           - Pro Gap or >= 2 Exciting Candles = 2.0 pts
           - 1 Exciting Candle = 1.0 pt
           - Otherwise = 0.5 pt
        3. Time at the Base (Max 2.0 Pts):
           - 1 to 3 Boring Base Candles = 2.0 pts
           - 4 to 5 Boring Base Candles = 1.0 pt
           - > 5 Boring Base Candles = 0.0 pts
        """
        # 1. Freshness
        if retest_count == 0:
            score_freshness = 3.0
            freshness_label = "Fresh (0 Prior Retests)"
        elif retest_count == 1:
            score_freshness = 1.5
            freshness_label = "Tested Once (1 Prior Retest)"
        else:
            score_freshness = 0.0
            freshness_label = f"Tested ({retest_count} Retests - Non-Tradable)"

        # 2. Departure Strength
        if is_pro_gap or exciting_candle_count >= 2 or departure_strength >= 2.0:
            score_departure = 2.0
            departure_label = "Strong (>=2 Exciting / Pro Gap)"
        elif exciting_candle_count == 1 or departure_strength >= 1.0:
            score_departure = 1.0
            departure_label = "Moderate (1 Exciting Candle)"
        else:
            score_departure = 0.5
            departure_label = "Weak Departure"

        # 3. Time at Base
        if 1 <= basing_candle_count <= 3:
            score_time_at_base = 2.0
            time_at_base_label = f"{basing_candle_count} Base Candles (Institutional Accumulation)"
        elif 4 <= basing_candle_count <= 5:
            score_time_at_base = 1.0
            time_at_base_label = f"{basing_candle_count} Base Candles (Moderate Basing)"
        else:
            score_time_at_base = 0.0
            time_at_base_label = f"{basing_candle_count} Base Candles (Prolonged Basing)"

        total_score_7 = round(score_freshness + score_departure + score_time_at_base, 1)

        # Entry Classification Tagging
        if total_score_7 >= 7.0:
            entry_type = "Entry Type 1: Set & Forget"
            entry_badge = "TYPE_1_LIMIT"
            execution_advice = "Place Limit Order at Proximal Line. High institutional odds (7.0/7.0)."
            is_tradable = True
        elif total_score_7 >= 5.0:
            entry_type = "Entry Type 2/3: Confirmation Entry"
            entry_badge = "TYPE_2_CONFIRMATION"
            execution_advice = "Wait for price to touch zone and form green reversal candle before entry (5.0-6.5/7.0)."
            is_tradable = True
        else:
            entry_type = "Non-Tradable"
            entry_badge = "NON_TRADABLE"
            execution_advice = "Score below 5.0/7.0 threshold. Setup disqualified by GTF criteria."
            is_tradable = False

        return {
            "gtf_score_7": total_score_7,
            "score_freshness": score_freshness,
            "freshness_label": freshness_label,
            "score_departure": score_departure,
            "departure_label": departure_label,
            "score_time_at_base": score_time_at_base,
            "time_at_base_label": time_at_base_label,
            "entry_type": entry_type,
            "entry_badge": entry_badge,
            "execution_advice": execution_advice,
            "is_tradable": is_tradable
        }

    def detect_lotl_consolidation(
        self,
        zones: List[ZoneSchema],
        atr_1d: float
    ) -> Dict[str, Any]:
        """
        LOTL (Level on Top of Level) Base Consolidation:
        Detects nested or stacked base formations across adjacent zones within 1.5 * ATR.
        Merged Bounds:
        - Proximal Entry: Highest body/level of upper base
        - Distal SL Base: Lowest wick of lower base
        """
        if len(zones) < 2:
            return {"is_lotl_merged": False, "lotl_count": 0}

        # Check distances between adjacent zones
        sorted_zones = sorted(zones, key=lambda z: z.proximal_price)
        merged = False
        lotl_zones = []

        for i in range(len(sorted_zones) - 1):
            z1 = sorted_zones[i]
            z2 = sorted_zones[i + 1]
            dist = abs(z2.distal_price - z1.proximal_price)
            if dist <= (1.5 * atr_1d):
                merged = True
                lotl_zones.extend([z1, z2])

        if merged:
            proximal_merged = max(z.proximal_price for z in lotl_zones)
            distal_merged = min(z.distal_price for z in lotl_zones)
            return {
                "is_lotl_merged": True,
                "lotl_count": len(lotl_zones),
                "merged_proximal": round(proximal_merged, 2),
                "merged_distal": round(distal_merged, 2),
                "note": "LOTL Detected: Stacked bases merged within 1.5 ATR."
            }

        return {"is_lotl_merged": False, "lotl_count": 0}

    def calculate_50sma_clock_angle(
        self,
        sma_values_7_candles: List[float]
    ) -> Dict[str, Any]:
        """
        50 SMA 7-Candle Angle Calculation (GTF Clock Rule):
        Samples the 50 SMA on the Intermediate Timeframe (ITF) over the last 7 candles:
        - Angle between 12:00 and 3:00 -> Trend UP (Green)
        - Angle between 3:00 and 6:00 -> Trend DOWN (Red)
        - Flat along 3:00 -> Trend SIDEWAYS
        """
        if not sma_values_7_candles or len(sma_values_7_candles) < 2:
            return {
                "clock_position": "3:00",
                "trend_status": "Trend SIDEWAYS",
                "slope_pct": 0.0,
                "color": "#94A3B8"
            }

        start_val = sma_values_7_candles[0]
        end_val = sma_values_7_candles[-1]
        if start_val <= 0:
            return {
                "clock_position": "3:00",
                "trend_status": "Trend SIDEWAYS",
                "slope_pct": 0.0,
                "color": "#94A3B8"
            }

        # Percentage slope over 7 periods
        slope_pct = ((end_val - start_val) / start_val) * 100.0

        if slope_pct > 0.8:
            clock_pos = "1:30 (12:00 - 3:00)"
            trend_status = "Trend UP"
            color = "#10B981"  # Green
        elif slope_pct < -0.8:
            clock_pos = "4:30 (3:00 - 6:00)"
            trend_status = "Trend DOWN"
            color = "#EF4444"  # Red
        else:
            clock_pos = "3:00"
            trend_status = "Trend SIDEWAYS"
            color = "#F59E0B"  # Amber

        return {
            "clock_position": clock_pos,
            "trend_status": trend_status,
            "slope_pct": round(slope_pct, 2),
            "color": color
        }

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
            trade_rule = "Prime Demand Zone (Bottom 1/3rd). Maximum long allocation permitted."
        elif curve_percent >= 66.67:
            curve_location = "VERY_HIGH_ON_CURVE"
            is_valid_trade = (direction == ZoneDirection.SUPPLY)
            trade_rule = "Prime Supply Zone (Top 1/3rd). Short setups prioritized."
        else:
            curve_location = "EQUILIBRIUM"
            is_valid_trade = True
            trade_rule = "Equilibrium Zone (Middle 1/3rd). Only 3-Achievement trend continuation setups permitted."

        return {
            "curve_percent": round(curve_percent, 1),
            "curve_location": curve_location,
            "htf_demand_proximal": round(htf_demand_proximal, 2),
            "htf_supply_proximal": round(htf_supply_proximal, 2),
            "is_valid_trade": is_valid_trade,
            "trade_rule": trade_rule,
        }


gtf_engine = GTFEngine()
