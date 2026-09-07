"""
Scanner Service Orchestrator.
Orchestrates:
1. Multi-timeframe aggregation from base candles (Quarterly, Monthly, Weekly, Daily, 125M, 75M)
2. Institutional zone detection on each timeframe
3. Strict freshness filter (untouched zones only)
4. Spatial Overlap Confluence Engine (Achievements > 1)
"""
from typing import List, Dict
import pandas as pd
from app.domain.enums import Timeframe
from app.domain.schemas import CandleSchema, ZoneSchema, SpatialOverlapCluster, ScanResponse
from app.engine.aggregator import CandleAggregator
from app.engine.zone_detector import ZoneDetector
from app.engine.freshness import FreshnessEvaluator
from app.engine.spatial_overlap import SpatialOverlapEngine


class ScannerPipeline:
    def __init__(self):
        self.detector = ZoneDetector()
        self.aggregator = CandleAggregator()
        self.freshness_evaluator = FreshnessEvaluator()
        self.spatial_engine = SpatialOverlapEngine()

    def run_scan_on_dataframe(
        self,
        symbol: str,
        df_intraday_or_daily: pd.DataFrame,
        timeframes: List[Timeframe] = None,
        min_achievements: int = 2
    ) -> ScanResponse:
        """
        Executes full MTF zone scan and confluence calculation.
        """
        if timeframes is None:
            timeframes = [
                Timeframe.QUARTERLY,
                Timeframe.MONTHLY,
                Timeframe.WEEKLY,
                Timeframe.DAILY,
                Timeframe.MIN_125,
                Timeframe.MIN_75
            ]

        all_detected_zones: List[ZoneSchema] = []
        all_fresh_zones: List[ZoneSchema] = []
        all_evaluated_zones: List[ZoneSchema] = []

        # 1. Aggregate and detect for each timeframe
        for tf in timeframes:
            try:
                tf_candles = self.aggregator.aggregate_from_df(df_intraday_or_daily, tf, symbol)
                if len(tf_candles) < 3:
                    continue

                # Detect zones
                detected = self.detector.detect_zones(tf_candles)
                # Evaluate achievements (e.g. Broken Opposing Supply)
                detected = self.detector.evaluate_zone_achievements(detected, tf_candles)
                all_detected_zones.extend(detected)

                # Strict Freshness evaluation & Breach analysis
                for z in detected:
                    eval_z = self.freshness_evaluator.evaluate_zone_freshness(z, tf_candles)
                    all_evaluated_zones.append(eval_z)
                    if eval_z.retest_count == 0 and not eval_z.is_breached:
                        all_fresh_zones.append(eval_z)

            except Exception as e:
                # E.g. intraday 75M requested on purely daily data
                continue

        # 2. Compute spatial overlap confluence (Achievements > 1)
        clusters = self.spatial_engine.find_confluence_clusters(
            zones=all_fresh_zones,
            min_achievements=min_achievements
        )

        tested_count = sum(1 for z in all_evaluated_zones if z.retest_count > 0 and not z.is_breached)
        breached_count = sum(1 for z in all_evaluated_zones if z.is_breached)

        return ScanResponse(
            symbol=symbol,
            total_zones_detected=len(all_evaluated_zones),
            fresh_zones_count=len(all_fresh_zones),
            tested_zones_count=tested_count,
            breached_zones_count=breached_count,
            clusters_count=len(clusters),
            clusters=clusters,
            all_zones=all_evaluated_zones
        )
