"""
Strict Fresh Spatial Overlap Confluence Engine.
Calculates 1D geometric intervals overlap between Multi-Timeframe zones.
Enforces Achievements > 1 (Tier 2 and Tier 3 institutional confluences).
"""
from typing import List, Dict
from app.domain.enums import Timeframe, ZoneDirection
from app.domain.schemas import ZoneSchema, SpatialOverlapCluster


class SpatialOverlapEngine:
    """
    Computes geometric spatial confluence of strictly fresh zones across:
    - HTF: Quarterly (3M), Monthly (1M), Weekly (1W)
    - Execution/Intermediate: Daily (1D), 125M, 75M

    Achievement Metric:
    - Number of distinct timeframes whose zones share a common non-empty price interval.
    - Achievements == 1: Single TF (discarded from Tier 2/3 pipeline)
    - Achievements == 2: Tier 2 Confluence (e.g. 1M + 1D or 1W + 125M)
    - Achievements >= 3: Tier 3 Strong Institutional Confluence (e.g. 1M + 1W + 1D)
    """

    # Timeframe weights for scoring
    TIMEFRAME_WEIGHTS: Dict[Timeframe, float] = {
        Timeframe.QUARTERLY: 4.0,
        Timeframe.MONTHLY: 3.5,
        Timeframe.WEEKLY: 2.5,
        Timeframe.DAILY: 1.5,
        Timeframe.MIN_125: 1.0,
        Timeframe.MIN_75: 0.8,
    }

    @classmethod
    def find_confluence_clusters(
        cls,
        zones: List[ZoneSchema],
        min_achievements: int = 2
    ) -> List[SpatialOverlapCluster]:
        """
        Groups fresh zones of the SAME symbol and SAME direction into overlapping price clusters.
        Filters for clusters where len(participating_timeframes) >= min_achievements.
        """
        if not zones:
            return []

        # Split by (symbol, direction)
        groups: Dict[tuple, List[ZoneSchema]] = {}
        for z in zones:
            key = (z.symbol, z.direction)
            groups.setdefault(key, []).append(z)

        clusters: List[SpatialOverlapCluster] = []

        for (sym, direction), group_zones in groups.items():
            # Cluster intervals
            found_clusters = cls._cluster_group(sym, direction, group_zones, min_achievements)
            clusters.extend(found_clusters)

        # Sort clusters by highest achievements, then highest cluster score
        return sorted(clusters, key=lambda c: (c.achievements, c.cluster_score), reverse=True)

    @classmethod
    def _cluster_group(
        cls,
        symbol: str,
        direction: ZoneDirection,
        zones: List[ZoneSchema],
        min_achievements: int
    ) -> List[SpatialOverlapCluster]:
        """
        Identifies all overlapping subsets of zones with distinct timeframes.
        """
        clusters: List[SpatialOverlapCluster] = []
        n = len(zones)
        if n < min_achievements:
            return []

        # Convert each zone to price interval [min_price, max_price]
        # For Demand: distal_price is bottom, proximal_price is top
        # For Supply: proximal_price is bottom, distal_price is top
        intervals = []
        for z in zones:
            low = min(z.proximal_price, z.distal_price)
            high = max(z.proximal_price, z.distal_price)
            intervals.append((low, high, z))

        # Check all combinations / seed intervals to find maximal overlaps
        visited_zone_sets = set()

        for i in range(n):
            current_low, current_high, seed_zone = intervals[i]
            cluster_zones = [seed_zone]
            overlap_low = current_low
            overlap_high = current_high

            for j in range(n):
                if i == j:
                    continue
                o_low, o_high, other_zone = intervals[j]
                
                # Check if other_zone overlaps with current intersection [overlap_low, overlap_high]
                new_overlap_low = max(overlap_low, o_low)
                new_overlap_high = min(overlap_high, o_high)

                if new_overlap_low < new_overlap_high:
                    # Valid intersection exists
                    overlap_low = new_overlap_low
                    overlap_high = new_overlap_high
                    cluster_zones.append(other_zone)

            # Extract distinct timeframes
            distinct_tfs = list(set([z.timeframe for z in cluster_zones]))
            achievements = len(distinct_tfs)

            if achievements >= min_achievements:
                # Key for deduplication: sorted zone timestamps + timeframes
                zone_signature = tuple(sorted([(z.timeframe.value, z.creation_timestamp.isoformat(), z.proximal_price) for z in cluster_zones]))
                if zone_signature not in visited_zone_sets:
                    visited_zone_sets.add(zone_signature)

                    # Calculate weighted cluster score
                    score = sum([cls.TIMEFRAME_WEIGHTS.get(tf, 1.0) for tf in distinct_tfs])

                    clusters.append(
                        SpatialOverlapCluster(
                            symbol=symbol,
                            direction=direction,
                            overlap_min_price=round(overlap_low, 2),
                            overlap_max_price=round(overlap_high, 2),
                            achievements=achievements,
                            participating_timeframes=sorted(distinct_tfs, key=lambda t: cls.TIMEFRAME_WEIGHTS.get(t, 0), reverse=True),
                            zones=cluster_zones,
                            is_fresh=True,
                            cluster_score=round(score, 2)
                        )
                    )

        return clusters
