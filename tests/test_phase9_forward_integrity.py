import pytest
import os
import json
import pandas as pd

def test_phase9_manifest_and_hash_integrity():
    """Verify manifest exists, is valid JSON, and matches locked candidate hash."""
    assert os.path.exists("V1.1_DEMANDCONF_MANIFEST.json")
    with open("V1.1_DEMANDCONF_MANIFEST.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    assert manifest["candidate_id"] == "Dhyanaksh-DemandConf-B-v1.1-research"
    assert manifest["candidate_hash"] == "1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852"
    assert manifest["directional_scope"] == "DEMAND_ONLY"
    assert manifest["live_broker_execution_enabled"] is False

def test_phase9_prospective_ledgers_isolation():
    """Verify that daily and event logging ledgers exist and are properly isolated."""
    assert os.path.exists("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    assert os.path.exists("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")
    assert os.path.exists("PAPER_TRADING_DAILY.csv")

    df_daily = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")
    assert "candidate_hash" in df_daily.columns
    assert len(df_daily) >= 1

def test_production_version_frozen():
    """Ensure production baseline v1.0.0 remains unmodified."""
    with open("STRATEGY_VERSION.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Dhyanaksh-HTF-SD-v1.0.0" in content
    assert "FROZEN FOR OBSERVATION" in content
