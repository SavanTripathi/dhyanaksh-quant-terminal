"""
Validated Achievement Sequence Engine.
Phase 2 Mathematical Specification & Domain Contract:

================================================================================
FORMAL DOMAIN CONTRACT: VIOLATION VS CONFIRMED BREAK
================================================================================
Dhyanaksh formally distinguishes legacy Zone Violation from Confirmed Structural Break.

LAYER A — ZONE INTERACTION
A candle reaches or enters the supply zone (e.g., High >= Proximal).

LAYER B — ZONE VIOLATION / PENETRATION (LEGACY)
`has_opposing_violation` represents zone penetration/violation semantics inherited
from the legacy ZoneDetector (`High >= Proximal OR Close >= Distal`).
This is NOT a confirmed structural break.

LAYER C — CONFIRMED STRUCTURAL BREAK (PHASE 2)
`validated_current_sequence_breaks` represents a stricter Phase 2 confirmed
structural-break policy:

    Confirmed Supply Break ⇔ Candle Close >= Supply Proximal

This confirmed-break criterion is an explicit Dhyanaksh Phase 2 engineering policy.
It must NOT be falsely represented as a verbatim inherited rule from the legacy
GTF specification.

DISTAL-WICK EXPLICIT POLICY:
If High >= Distal but Close < Proximal, the confirmed structural break is FALSE.
This candle may represent penetration/violation under legacy semantics, but
validated_current_sequence_breaks += 0. This is an intentional Phase 2 policy decision.
================================================================================

Counting Semantics:
- total_detected_supply_zones: Total unique opposing supply zones detected on this timeframe.
- raw_historical_broken_supply_count: Unique supply zones ever confirmed broken (Close >= Proximal) after supply creation.
- validated_current_sequence_breaks: Unique supply zones confirmed broken strictly for the first time on or after active demand creation.
- rejected_pre_demand_breaks: Unique supply zones whose first confirmed break occurred before active demand creation.
- rejected_unbroken_supply: Unique supply zones that have never satisfied the confirmed break condition.

Mathematical Invariants strictly enforced:
1. validated_current_sequence_breaks <= raw_historical_broken_supply_count
2. validated_current_sequence_breaks + rejected_pre_demand_breaks == raw_historical_broken_supply_count
3. raw_historical_broken_supply_count + rejected_unbroken_supply == total_detected_supply_zones
"""
from typing import List, Dict, Optional, Any, Tuple
import os
import json
import logging
from datetime import datetime
import pandas as pd
from pydantic import BaseModel, Field

from app.domain.enums import Timeframe, ZoneDirection, FreshnessStatus
from app.domain.schemas import CandleSchema, ZoneSchema
from app.engine.aggregator import CandleAggregator
from app.engine.zone_detector import ZoneDetector
from app.engine.freshness import FreshnessEvaluator

logger = logging.getLogger("dhyanaksh.validated_sequence")


class ValidatedAchievementRecord(BaseModel):
    """
    Individual validated or rejected opposing supply break event.
    """
    timeframe: str
    active_demand_zone_fingerprint: str
    demand_zone_creation_timestamp: str
    opposing_supply_zone_fingerprint: str
    opposing_supply_creation_timestamp: str
    supply_proximal: float
    supply_distal: float
    first_breakout_timestamp: Optional[str] = None
    first_breakout_price: Optional[float] = None
    chronological_valid: bool = False
    breakout_confirmed: bool = False
    demand_still_valid: bool = False
    validation_status: str  # VALID, REJECTED_PRE_DEMAND, REJECTED_DUPLICATE, REJECTED_UNCONFIRMED, REJECTED_INVALID_DEMAND, REJECTED_TIMEFRAME_MISMATCH, REJECTED_UNBROKEN


class TimeframeValidatedAchievementSummary(BaseModel):
    """
    Per-timeframe summary of raw vs validated structural sequence breaks.
    """
    timeframe: str
    total_detected_supply_zones: int = 0
    raw_historical_broken_supply_count: int = 0
    validated_current_sequence_breaks: int = 0
    rejected_pre_demand_breaks: int = 0
    rejected_unbroken_supply: int = 0
    active_demand_zone_fingerprint: Optional[str] = None
    demand_zone_created_at: Optional[str] = None
    status: str = "VALID"  # VALID, NO_ACTIVE_DEMAND, DATA_INSUFFICIENT, NO_VALIDATED_BREAK
    rejection_distribution: Dict[str, int] = Field(default_factory=lambda: {
        "PRE_DEMAND": 0,
        "DUPLICATE": 0,
        "UNCONFIRMED": 0,
        "INVALID_DEMAND": 0,
        "UNBROKEN": 0,
        "TIMEFRAME_MISMATCH": 0,
        "NO_PROVENANCE": 0
    })
    validated_achievements: List[ValidatedAchievementRecord] = Field(default_factory=list)


