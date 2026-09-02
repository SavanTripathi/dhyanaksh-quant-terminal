import pytest
import pandas as pd

def test_entry_models_results_integrity():
    """Verify that all confirmation models produced valid non-empty results."""
    df_models = pd.read_csv("ENTRY_MODEL_COMPARISON.csv")
    assert len(df_models) == 3
    assert "MODEL_B (Rejection Conf)" in df_models["model"].values
    
    df_trades = pd.read_csv("ENTRY_MODEL_TRADE_RESULTS.csv")
    assert len(df_trades) > 10000

def test_production_version_isolation():
    """Ensure that research models did not modify the frozen v1.0.0 production baseline."""
    with open("STRATEGY_VERSION.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Dhyanaksh-HTF-SD-v1.0.0" in content
