"""
Automated unit and universe-level tests for Phase 2: Validated Achievement Sequence Engine.
Verifies:
1. Confirmed Break Rule: Close >= Proximal (NOT wick-touch High >= Proximal).
2. Zone Violation vs Confirmed Break distinction across 8 canonical cases.
3. First-Break Semantics: Wick-only penetration must NOT become first achievement.
4. ESCORTS 3M Forensic Recheck.
5. Mathematical invariants:
   - validated_current_sequence_breaks <= raw_historical_broken_supply_count
   - validated_current_sequence_breaks + rejected_pre_demand_breaks == raw_historical_broken_supply_count
   - raw_historical_broken_supply_count + rejected_unbroken_supply == total_detected_supply_zones
6. MARUTI special isolation: 13065.78 on 1W and 1D produces distinct fingerprints and independent state.
7. Dynamic NIFTY 500 universe orchestration & 100% Determinism.
"""
from datetime import datetime, timezone, timedelta
import pytest

from app.domain.enums import Timeframe, ZoneDirection, ZoneStructure, FreshnessStatus, CandleType
from app.domain.schemas import CandleSchema, ZoneSchema
from app.engine.universe import UniverseRepository
from app.engine.data_feed import generate_mock_nifty_data
from app.engine.validated_sequence import (
    ValidatedAchievementEngine, ValidatedAchievementRecord,
    TimeframeValidatedAchievementSummary, build_zone_fingerprint,
    SymbolValidatedSequenceResult, is_supply_broken_by_candle
)


def create_candle(symbol: str, tf: Timeframe, dt: datetime, o: float, h: float, l: float, c: float) -> CandleSchema:
    return CandleSchema(
        symbol=symbol,
        timeframe=tf,
        timestamp=dt,
        open=o,
        high=h,
        low=l,
        close=c,
        volume=1000.0,
        candle_type=CandleType.ERC if (c - o) / (h - l) >= 0.5 else CandleType.NRC,
        body_ratio=abs(c - o) / (h - l) if h > l else 1.0
    )


def create_zone(symbol: str, tf: Timeframe, direction: ZoneDirection, dt: datetime, prox: float, dist: float, fresh: FreshnessStatus = FreshnessStatus.FRESH) -> ZoneSchema:
    return ZoneSchema(
        symbol=symbol,
        timeframe=tf,
        direction=direction,
        structure=ZoneStructure.DBR if direction == ZoneDirection.DEMAND else ZoneStructure.RBD,
        proximal_price=prox,
        distal_price=dist,
        creation_timestamp=dt,
        base_candle_count=2,
        freshness=fresh,
        has_opposing_violation=True
    )


# ==============================================================================
# CASE A-F: ZONE VIOLATION vs CONFIRMED BREAK DISTINCTION
# ==============================================================================

def test_case_A_wick_penetration_only_not_confirmed_break():
    """
    Case A — Wick penetration only:
    High > Proximal, Close < Proximal, High < Distal
    zone_violation = TRUE, confirmed_break = FALSE
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 98.0, 102.0, 94.0, 95.0)
    # Wick touches zone but close is below proximal — NOT a confirmed break
    assert is_supply_broken_by_candle(c, s) is False


def test_case_B_close_through_proximal_confirmed_break():
    """
    Case B — Close through proximal:
    Close >= Proximal
    zone_violation = TRUE, confirmed_break = TRUE
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 95.0, 105.0, 94.0, 104.0)
    assert is_supply_broken_by_candle(c, s) is True


def test_case_C_high_reaches_distal_close_above_proximal():
    """
    Case C — High reaches distal, Close above proximal:
    confirmed_break = TRUE (Close >= Proximal)
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 95.0, 112.0, 94.0, 105.0)
    assert is_supply_broken_by_candle(c, s) is True


def test_case_D_close_reaches_distal():
    """
    Case D — Close reaches distal:
    Close >= Distal (which is >= Proximal) → confirmed_break = TRUE
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 95.0, 115.0, 94.0, 112.0)
    assert is_supply_broken_by_candle(c, s) is True


def test_case_E_no_penetration_not_broken():
    """
    Case E — No penetration at all:
    High < Proximal, Close < Proximal → confirmed_break = FALSE
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 90.0, 98.0, 88.0, 95.0)
    assert is_supply_broken_by_candle(c, s) is False


def test_case_F1_exact_equality_high_proximal_close_below():
    """
    Case F1 — High == Proximal, Close < Proximal:
    Wick touches exact boundary but close stays below → NOT confirmed break
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 90.0, 100.0, 89.0, 95.0)
    assert is_supply_broken_by_candle(c, s) is False