class SymbolValidatedSequenceResult(BaseModel):
    """
    Complete multi-timeframe validated structural sequence result for an equity.
    """
    symbol: str
    status: str = "VALID"  # VALID, DATA_INSUFFICIENT, DATA_INVALID
    validated_sequence: Dict[str, TimeframeValidatedAchievementSummary] = Field(default_factory=dict)
    total_validated_breaks: int = 0
    total_raw_breaks: int = 0


def build_zone_fingerprint(zone: ZoneSchema) -> str:
    """
    Generates a deterministic unique fingerprint for a zone.
    """
    created_iso = zone.creation_timestamp.isoformat() if hasattr(zone.creation_timestamp, "isoformat") else str(zone.creation_timestamp)
    tf_val = zone.timeframe.value if hasattr(zone.timeframe, "value") else str(zone.timeframe)
    dir_val = zone.direction.value if hasattr(zone.direction, "value") else str(zone.direction)
    return f"{zone.symbol}|{tf_val}|{dir_val}|{created_iso}|{zone.proximal_price:.2f}|{zone.distal_price:.2f}"


def is_supply_broken_by_candle(candle: CandleSchema, supply_zone: ZoneSchema) -> bool:
    """
    CANONICAL CONFIRMED SUPPLY BREAK RULE (Stricter than ZoneDetector violation detection):
    A supply zone is CONFIRMED BROKEN by a candle if and only if:
        candle.close >= supply_zone.proximal_price

    This is intentionally stricter than the legacy ZoneDetector's violation rule
    (high >= proximal OR close >= distal), which detects zone penetration.
    A wick-only penetration (High >= Proximal, Close < Proximal) is a VIOLATION,
    not a confirmed structural break.
    """
    return candle.close >= supply_zone.proximal_price


