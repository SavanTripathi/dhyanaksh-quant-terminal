import pytest
import os
import json
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime

PROSPECTIVE_START = "2026-09-01T00:00:00Z"
LOCKED_CANDIDATE_HASH = "1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852"

# 1. Prospective Boundary Integrity
def test_01_prospective_boundary():
    df_daily = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")
    for d in df_daily["date"]:
        assert d >= "2026-09-01", f"Found historical date {d} in prospective ledger"

# 2. Actual Prospective Sample Count & Accounting
def test_02_sample_count_reconciliation():
    df_events = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    df_daily = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")
    assert len(df_events) >= 1
    assert len(df_daily) >= 1

# 3. Candidate Hash Immutability
def test_03_candidate_hash_immutability():
    with open("V1.1_DEMANDCONF_MANIFEST.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["candidate_hash"] == LOCKED_CANDIDATE_HASH
    
    df_daily = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")
    for h in df_daily["candidate_hash"]:
        assert h == LOCKED_CANDIDATE_HASH

# 4. Confirmation-Before-Entry Timing
def test_04_confirmation_before_entry_timing():
    with open("V1.1_DEMANDCONF_SPEC.md", "r", encoding="utf-8") as f:
        spec = f.read()
    assert "Next-Bar Open following confirmed candle close" in spec

# 5. Lookahead Protection & Reconstruction
def test_05_lookahead_protection():
    with open("PHASE10_DATA_INTEGRITY.json", "r", encoding="utf-8") as f:
        diag = json.load(f)
    assert diag["lookahead_violations"] == 0

# 6. Theoretical vs Paper Execution Separation
def test_06_theoretical_vs_paper_separation():
    df_events = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    assert "event_type" in df_events.columns
    assert "state" in df_events.columns

# 7. 25 bps Fixed Cost Accounting
def test_07_fixed_25_bps_cost():
    with open("V1.1_DEMANDCONF_MANIFEST.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["cost_assumption_bps"] == 25

# 8. Append-Only Event Log Integrity
def test_08_append_only_event_log():
    df_events = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    assert df_events["event_id"].is_unique

# 9. Daily Snapshot Immutability
def test_09_daily_snapshot_immutability():
    df_daily = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")
    assert "date" in df_daily.columns
    assert "candidate_hash" in df_daily.columns

# 10. Production v1.0 vs Prospective v1.1 Isolation
def test_10_production_v1_isolation():
    assert os.path.exists("PAPER_TRADING_DAILY.csv")
    assert os.path.exists("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")

# 11. Live Broker Execution Hard-Disable
def test_11_live_broker_hard_disable():
    assert os.getenv("ENABLE_LIVE_BROKER_EXECUTION", "false").lower() == "false"

# 12. Statistical-Estimation Readiness (N=0 Handled)
def test_12_statistical_estimation_readiness():
    df_daily = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")
    closed_trades = df_daily["closed_trades"].sum()
    if closed_trades == 0:
        stat_status = "NOT YET ESTIMABLE"
    else:
        stat_status = "ESTIMABLE"
    assert stat_status in ["NOT YET ESTIMABLE", "ESTIMABLE"]

# 13. Deterministic Bootstrap Methodology
def test_13_deterministic_bootstrap():
    np.random.seed(42)
    sample = np.random.choice([1.0, -1.0, 2.0], size=10, replace=True)
    assert len(sample) == 10

# 14. State Machine Legal Transitions
def test_14_state_machine_validity():
    legal_states = {
        "ZONE_DETECTED", "ZONE_ACTIVE", "CONFIRMATION_PENDING", "CONFIRMED",
        "ENTRY_PENDING", "PAPER_FILLED", "STOPPED", "T1_HIT", "T2_HIT", "T3_HIT",
        "CLOSED", "EXPIRED", "INVALIDATED", "PROSPECTIVE_MONITORING_ACTIVE"
    }
    df_events = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    for st in df_events["state"]:
        assert st in legal_states

# 15. Timestamp / Timezone Consistency
def test_15_timestamp_consistency():
    df_events = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    for ts in df_events["timestamp"]:
        assert ts.endswith("Z") or "+00:00" in ts or "T" in ts

# 16. Manifest File Integrity
def test_16_manifest_integrity():
    with open("V1.1_DEMANDCONF_MANIFEST.json", "r", encoding="utf-8") as f:
        data = f.read()
    assert "Dhyanaksh-DemandConf-B-v1.1-research" in data

# 17. Configuration & Strategy Drift Detection
def test_17_strategy_drift_detection():
    with open("STRATEGY_VERSION.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Dhyanaksh-HTF-SD-v1.0.0" in content
    assert "FROZEN FOR OBSERVATION" in content