def test_case_F2_exact_equality_close_proximal():
    """
    Case F2 — Close == Proximal:
    Close exactly at proximal boundary → confirmed_break = TRUE (Close >= Proximal)
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 95.0, 105.0, 94.0, 100.0)
    assert is_supply_broken_by_candle(c, s) is True


def test_case_F3_exact_equality_close_distal():
    """
    Case F3 — Close == Distal:
    Close exactly at distal extreme → confirmed_break = TRUE (Close >= Proximal)
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 95.0, 115.0, 94.0, 110.0)
    assert is_supply_broken_by_candle(c, s) is True


def test_case_G1_high_exceeds_distal_close_below_proximal():
    """
    Case G1 — High exceeds distal, Close below proximal:
    High=112 > Distal=110, Close=98 < Proximal=100
    Complete intrabar penetration through the entire supply zone,
    but the candle closes below proximal.
    zone_violation = TRUE, confirmed_supply_break = FALSE, validated_achievement = FALSE
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 97.0, 112.0, 94.0, 98.0)
    assert is_supply_broken_by_candle(c, s) is False


def test_case_G2_high_equals_distal_close_below_proximal():
    """
    Case G2 — High == Distal, Close < Proximal:
    High=110 == Distal=110, Close=98 < Proximal=100
    Wick touches the extreme of the supply zone but close stays below proximal.
    zone_violation = TRUE, confirmed_supply_break = FALSE, validated_achievement = FALSE
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 97.0, 110.0, 94.0, 98.0)
    assert is_supply_broken_by_candle(c, s) is False


# ==============================================================================
# CRITICAL WICK-TOUCH TEST (User's Specific Test Case from Section 4)
# ==============================================================================

def test_critical_wick_touch_test():
    """
    The exact candle from the user's blocking finding:
    Proximal=100, Distal=110, Open=98, High=102, Low=94, Close=95.
    This candle enters the supply zone but closes below proximal.
    zone_violation = TRUE (wick), confirmed_supply_break = FALSE, validated_achievement = FALSE
    """
    s = create_zone("T", Timeframe.DAILY, ZoneDirection.SUPPLY, datetime(2026, 1, 1, tzinfo=timezone.utc), 100.0, 110.0)
    c = create_candle("T", Timeframe.DAILY, datetime(2026, 2, 1, tzinfo=timezone.utc), 98.0, 102.0, 94.0, 95.0)

    # Confirmed break: FALSE (Close 95 < Proximal 100)
    assert is_supply_broken_by_candle(c, s) is False

    # Full engine test: this supply must be UNBROKEN, not a validated achievement
    d_zone = create_zone("T", Timeframe.DAILY, ZoneDirection.DEMAND, datetime(2026, 1, 15, tzinfo=timezone.utc), 80.0, 70.0)
    c_pre = create_candle("T", Timeframe.DAILY, datetime(2026, 1, 15, tzinfo=timezone.utc), 75.0, 82.0, 74.0, 80.0)
    c_pre2 = create_candle("T", Timeframe.DAILY, datetime(2026, 1, 20, tzinfo=timezone.utc), 78.0, 84.0, 76.0, 82.0)

    summary = ValidatedAchievementEngine.evaluate_timeframe_sequence(
        timeframe=Timeframe.DAILY,
        demand_zones=[d_zone],
        supply_zones=[s],
        candles=[c_pre, c_pre2, c],
        active_demand_zone=d_zone
    )
    assert summary.validated_current_sequence_breaks == 0
    assert summary.rejected_unbroken_supply == 1
    assert summary.raw_historical_broken_supply_count == 0


# ==============================================================================
# FIRST-BREAK SEMANTICS TEST
# ==============================================================================

