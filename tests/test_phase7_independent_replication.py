import pytest
import pandas as pd
import numpy as np

def test_phase7_raw_replication_integrity():
    """Verify that independent raw data replication generated full datasets with valid totals."""
    df_comp = pd.read_csv("PHASE7_MODEL_COMPARISON.csv")
    assert len(df_comp) == 5
    
    # Model B and Model E counts
    row_b = df_comp[df_comp["model"] == "MODEL_B"].iloc[0]
    row_e = df_comp[df_comp["model"] == "MODEL_E"].iloc[0]
    assert row_b["total_trades"] == 5344
    assert row_e["total_trades"] == 3976

def test_research_ledger_completeness():
    """Verify that all tested hypotheses are documented in the research ledger."""
    df_ledger = pd.read_csv("PHASE7_RESEARCH_LEDGER.csv")
    assert len(df_ledger) >= 5
    assert "H1: Blind Limits (Model A) have edge" in df_ledger["hypothesis"].values

def test_production_version_unmodified():
    """Ensure production baseline v1.0.0 remains frozen."""
    with open("STRATEGY_VERSION.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Dhyanaksh-HTF-SD-v1.0.0" in content
    assert "FROZEN FOR OBSERVATION" in content
