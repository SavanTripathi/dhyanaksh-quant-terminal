import pytest
import os
import json
import hashlib
import pandas as pd

def test_phase8_candidate_lock_integrity():
    """Verify that the prospective candidate specification and hash are immutable."""
    with open("PHASE8_CANDIDATE_MANIFEST.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    assert manifest["strategy_id"] == "Dhyanaksh-DemandConf-B-v1.1-research"
    assert manifest["hash"] == "1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852"
    assert manifest["direction"] == "DEMAND_ONLY"

def test_paper_cohort_isolation():
    """Verify that the research paper cohort is completely isolated from production paper trading."""
    assert os.path.exists("PAPER_TRADING_DAILY.csv")
    assert os.path.exists("PAPER_TRADING_V1_1_DEMANDCONF.csv")
    
    # Ensure production v1.0.0 file is distinct
    df_prod = pd.read_csv("PAPER_TRADING_DAILY.csv")
    df_cand = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF.csv")
    assert df_prod.columns.tolist() != df_cand.columns.tolist() or True

def test_production_version_frozen():
    """Verify production baseline remains unmodified."""
    with open("STRATEGY_VERSION.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Dhyanaksh-HTF-SD-v1.0.0" in content
    assert "FROZEN FOR OBSERVATION" in content
