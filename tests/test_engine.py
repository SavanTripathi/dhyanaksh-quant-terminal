"""
Test suite for Step 1 components:
- Candle Aggregator
- Zone Detector
- Freshness Evaluator
- Spatial Overlap Engine (Achievements > 1)
"""
from datetime import datetime, timedelta
import pytest
import pandas as pd
from app.domain.enums import Timeframe, ZoneDirection, FreshnessStatus, ZoneStructure, CandleType
from app.domain.schemas import CandleSchema, ZoneSchema
from app.engine.aggregator import CandleAggregator
from app.engine.zone_detector import ZoneDetector
from app.engine.freshness import FreshnessEvaluator
from app.engine.spatial_overlap import SpatialOverlapEngine


def test_zone_detector_dbr_demand():
    """
    Test Drop-Base-Rally (DBR) Demand zone detection.
    """
    t0 = datetime(2026, 1, 1, 9, 15)
    
    # Leg-In (Bearish ERC): Open 100, Close 80 (Body 20, Range 20 -> Ratio 1.0)
    c1 = CandleSchema(
        timestamp=t0, symbol="NIFTY", timeframe=Timeframe.DAILY,
        open=100.0, high=100.0, low=80.0, close=80.0, volume=1000,
        candle_type=CandleType.ERC, body_ratio=1.0, body_range=20.0, total_range=20.0
    )
    # Basing Candle 1 (NRC): Open 81, Close 82, High 83, Low 79 (Body 1, Range 4 -> Ratio 0.25)
    c2 = CandleSchema(
        timestamp=t0 + timedelta(days=1), symbol="NIFTY", timeframe=Timeframe.DAILY,
        open=81.0, high=83.0, low=79.0, close=82.0, volume=500,
        candle_type=CandleType.NRC, body_ratio=0.25, body_range=1.0, total_range=4.0
    )
    # Leg-Out (Bullish ERC): Open 83, Close 110 (Body 27, Range 27 -> Ratio 1.0)
    c3 = CandleSchema(
        timestamp=t0 + timedelta(days=2), symbol="NIFTY", timeframe=Timeframe.DAILY,
        open=83.0, high=110.0, low=83.0, close=110.0, volume=2000,
        candle_type=CandleType.ERC, body_ratio=1.0, body_range=27.0, total_range=27.0
    )

    detector = ZoneDetector()
    zones = detector.detect_zones([c1, c2, c3])

    assert len(zones) == 1
    zone = zones[0]
    assert zone.direction == ZoneDirection.DEMAND
    assert zone.structure == ZoneStructure.DBR
    assert zone.proximal_price == 82.0  # Max body of base
    assert zone.distal_price == 79.0    # Lowest low of base
    assert zone.freshness == FreshnessStatus.FRESH


def test_freshness_evaluator_penetration():
    """
    Test strict freshness penetration check.
    """
    t0 = datetime(2026, 1, 1)
    zone = ZoneSchema(
        symbol="NIFTY",
        timeframe=Timeframe.DAILY,
        direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR,
        proximal_price=100.0,
        distal_price=90.0,
        freshness=FreshnessStatus.FRESH,
        creation_timestamp=t0,
        base_candle_count=1
    )

    # Subsequent candle 1: Low 105 (Untouched -> still FRESH)
    sc1 = CandleSchema(
        timestamp=t0 + timedelta(days=1), symbol="NIFTY", timeframe=Timeframe.DAILY,
        open=110.0, high=115.0, low=105.0, close=112.0
    )
    eval1 = FreshnessEvaluator.evaluate_zone_freshness(zone, [sc1])
    assert eval1.freshness == FreshnessStatus.FRESH

    # Subsequent candle 2: Low 99 (Penetrates proximal 100 -> INVALIDATED)
    sc2 = CandleSchema(
        timestamp=t0 + timedelta(days=2), symbol="NIFTY", timeframe=Timeframe.DAILY,
        open=108.0, high=110.0, low=99.0, close=102.0
    )
    eval2 = FreshnessEvaluator.evaluate_zone_freshness(zone, [sc1, sc2])
    assert eval2.freshness == FreshnessStatus.INVALIDATED
    assert eval2.penetration_timestamp == sc2.timestamp


def test_spatial_overlap_achievements_threshold():
    """
    Test spatial overlap engine enforcing Achievements > 1.
    """
    t0 = datetime(2026, 1, 1)

    # Monthly Zone: Demand [1000, 1050]
    z_monthly = ZoneSchema(
        symbol="RELIANCE", timeframe=Timeframe.MONTHLY, direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR, proximal_price=1050.0, distal_price=1000.0,
        creation_timestamp=t0, base_candle_count=2
    )

    # Weekly Zone: Demand [1020, 1060] (Overlaps [1020, 1050])
    z_weekly = ZoneSchema(
        symbol="RELIANCE", timeframe=Timeframe.WEEKLY, direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.RBR, proximal_price=1060.0, distal_price=1020.0,
        creation_timestamp=t0 + timedelta(days=5), base_candle_count=1
    )

    # Daily Zone: Demand [1030, 1045] (Overlaps [1030, 1045])
    z_daily = ZoneSchema(
        symbol="RELIANCE", timeframe=Timeframe.DAILY, direction=ZoneDirection.DEMAND,
        structure=ZoneStructure.DBR, proximal_price=1045.0, distal_price=1030.0,
        creation_timestamp=t0 + timedelta(days=10), base_candle_count=1
    )

    # 1. Confluence of all 3 -> Achievements = 3
    clusters = SpatialOverlapEngine.find_confluence_clusters(
        zones=[z_monthly, z_weekly, z_daily],
        min_achievements=2
    )
    assert len(clusters) >= 1
    assert clusters[0].achievements >= 2
    assert clusters[0].overlap_min_price >= 1000.0
    assert clusters[0].overlap_max_price <= 1060.0

    # 2. Single zone alone -> Achievements == 1 -> Must be discarded by filter
    single_clusters = SpatialOverlapEngine.find_confluence_clusters(
        zones=[z_monthly],
        min_achievements=2
    )
    assert len(single_clusters) == 0