def test_first_break_semantics_wick_then_close():
    """
    First-Break Semantics:
    Candle 1: High=102, Close=95 → Wick penetration only (NOT first break)
    Candle 2: High=108, Close=104 → FIRST CONFIRMED BREAK (Close >= Proximal)
    The first achievement timestamp must be Candle 2, not Candle 1.
    """
    t0 = datetime(2025, 12, 1, tzinfo=timezone.utc)
    t_demand = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 2, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 3, 1, tzinfo=timezone.utc)

    s_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.SUPPLY, t0, 100.0, 110.0)
    d_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.DEMAND, t_demand, 80.0, 70.0)

    c_pre = create_candle("TEST", Timeframe.DAILY, t_demand, 75.0, 82.0, 74.0, 80.0)
    c1_wick = create_candle("TEST", Timeframe.DAILY, t1, 98.0, 102.0, 94.0, 95.0)  # Wick only
    c2_break = create_candle("TEST", Timeframe.DAILY, t2, 98.0, 108.0, 97.0, 104.0)  # Confirmed break

    summary = ValidatedAchievementEngine.evaluate_timeframe_sequence(
        timeframe=Timeframe.DAILY,
        demand_zones=[d_zone],
        supply_zones=[s_zone],
        candles=[c_pre, c1_wick, c2_break],
        active_demand_zone=d_zone
    )

    assert summary.validated_current_sequence_breaks == 1
    assert summary.raw_historical_broken_supply_count == 1
    assert len(summary.validated_achievements) == 1

    # The first break timestamp must be Candle 2, NOT Candle 1
    first_break_ts = summary.validated_achievements[0].first_breakout_timestamp
    assert first_break_ts == t2.isoformat()


# ==============================================================================
# ESCORTS 3M FORENSIC RECHECK
# ==============================================================================

def test_escorts_3m_forensic_recheck():
    """
    ESCORTS 3M Supply Break Forensic Recheck:
    Supply: Created 2022-12-31, Proximal=2064.70, Distal=2282.83
    Break Candle: 2023-06-30, O=1834.66, H=2194.53, L=1772.85, C=2183.36
    Close=2183.36 >= Proximal=2064.70 → CONFIRMED BREAK
    """
    t_supply = datetime(2022, 12, 31, tzinfo=timezone.utc)
    t_demand = datetime(2023, 3, 31, tzinfo=timezone.utc)
    t_break = datetime(2023, 6, 30, tzinfo=timezone.utc)

    s_zone = create_zone("ESCORTS", Timeframe.QUARTERLY, ZoneDirection.SUPPLY, t_supply, 2064.70, 2282.83)
    d_zone = create_zone("ESCORTS", Timeframe.QUARTERLY, ZoneDirection.DEMAND, t_demand, 1900.0, 1750.0)

    c_early = create_candle("ESCORTS", Timeframe.QUARTERLY, t_supply, 1700.0, 1800.0, 1650.0, 1750.0)
    c_pre = create_candle("ESCORTS", Timeframe.QUARTERLY, t_demand, 1800.0, 1950.0, 1750.0, 1900.0)
    c_break = create_candle("ESCORTS", Timeframe.QUARTERLY, t_break, 1834.66, 2194.53, 1772.85, 2183.36)

    # Unit-level: confirmed break
    assert is_supply_broken_by_candle(c_break, s_zone) is True

    # Full engine test
    summary = ValidatedAchievementEngine.evaluate_timeframe_sequence(
        timeframe=Timeframe.QUARTERLY,
        demand_zones=[d_zone],
        supply_zones=[s_zone],
        candles=[c_early, c_pre, c_break],
        active_demand_zone=d_zone
    )

    assert summary.validated_current_sequence_breaks == 1
    assert summary.raw_historical_broken_supply_count == 1
    assert summary.rejected_unbroken_supply == 0
    assert len(summary.validated_achievements) == 1
    assert summary.validated_achievements[0].first_breakout_timestamp == t_break.isoformat()
    assert summary.validated_achievements[0].validation_status == "VALID"


# ==============================================================================
# DEDUPLICATION TEST
# ==============================================================================

def test_multiple_candles_after_first_break_deduplicated():
    """Same supply broken across multiple candles → Exactly 1 count credited"""
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 2, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 3, 1, tzinfo=timezone.utc)
    t3 = datetime(2026, 3, 2, tzinfo=timezone.utc)
    t4 = datetime(2026, 3, 3, tzinfo=timezone.utc)

    s_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.SUPPLY, t0, 100.0, 110.0)
    d_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.DEMAND, t1, 80.0, 70.0)
    c1 = create_candle("TEST", Timeframe.DAILY, t1, 75.0, 82.0, 74.0, 80.0)
    c2 = create_candle("TEST", Timeframe.DAILY, t2, 98.0, 105.0, 97.0, 103.0)  # Close=103 >= Prox=100: BREAK
    c3 = create_candle("TEST", Timeframe.DAILY, t3, 103.0, 108.0, 102.0, 107.0)  # Also break, but already counted
    c4 = create_candle("TEST", Timeframe.DAILY, t4, 107.0, 112.0, 106.0, 111.0)  # Also break

    summary = ValidatedAchievementEngine.evaluate_timeframe_sequence(
        timeframe=Timeframe.DAILY,
        demand_zones=[d_zone],
        supply_zones=[s_zone, s_zone],
        candles=[c1, c2, c3, c4],
        active_demand_zone=d_zone
    )

    assert summary.validated_current_sequence_breaks == 1
    assert summary.raw_historical_broken_supply_count == 1
    assert summary.rejection_distribution["DUPLICATE"] == 1


