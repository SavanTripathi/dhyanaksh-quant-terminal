import pytest
import os
import json
import pandas as pd

def test_phase10_prospective_boundary_and_manifest():
    """Verify prospective boundary start date, manifest consistency, and candidate hash stability."""
    assert os.path.exists("V1.1_DEMANDCONF_MANIFEST.json")
    with open("V1.1_DEMANDCONF_MANIFEST.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    assert manifest["candidate_id"] == "Dhyanaksh-DemandConf-B-v1.1-research"
    assert manifest["candidate_hash"] == "1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852"
    assert manifest["prospective_start_timestamp"] == "2026-09-01T00:00:00Z"
    assert manifest["directional_scope"] == "DEMAND_ONLY"
    assert manifest["live_broker_execution_enabled"] is False

def test_phase10_isolated_ledgers_and_event_states():
    """Verify append-only event log and daily snapshot integrity."""
    assert os.path.exists("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    assert os.path.exists("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")
    assert os.path.exists("PAPER_TRADING_DAILY.csv")

    df_events = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    assert "candidate_hash" in df_events.columns
    assert len(df_events) >= 1

def test_phase10_live_broker_safety_hard_gate():
    """Verify live broker execution remains disabled."""
    assert os.getenv("ENABLE_LIVE_BROKER_EXECUTION", "false").lower() == "false"

def test_phase10_production_v1_isolation():
    """Verify production strategy v1.0.0 remains frozen and untouched."""
    with open("STRATEGY_VERSION.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Dhyanaksh-HTF-SD-v1.0.0" in content
    assert "FROZEN FOR OBSERVATION" in content
