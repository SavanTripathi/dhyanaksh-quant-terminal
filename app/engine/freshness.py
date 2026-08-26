"""
Strict Freshness Evaluator.
Validates zone freshness against all subsequent price candles:
- Demand Zone: FRESH if no subsequent candle LOW touches or drops below proximal_price.
  (If low <= proximal_price, zone is tested/penetrated -> INVALIDATED / UNFRESH).
- Supply Zone: FRESH if no subsequent candle HIGH touches or breaches above proximal_price.
  (If high >= proximal_price, zone is tested/penetrated -> INVALIDATED / UNFRESH).
"""
from typing import List, Tuple
from app.domain.enums import ZoneDirection, FreshnessStatus
from app.domain.schemas import CandleSchema, ZoneSchema


class FreshnessEvaluator:
    """
    Applies strict institutional freshness rules:
    Only 100% untouched zones are marked FRESH.
    """

    @classmethod
    def evaluate_zone_freshness(
        cls,
        zone: ZoneSchema,
        subsequent_candles: List[CandleSchema]
    ) -> ZoneSchema:
        """
        Takes a detected zone and all candles occurring AFTER zone.creation_timestamp.
        Updates freshness status and sets penetration_timestamp if invalidated.
        """
        # Filter candles after creation
        after_candles = [c for c in subsequent_candles if c.timestamp > zone.creation_timestamp]
        after_candles.sort(key=lambda x: x.timestamp)

        for candle in after_candles:
            if zone.direction == ZoneDirection.DEMAND:
                # Demand zone is penetrated if candle low reaches proximal line
                if candle.low <= zone.proximal_price:
                    zone.freshness = FreshnessStatus.INVALIDATED
                    zone.penetration_timestamp = candle.timestamp
                    return zone
            elif zone.direction == ZoneDirection.SUPPLY:
                # Supply zone is penetrated if candle high reaches proximal line
                if candle.high >= zone.proximal_price:
                    zone.freshness = FreshnessStatus.INVALIDATED
                    zone.penetration_timestamp = candle.timestamp
                    return zone

        zone.freshness = FreshnessStatus.FRESH
        zone.penetration_timestamp = None
        return zone

    @classmethod
    def filter_fresh_zones(
        cls,
        zones: List[ZoneSchema],
        candles: List[CandleSchema]
    ) -> List[ZoneSchema]:
        """
        Evaluates a collection of zones against the candle dataset and returns ONLY strictly fresh zones.
        """
        fresh_zones: List[ZoneSchema] = []
        for zone in zones:
            evaluated = cls.evaluate_zone_freshness(zone, candles)
            if evaluated.freshness == FreshnessStatus.FRESH:
                fresh_zones.append(evaluated)
        return fresh_zones