# ==============================================================================
# PRE-DEMAND REJECTION TEST
# ==============================================================================

def test_supply_broken_before_demand_formation_rejected():
    """Supply first confirmed broken prior to demand formation → REJECTED_PRE_DEMAND"""
    t0 = datetime(2025, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2025, 3, 1, tzinfo=timezone.utc)
    t2 = datetime(2025, 6, 1, tzinfo=timezone.utc)
    t3 = datetime(2025, 6, 2, tzinfo=timezone.utc)

    s_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.SUPPLY, t0, 100.0, 110.0)
    c1 = create_candle("TEST", Timeframe.DAILY, t1, 95.0, 105.0, 94.0, 104.0)  # Close=104 >= Prox=100: BREAK in March
    d_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.DEMAND, t2, 90.0, 80.0)  # Formed June
    c2 = create_candle("TEST", Timeframe.DAILY, t2, 90.0, 95.0, 85.0, 94.0)
    c3 = create_candle("TEST", Timeframe.DAILY, t3, 94.0, 96.0, 91.0, 95.0)

    summary = ValidatedAchievementEngine.evaluate_timeframe_sequence(
        timeframe=Timeframe.DAILY,
        demand_zones=[d_zone],
        supply_zones=[s_zone],
        candles=[c1, c2, c3],
        active_demand_zone=d_zone
    )

    assert summary.validated_current_sequence_breaks == 0
    assert summary.raw_historical_broken_supply_count == 1
    assert summary.rejected_pre_demand_breaks == 1
    assert summary.validated_current_sequence_breaks <= summary.raw_historical_broken_supply_count


# ==============================================================================
# SUPPLY NEVER BROKEN TEST
# ==============================================================================

def test_supply_never_broken():
    """Supply never confirmed broken (all closes below proximal) → UNBROKEN"""
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 2, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 3, 1, tzinfo=timezone.utc)
    t3 = datetime(2026, 3, 2, tzinfo=timezone.utc)

    s_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.SUPPLY, t0, 100.0, 110.0)
    d_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.DEMAND, t1, 80.0, 70.0)
    c1 = create_candle("TEST", Timeframe.DAILY, t1, 75.0, 82.0, 74.0, 80.0)
    c2 = create_candle("TEST", Timeframe.DAILY, t2, 85.0, 95.0, 84.0, 92.0)
    c3 = create_candle("TEST", Timeframe.DAILY, t3, 91.0, 98.0, 88.0, 90.0)

    summary = ValidatedAchievementEngine.evaluate_timeframe_sequence(
        timeframe=Timeframe.DAILY,
        demand_zones=[d_zone],
        supply_zones=[s_zone],
        candles=[c1, c2, c3],
        active_demand_zone=d_zone
    )

    assert summary.validated_current_sequence_breaks == 0
    assert summary.raw_historical_broken_supply_count == 0
    assert summary.rejected_unbroken_supply == 1
    assert summary.total_detected_supply_zones == 1


def test_wick_above_proximal_close_below_is_unbroken():
    """
    Supply with wick above proximal but ALL closes below proximal → UNBROKEN.
    This is the critical distinction: wick penetration ≠ confirmed break.
    """
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 2, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 3, 1, tzinfo=timezone.utc)
    t3 = datetime(2026, 3, 2, tzinfo=timezone.utc)

    s_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.SUPPLY, t0, 100.0, 110.0)
    d_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.DEMAND, t1, 80.0, 70.0)
    c1 = create_candle("TEST", Timeframe.DAILY, t1, 75.0, 82.0, 74.0, 80.0)
    # Multiple wick-only penetrations — all closes below proximal
    c2 = create_candle("TEST", Timeframe.DAILY, t2, 95.0, 103.0, 94.0, 97.0)   # H=103 > P=100, C=97 < P
    c3 = create_candle("TEST", Timeframe.DAILY, t3, 96.0, 105.0, 93.0, 98.0)   # H=105 > P=100, C=98 < P

    summary = ValidatedAchievementEngine.evaluate_timeframe_sequence(
        timeframe=Timeframe.DAILY,
        demand_zones=[d_zone],
        supply_zones=[s_zone],
        candles=[c1, c2, c3],
        active_demand_zone=d_zone
    )

    assert summary.validated_current_sequence_breaks == 0
    assert summary.raw_historical_broken_supply_count == 0
    assert summary.rejected_unbroken_supply == 1


