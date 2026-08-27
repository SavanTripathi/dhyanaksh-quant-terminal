"""
Institutional Supply & Demand Zone Detection Engine.
Identifies:
- Demand Formations: DBR (Drop-Base-Rally), RBR (Rally-Base-Rally)
- Supply Formations: RBD (Rally-Base-Drop), DBD (Drop-Base-Drop)

Applies institutional scoring:
- Leg-In (ERC requirement)
- Basing structure (1 to MAX_BASE_CANDLES of NRC / consolidation)
- Leg-Out (Strong ERC departure)
- Precise calculation of Proximal Price and Distal Price
"""
from typing import List, Optional
from datetime import datetime
from app.domain.enums import Timeframe, ZoneDirection, ZoneStructure, CandleType
from app.domain.schemas import CandleSchema, ZoneSchema
from app.core.config import settings


class ZoneDetector:
    """
    Identifies institutional supply & demand zones across any timeframe.
    """

    def __init__(self, max_base_candles: int = settings.MAX_BASE_CANDLES):
        self.max_base_candles = max_base_candles

    def detect_zones(self, candles: List[CandleSchema]) -> List[ZoneSchema]:
        """
        Scans a sequence of chronologically sorted candles for institutional zones.
        """
        if len(candles) < 3:
            return []

        detected_zones: List[ZoneSchema] = []
        n = len(candles)

        # Iterate looking for basing sequences of length 1 to max_base_candles
        # Structure: Leg-In [i], Basing [i+1 ... i+k], Leg-Out [i+k+1]
        for base_len in range(1, self.max_base_candles + 1):
            for i in range(n - base_len - 1):
                leg_in = candles[i]
                basing_candles = candles[i + 1 : i + 1 + base_len]
                leg_out = candles[i + 1 + base_len]

                # Check Basing Candle quality: all basing candles should ideally be NRC or small range
                # Also verify Basing stays within a tight consolidation boundary
                if not self._is_valid_base(basing_candles):
                    continue

                # Check Demand formations: Leg-Out must be strong bullish ERC
                if self._is_bullish_erc(leg_out):
                    if self._is_bearish_erc(leg_in):
                        # DBR - Drop Base Rally
                        zone = self._construct_demand_zone(
                            symbol=leg_in.symbol,
                            timeframe=leg_in.timeframe,
                            structure=ZoneStructure.DBR,
                            leg_in=leg_in,
                            basing=basing_candles,
                            leg_out=leg_out
                        )
                        if zone:
                            detected_zones.append(zone)
                    elif self._is_bullish_erc(leg_in):
                        # RBR - Rally Base Rally
                        zone = self._construct_demand_zone(
                            symbol=leg_in.symbol,
                            timeframe=leg_in.timeframe,
                            structure=ZoneStructure.RBR,
                            leg_in=leg_in,
                            basing=basing_candles,
                            leg_out=leg_out
                        )
                        if zone:
                            detected_zones.append(zone)

                # Check Supply formations: Leg-Out must be strong bearish ERC
                elif self._is_bearish_erc(leg_out):
                    if self._is_bullish_erc(leg_in):
                        # RBD - Rally Base Drop
                        zone = self._construct_supply_zone(
                            symbol=leg_in.symbol,
                            timeframe=leg_in.timeframe,
                            structure=ZoneStructure.RBD,
                            leg_in=leg_in,
                            basing=basing_candles,
                            leg_out=leg_out
                        )
                        if zone:
                            detected_zones.append(zone)
                    elif self._is_bearish_erc(leg_in):
                        # DBD - Drop Base Drop
                        zone = self._construct_supply_zone(
                            symbol=leg_in.symbol,
                            timeframe=leg_in.timeframe,
                            structure=ZoneStructure.DBD,
                            leg_in=leg_in,
                            basing=basing_candles,
                            leg_out=leg_out
                        )
                        if zone:
                            detected_zones.append(zone)

        # Deduplicate overlapping/identical zones at same timestamp
        return self._deduplicate_zones(detected_zones)

    def _is_valid_base(self, basing_candles: List[CandleSchema]) -> bool:
        # A valid base has narrow range candles (mostly NRC)
        for c in basing_candles:
            if c.body_ratio is not None and c.body_ratio > 0.65:
                return False
        return True

    def _is_bullish_erc(self, candle: CandleSchema) -> bool:
        is_bullish = candle.close > candle.open
        is_erc = candle.candle_type == CandleType.ERC or (candle.body_ratio is not None and candle.body_ratio >= 0.50)
        return is_bullish and is_erc

    def _is_bearish_erc(self, candle: CandleSchema) -> bool:
        is_bearish = candle.close < candle.open
        is_erc = candle.candle_type == CandleType.ERC or (candle.body_ratio is not None and candle.body_ratio >= 0.50)
        return is_bearish and is_erc

    def _construct_demand_zone(
        self,
        symbol: str,
        timeframe: Timeframe,
        structure: ZoneStructure,
        leg_in: CandleSchema,
        basing: List[CandleSchema],
        leg_out: CandleSchema
    ) -> Optional[ZoneSchema]:
        """
        Standard Institutional Demand Zone:
        - Proximal Line: Highest body (open/close) of basing candles.
        - Distal Line: Lowest low among basing candles (and optional leg-in/leg-out origin).
        """
        basing_bodies = [max(c.open, c.close) for c in basing]
        basing_lows = [c.low for c in basing]

        proximal = max(basing_bodies)
        distal = min(basing_lows)

        # Sanity check: Proximal must be strictly above Distal
        if proximal <= distal:
            proximal = max([c.high for c in basing])
            if proximal <= distal:
                return None

        # Leg out must break above proximal
        if leg_out.close <= proximal:
            return None

        departure_strength = ((leg_out.close - proximal) / proximal) * 100.0

        return ZoneSchema(
            symbol=symbol,
            timeframe=timeframe,
            direction=ZoneDirection.DEMAND,
            structure=structure,
            proximal_price=round(proximal, 2),
            distal_price=round(distal, 2),
            creation_timestamp=leg_out.timestamp,
            base_candle_count=len(basing),
            leg_in_time=leg_in.timestamp,
            leg_out_time=leg_out.timestamp,
            departure_strength=round(departure_strength, 2)
        )

    def _construct_supply_zone(
        self,
        symbol: str,
        timeframe: Timeframe,
        structure: ZoneStructure,
        leg_in: CandleSchema,
        basing: List[CandleSchema],
        leg_out: CandleSchema
    ) -> Optional[ZoneSchema]:
        """
        Standard Institutional Supply Zone:
        - Proximal Line: Lowest body (open/close) of basing candles.
        - Distal Line: Highest high among basing candles.
        """
        basing_bodies = [min(c.open, c.close) for c in basing]
        basing_highs = [c.high for c in basing]

        proximal = min(basing_bodies)
        distal = max(basing_highs)

        # Sanity check: Distal must be strictly above Proximal
        if distal <= proximal:
            proximal = min([c.low for c in basing])
            if distal <= proximal:
                return None

        # Leg out must break below proximal
        if leg_out.close >= proximal:
            return None

        departure_strength = ((proximal - leg_out.close) / proximal) * 100.0

        return ZoneSchema(
            symbol=symbol,
            timeframe=timeframe,
            direction=ZoneDirection.SUPPLY,
            structure=structure,
            proximal_price=round(proximal, 2),
            distal_price=round(distal, 2),
            creation_timestamp=leg_out.timestamp,
            base_candle_count=len(basing),
            leg_in_time=leg_in.timestamp,
            leg_out_time=leg_out.timestamp,
            departure_strength=round(departure_strength, 2)
        )

    def _deduplicate_zones(self, zones: List[ZoneSchema]) -> List[ZoneSchema]:
        unique = {}
        for z in zones:
            key = (z.symbol, z.timeframe, z.direction, z.creation_timestamp, z.proximal_price, z.distal_price)
            if key not in unique:
                unique[key] = z
        return sorted(list(unique.values()), key=lambda x: x.creation_timestamp)

    def evaluate_zone_achievements(
        self,
        zones: List[ZoneSchema],
        all_candles: List[CandleSchema]
    ) -> List[ZoneSchema]:
        """
        Evaluates institutional achievements (GTF Achievement #1: Opposing Zone Violation).
        For Demand Zones: Checks if the rally originating from the zone subsequently broke & closed above a prior HTF Supply Zone.
        For Supply Zones: Checks if the drop originating from the zone subsequently broke & closed below a prior HTF Demand Zone.
        """
        if not zones or not all_candles:
            return zones

        # Separate demand and supply zones
        demand_zones = [z for z in zones if z.direction == ZoneDirection.DEMAND]
        supply_zones = [z for z in zones if z.direction == ZoneDirection.SUPPLY]

        # Evaluate Demand Zones breaking opposing Supply Zones
        for d_zone in demand_zones:
            # Subsequent candles after demand zone creation
            candles_after = [c for c in all_candles if c.timestamp >= d_zone.creation_timestamp]
            if not candles_after:
                continue
            highest_high = max([c.high for c in candles_after])
            highest_close = max([c.close for c in candles_after])

            # Prior opposing supply zones formed before or around this rally
            prior_supplies = [s for s in supply_zones if s.creation_timestamp <= d_zone.creation_timestamp or s.proximal_price > d_zone.proximal_price]
            for s_zone in prior_supplies:
                if s_zone.proximal_price > d_zone.proximal_price:
                    # If subsequent rally exceeded and violated the opposing supply zone
                    if highest_high >= s_zone.proximal_price or highest_close >= s_zone.distal_price:
                        d_zone.has_opposing_violation = True
                        d_zone.broken_supply_level = round(s_zone.proximal_price, 2)
                        break

        # Evaluate Supply Zones breaking opposing Demand Zones
        for s_zone in supply_zones:
            candles_after = [c for c in all_candles if c.timestamp >= s_zone.creation_timestamp]
            if not candles_after:
                continue
            lowest_low = min([c.low for c in candles_after])
            lowest_close = min([c.close for c in candles_after])

            prior_demands = [d for d in demand_zones if d.creation_timestamp <= s_zone.creation_timestamp or d.proximal_price < s_zone.proximal_price]
            for d_zone in prior_demands:
                if d_zone.proximal_price < s_zone.proximal_price:
                    if lowest_low <= d_zone.proximal_price or lowest_close <= d_zone.distal_price:
                        s_zone.has_opposing_violation = True
                        s_zone.broken_supply_level = round(d_zone.proximal_price, 2)
                        break

        return zones

