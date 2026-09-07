"""
Strict Freshness and Breach Evaluator adhering to GTF Methodology.

Methodology Rules:
1. Freshness (GTF PDF Page 34):
   - 0 prior tests -> FRESH (Score = 3.0)
   - 1 prior test -> TESTED (Score = 1.5)
   - 2+ prior tests -> TESTED (Score = 0.0)
   A test occurs when price returns to the zone by penetrating/touching the proximal boundary.
   A test does NOT destroy/invalidate the zone.

2. Breach (GTF PDF Page 24 - Closing Concepts):
   - Demand Zone: Candle CLOSE strictly below distal line (close < demand_distal) -> BREACHED.
   - Supply Zone: Candle CLOSE strictly above distal line (close > supply_distal) -> BREACHED.
   - Wick penetration beyond distal without closing beyond distal -> NOT BREACHED.
   - Proximal penetration -> TEST, NOT BREACH.
"""
from typing import List, Optional
from app.domain.enums import ZoneDirection, FreshnessStatus
from app.domain.schemas import CandleSchema, ZoneSchema


class FreshnessEvaluator:
    """
    Evaluates chronological zone interaction, test counts, and distal breach status.
    """

    @classmethod
    def evaluate_zone_freshness(
        cls,
        zone: ZoneSchema,
        subsequent_candles: List[CandleSchema]
    ) -> ZoneSchema:
        """
        Takes a detected zone and all candles occurring AFTER zone.creation_timestamp.
        Evaluates chronological tests and breach status.
        """
        # Filter candles strictly after creation
        after_candles = [c for c in subsequent_candles if c.timestamp > zone.creation_timestamp]
        after_candles.sort(key=lambda x: x.timestamp)

        retest_count = 0
        is_breached = False
        breach_timestamp = None
        penetration_timestamp = None
        in_test = False

        for candle in after_candles:
            if zone.direction == ZoneDirection.DEMAND:
                # 1. Breach check: Close strictly below distal line
                if candle.close < zone.distal_price:
                    is_breached = True
                    breach_timestamp = candle.timestamp
                    zone.freshness = FreshnessStatus.BREACHED
                    zone.is_breached = True
                    zone.breach_timestamp = breach_timestamp
                    zone.retest_count = retest_count
                    zone.penetration_timestamp = penetration_timestamp or candle.timestamp
                    return zone

                # 2. Test interaction check: Low touches or penetrates proximal line
                if candle.low <= zone.proximal_price:
                    if not in_test:
                        retest_count += 1
                        if penetration_timestamp is None:
                            penetration_timestamp = candle.timestamp
                        # If candle closed back above proximal, test completed within this candle
                        if candle.close > zone.proximal_price:
                            in_test = False
                        else:
                            in_test = True
                else:
                    # Price moved completely above proximal
                    in_test = False

            elif zone.direction == ZoneDirection.SUPPLY:
                # 1. Breach check: Close strictly above distal line
                if candle.close > zone.distal_price:
                    is_breached = True
                    breach_timestamp = candle.timestamp
                    zone.freshness = FreshnessStatus.BREACHED
                    zone.is_breached = True
                    zone.breach_timestamp = breach_timestamp
                    zone.retest_count = retest_count
                    zone.penetration_timestamp = penetration_timestamp or candle.timestamp
                    return zone

                # 2. Test interaction check: High touches or penetrates proximal line
                if candle.high >= zone.proximal_price:
                    if not in_test:
                        retest_count += 1
                        if penetration_timestamp is None:
                            penetration_timestamp = candle.timestamp
                        # If candle closed back below proximal, test completed within this candle
                        if candle.close < zone.proximal_price:
                            in_test = False
                        else:
                            in_test = True
                else:
                    # Price moved completely below proximal
                    in_test = False

        zone.is_breached = False
        zone.breach_timestamp = None
        zone.retest_count = retest_count
        zone.penetration_timestamp = penetration_timestamp

        if retest_count == 0:
            zone.freshness = FreshnessStatus.FRESH
        else:
            zone.freshness = FreshnessStatus.TESTED

        return zone

    @classmethod
    def filter_fresh_zones(
        cls,
        zones: List[ZoneSchema],
        candles: List[CandleSchema]
    ) -> List[ZoneSchema]:
        """
        Returns ONLY strictly untouched zones (0 tests, not breached).
        """
        fresh_zones: List[ZoneSchema] = []
        for zone in zones:
            evaluated = cls.evaluate_zone_freshness(zone, candles)
            if evaluated.freshness == FreshnessStatus.FRESH and evaluated.retest_count == 0 and not evaluated.is_breached:
                fresh_zones.append(evaluated)
        return fresh_zones

    @classmethod
    def filter_unbreached_zones(
        cls,
        zones: List[ZoneSchema],
        candles: List[CandleSchema]
    ) -> List[ZoneSchema]:
        """
        Returns all valid active zones that have NOT been breached (fresh or tested).
        """
        active_zones: List[ZoneSchema] = []
        for zone in zones:
            evaluated = cls.evaluate_zone_freshness(zone, candles)
            if not evaluated.is_breached:
                active_zones.append(evaluated)
        return active_zones