# ==============================================================================
# CONSERVATION INVARIANTS TEST
# ==============================================================================

def test_conservation_invariants_multi_supply():
    """
    Multi-supply conservation test:
    S1: Broken before demand (PRE_DEMAND)
    S2: Broken after demand (VALID)
    S3: Never broken (UNBROKEN)
    All three invariants must hold.
    """
    t0 = datetime(2025, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2025, 3, 1, tzinfo=timezone.utc)
    t_demand = datetime(2025, 6, 1, tzinfo=timezone.utc)
    t3 = datetime(2025, 9, 1, tzinfo=timezone.utc)
    t4 = datetime(2025, 10, 1, tzinfo=timezone.utc)

    s1 = create_zone("TEST", Timeframe.DAILY, ZoneDirection.SUPPLY, t0, 100.0, 110.0)
    s2 = create_zone("TEST", Timeframe.DAILY, ZoneDirection.SUPPLY, t0, 120.0, 130.0)
    s3 = create_zone("TEST", Timeframe.DAILY, ZoneDirection.SUPPLY, t0, 150.0, 160.0)
    d_zone = create_zone("TEST", Timeframe.DAILY, ZoneDirection.DEMAND, t_demand, 80.0, 70.0)

    c0 = create_candle("TEST", Timeframe.DAILY, t0, 90.0, 95.0, 85.0, 90.0)
    c1 = create_candle("TEST", Timeframe.DAILY, t1, 95.0, 105.0, 94.0, 104.0)   # Breaks S1 (pre-demand)
    c2 = create_candle("TEST", Timeframe.DAILY, t_demand, 80.0, 85.0, 75.0, 82.0)
    c3 = create_candle("TEST", Timeframe.DAILY, t3, 115.0, 128.0, 114.0, 125.0)  # Breaks S2 (post-demand)
    c4 = create_candle("TEST", Timeframe.DAILY, t4, 125.0, 140.0, 124.0, 135.0)  # Not enough for S3 (Close 135 < 150)

    summary = ValidatedAchievementEngine.evaluate_timeframe_sequence(
        timeframe=Timeframe.DAILY,
        demand_zones=[d_zone],
        supply_zones=[s1, s2, s3],
        candles=[c0, c1, c2, c3, c4],
        active_demand_zone=d_zone
    )

    # Invariant 1: validated <= raw
    assert summary.validated_current_sequence_breaks <= summary.raw_historical_broken_supply_count
    # Invariant 2: validated + pre_demand == raw
    assert summary.validated_current_sequence_breaks + summary.rejected_pre_demand_breaks == summary.raw_historical_broken_supply_count
    # Invariant 3: raw + unbroken == total
    assert summary.raw_historical_broken_supply_count + summary.rejected_unbroken_supply == summary.total_detected_supply_zones

    # Specific expected values
    assert summary.total_detected_supply_zones == 3
    assert summary.raw_historical_broken_supply_count == 2  # S1 + S2
    assert summary.validated_current_sequence_breaks == 1   # S2 only
    assert summary.rejected_pre_demand_breaks == 1          # S1
    assert summary.rejected_unbroken_supply == 1            # S3


# ==============================================================================
# MARUTI TIMEFRAME ISOLATION TEST
# ==============================================================================