class ValidatedAchievementEngine:
    """
    Evaluates chronological and structural validity of opposing supply breaks
    belonging strictly to the current active demand setup lifecycle across any NIFTY 500 security.
    """

    @classmethod
    def evaluate_timeframe_sequence(
        cls,
        timeframe: Timeframe,
        demand_zones: List[ZoneSchema],
        supply_zones: List[ZoneSchema],
        candles: List[CandleSchema],
        active_demand_zone: Optional[ZoneSchema] = None
    ) -> TimeframeValidatedAchievementSummary:
        """
        Executes strict sequence validation for a single isolated timeframe using the canonical break definition.
        """
        tf_str = timeframe.value if hasattr(timeframe, "value") else str(timeframe)
        summary = TimeframeValidatedAchievementSummary(timeframe=tf_str)

        # 1. Gate C & D: Isolate and ensure valid provenance
        tf_demand_zones = [z for z in demand_zones if (z.timeframe == timeframe or str(z.timeframe) == tf_str)]
        tf_supply_zones = [z for z in supply_zones if (z.timeframe == timeframe or str(z.timeframe) == tf_str)]
        tf_candles = [c for c in candles if (c.timeframe == timeframe or str(c.timeframe) == tf_str)]
        tf_candles.sort(key=lambda c: c.timestamp)

        if not tf_candles or len(tf_candles) < 3:
            summary.status = "DATA_INSUFFICIENT"
            return summary

        # 2. Deduplicate unique opposing supply zones by fingerprint
        unique_supplies: Dict[str, ZoneSchema] = {}
        for s in tf_supply_zones:
            fp = build_zone_fingerprint(s)
            if fp not in unique_supplies:
                unique_supplies[fp] = s
            else:
                summary.rejection_distribution["DUPLICATE"] += 1

        summary.total_detected_supply_zones = len(unique_supplies)

        # 3. Gate A: Active Demand Zone Existence
        if active_demand_zone is None:
            fresh_demands = [z for z in tf_demand_zones if z.freshness == FreshnessStatus.FRESH]
            if fresh_demands:
                fresh_demands.sort(key=lambda z: z.creation_timestamp, reverse=True)
                active_demand_zone = fresh_demands[0]

        # 4. First identify all supply zones ever confirmed broken in history (Population: Raw Historical Broken Supply)
        # Using the Canonical Confirmed Break Condition: candle.close >= s.proximal_price
        for s_fp, s_zone in unique_supplies.items():
            sub_c = [c for c in tf_candles if c.timestamp >= s_zone.creation_timestamp]
            first_break_c = next((c for c in sub_c if is_supply_broken_by_candle(c, s_zone)), None)

            if first_break_c is not None:
                summary.raw_historical_broken_supply_count += 1
            else:
                summary.rejected_unbroken_supply += 1
                summary.rejection_distribution["UNBROKEN"] += 1

        if active_demand_zone is None:
            summary.status = "NO_ACTIVE_DEMAND"
            summary.rejected_pre_demand_breaks = summary.raw_historical_broken_supply_count
            summary.rejection_distribution["PRE_DEMAND"] = summary.raw_historical_broken_supply_count
            return summary

        # 5. Gate G: Active Demand Zone Validity
        demand_is_valid = (active_demand_zone.freshness == FreshnessStatus.FRESH)
        demand_fp = build_zone_fingerprint(active_demand_zone)
        demand_created_dt = active_demand_zone.creation_timestamp
        demand_created_str = demand_created_dt.isoformat() if hasattr(demand_created_dt, "isoformat") else str(demand_created_dt)

        summary.active_demand_zone_fingerprint = demand_fp
        summary.demand_zone_created_at = demand_created_str

        if not demand_is_valid:
            summary.status = "NO_ACTIVE_DEMAND"
            summary.rejection_distribution["INVALID_DEMAND"] = summary.raw_historical_broken_supply_count
            summary.rejected_pre_demand_breaks = summary.raw_historical_broken_supply_count
            return summary

        # 6. Evaluate Candidate Supply Breaks against Active Demand Lifecycle
        for s_fp, s_zone in unique_supplies.items():
            sub_c = [c for c in tf_candles if c.timestamp >= s_zone.creation_timestamp]
            s_prox = s_zone.proximal_price
            s_dist = s_zone.distal_price
            s_created_str = s_zone.creation_timestamp.isoformat() if hasattr(s_zone.creation_timestamp, "isoformat") else str(s_zone.creation_timestamp)

            first_break_c = next((c for c in sub_c if is_supply_broken_by_candle(c, s_zone)), None)

            if first_break_c is None:
                # Supply never broken
                continue

            brk_ts = first_break_c.timestamp
            brk_ts_str = brk_ts.isoformat() if hasattr(brk_ts, "isoformat") else str(brk_ts)
            brk_price = float(first_break_c.close)

            # Gate B: Strict Chronological Validity (first breakout must occur >= demand creation)
            if brk_ts < demand_created_dt:
                summary.rejected_pre_demand_breaks += 1
                summary.rejection_distribution["PRE_DEMAND"] += 1
                record = ValidatedAchievementRecord(
                    timeframe=tf_str,
                    active_demand_zone_fingerprint=demand_fp,
                    demand_zone_creation_timestamp=demand_created_str,
                    opposing_supply_zone_fingerprint=s_fp,
                    opposing_supply_creation_timestamp=s_created_str,
                    supply_proximal=s_prox,
                    supply_distal=s_dist,
                    first_breakout_timestamp=brk_ts_str,
                    first_breakout_price=brk_price,
                    chronological_valid=False,
                    breakout_confirmed=False,
                    demand_still_valid=demand_is_valid,
                    validation_status="REJECTED_PRE_DEMAND"
                )
            else:
                # Gate F: Breakout confirmed under canonical rule
                summary.validated_current_sequence_breaks += 1
                record = ValidatedAchievementRecord(
                    timeframe=tf_str,
                    active_demand_zone_fingerprint=demand_fp,
                    demand_zone_creation_timestamp=demand_created_str,
                    opposing_supply_zone_fingerprint=s_fp,
                    opposing_supply_creation_timestamp=s_created_str,
                    supply_proximal=s_prox,
                    supply_distal=s_dist,
                    first_breakout_timestamp=brk_ts_str,
                    first_breakout_price=brk_price,
                    chronological_valid=True,
                    breakout_confirmed=True,
                    demand_still_valid=demand_is_valid,
                    validation_status="VALID"
                )
                summary.validated_achievements.append(record)

        if summary.validated_current_sequence_breaks == 0:
            summary.status = "NO_VALIDATED_BREAK"
        return summary

    @classmethod
    def evaluate_multi_timeframe_sequence(
        cls,
        timeframe_zones: Dict[str, List[ZoneSchema]],
        timeframe_candles: Dict[str, List[CandleSchema]],
        active_demand_zones: Optional[Dict[str, ZoneSchema]] = None
    ) -> Dict[str, TimeframeValidatedAchievementSummary]:
        """
        Evaluates sequence across all four primary timeframes (3M, 1M, 1W, 1D) with zero cross-contamination.
        """
        active_map = active_demand_zones or {}
        results = {}

        for tf_enum in [Timeframe.QUARTERLY, Timeframe.MONTHLY, Timeframe.WEEKLY, Timeframe.DAILY]:
            tf_key = tf_enum.value
            zones = timeframe_zones.get(tf_key, [])
            candles = timeframe_candles.get(tf_key, [])
            active_dz = active_map.get(tf_key)

            d_zones = [z for z in zones if z.direction == ZoneDirection.DEMAND]
            s_zones = [z for z in zones if z.direction == ZoneDirection.SUPPLY]

            summary = cls.evaluate_timeframe_sequence(
                timeframe=tf_enum,
                demand_zones=d_zones,
                supply_zones=s_zones,
                candles=candles,
                active_demand_zone=active_dz
            )
            results[tf_key] = summary

        return results

    @classmethod
    def evaluate_symbol_dataframe(
        cls,
        symbol: str,
        df: pd.DataFrame,
        detector: Optional[ZoneDetector] = None,
        aggregator: Optional[CandleAggregator] = None,
        freshness_evaluator: Optional[FreshnessEvaluator] = None
    ) -> SymbolValidatedSequenceResult:
        """
        Generic, symbol-agnostic endpoint to scan any historical equity dataframe.
        Executes multi-timeframe resampling, zone detection, and chronological sequence validation.
        """
        if df is None or df.empty or len(df) < 5:
            return SymbolValidatedSequenceResult(symbol=symbol, status="DATA_INSUFFICIENT")

        det = detector or ZoneDetector()
        agg = aggregator or CandleAggregator()
        fresh_eval = freshness_evaluator or FreshnessEvaluator()

        df_work = df.copy()
        df_work.columns = [c.lower() for c in df_work.columns]

        tf_zones = {}
        tf_candles = {}
        active_demands = {}

        for tf in [Timeframe.QUARTERLY, Timeframe.MONTHLY, Timeframe.WEEKLY, Timeframe.DAILY]:
            try:
                candles = agg.aggregate_from_df(df_work, tf, symbol)
                if len(candles) < 3:
                    continue
                raw_zones = det.detect_zones(candles)
                evaluated_zones = det.evaluate_zone_achievements(raw_zones, candles)
                fresh_zones = fresh_eval.filter_fresh_zones(evaluated_zones, candles)

                tf_zones[tf.value] = evaluated_zones
                tf_candles[tf.value] = candles

                fresh_demands = [z for z in fresh_zones if z.direction == ZoneDirection.DEMAND]
                if fresh_demands:
                    fresh_demands.sort(key=lambda z: z.creation_timestamp, reverse=True)
                    active_demands[tf.value] = fresh_demands[0]
            except Exception as e:
                logger.debug(f"Error processing {symbol} on {tf.value}: {e}")
                continue

        if not tf_candles:
            return SymbolValidatedSequenceResult(symbol=symbol, status="DATA_INVALID")

        sequence_summary = cls.evaluate_multi_timeframe_sequence(
            timeframe_zones=tf_zones,
            timeframe_candles=tf_candles,
            active_demand_zones=active_demands
        )

        tot_val = sum(s.validated_current_sequence_breaks for s in sequence_summary.values())
        tot_raw = sum(s.raw_historical_broken_supply_count for s in sequence_summary.values())

        return SymbolValidatedSequenceResult(
            symbol=symbol,
            status="VALID",
            validated_sequence=sequence_summary,
            total_validated_breaks=tot_val,
            total_raw_breaks=tot_raw
        )