def test_maruti_identical_coordinates_different_timeframes():
    """
    MARUTI Special Isolation:
    Identical price coordinates (13065.78) on 1W and 1D have different zone fingerprints
    and do NOT cause duplicate counting or cross-timeframe contamination.
    """
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 2, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 3, 1, tzinfo=timezone.utc)
    t3 = datetime(2026, 3, 8, tzinfo=timezone.utc)

    s_zone_1w = create_zone("MARUTI", Timeframe.WEEKLY, ZoneDirection.SUPPLY, t0, 14000.0, 13065.78)
    d_zone_1w = create_zone("MARUTI", Timeframe.WEEKLY, ZoneDirection.DEMAND, t1, 13686.55, 13065.78)
    c_1w_1 = create_candle("MARUTI", Timeframe.WEEKLY, t1, 13000.0, 13700.0, 12900.0, 13600.0)
    c_1w_2 = create_candle("MARUTI", Timeframe.WEEKLY, t2, 13500.0, 14200.0, 13400.0, 14100.0)  # Close=14100 >= Prox=14000: BREAK
    c_1w_3 = create_candle("MARUTI", Timeframe.WEEKLY, t3, 14000.0, 14500.0, 13900.0, 14300.0)

    s_zone_1d = create_zone("MARUTI", Timeframe.DAILY, ZoneDirection.SUPPLY, t0, 13500.0, 13065.78)
    d_zone_1d = create_zone("MARUTI", Timeframe.DAILY, ZoneDirection.DEMAND, t1, 13308.34, 13065.78)
    c_1d_1 = create_candle("MARUTI", Timeframe.DAILY, t1, 13000.0, 13400.0, 12900.0, 13300.0)
    c_1d_2 = create_candle("MARUTI", Timeframe.DAILY, t2, 13200.0, 13700.0, 13100.0, 13650.0)  # Close=13650 >= Prox=13500: BREAK
    c_1d_3 = create_candle("MARUTI", Timeframe.DAILY, t3, 13600.0, 13800.0, 13500.0, 13750.0)

    tf_zones = {
        "1W": [s_zone_1w, d_zone_1w],
        "1D": [s_zone_1d, d_zone_1d]
    }
    tf_candles = {
        "1W": [c_1w_1, c_1w_2, c_1w_3],
        "1D": [c_1d_1, c_1d_2, c_1d_3]
    }
    active_dz = {
        "1W": d_zone_1w,
        "1D": d_zone_1d
    }

    results = ValidatedAchievementEngine.evaluate_multi_timeframe_sequence(
        timeframe_zones=tf_zones,
        timeframe_candles=tf_candles,
        active_demand_zones=active_dz
    )

    fp_1w = build_zone_fingerprint(s_zone_1w)
    fp_1d = build_zone_fingerprint(s_zone_1d)
    assert fp_1w != fp_1d

    assert results["1W"].validated_current_sequence_breaks == 1
    assert results["1D"].validated_current_sequence_breaks == 1
    assert results["1W"].validated_current_sequence_breaks <= results["1W"].raw_historical_broken_supply_count
    assert results["1D"].validated_current_sequence_breaks <= results["1D"].raw_historical_broken_supply_count
    assert results["1W"].validated_achievements[0].opposing_supply_zone_fingerprint == fp_1w
    assert results["1D"].validated_achievements[0].opposing_supply_zone_fingerprint == fp_1d


# ==============================================================================
# DYNAMIC UNIVERSE ORCHESTRATION & DETERMINISM TEST
# ==============================================================================

def test_dynamic_universe_orchestration_and_determinism():
    """
    Universe Test: Evaluates dynamic batch orchestration across multiple symbols
    and confirms 100% determinism (Run 1 == Run 2 on identical datasets).
    """
    symbols = ["RELIANCE", "TCS", "INFY", "ITC", "BHARTIARTL", "SBIN", "LT", "ICICIBANK"]
    data_map = {sym: generate_mock_nifty_data(sym, days=120) for sym in symbols}

    run1 = {}
    for sym in symbols:
        res1 = ValidatedAchievementEngine.evaluate_symbol_dataframe(sym, data_map[sym])
        run1[sym] = res1
        assert res1.status in ["VALID", "DATA_INSUFFICIENT", "NO_ACTIVE_DEMAND"]
        for tf, s in res1.validated_sequence.items():
            assert s.validated_current_sequence_breaks <= s.raw_historical_broken_supply_count
            assert s.validated_current_sequence_breaks + s.rejected_pre_demand_breaks == s.raw_historical_broken_supply_count
            assert s.raw_historical_broken_supply_count + s.rejected_unbroken_supply == s.total_detected_supply_zones

    run2 = {}
    for sym in symbols:
        res2 = ValidatedAchievementEngine.evaluate_symbol_dataframe(sym, data_map[sym])
        run2[sym] = res2

    for sym in symbols:
        d1 = run1[sym].model_dump()
        d2 = run2[sym].model_dump()
        assert d1 == d2, f"Determinism failure for {sym}"
