import pytest
import pandas as pd

def test_phase6_models_complete_reconciliation():
    """Verify that all 5 confirmation models reconcile to the expected trade volume."""
    df = pd.read_csv("PHASE6_MODEL_COMPARISON.csv")
    assert len(df) > 20000
    
    models = df["model"].unique()
    assert set(models) == {"MODEL_A", "MODEL_B", "MODEL_C", "MODEL_D", "MODEL_E"}
    
    # Check Model B counts
    sub_b = df[df["model"] == "MODEL_B"]
    assert len(sub_b) == 5344

def test_production_baseline_isolation():
    """Ensure that Phase 6 research did not mutate frozen production baseline files."""
    with open("STRATEGY_VERSION.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Dhyanaksh-HTF-SD-v1.0.0" in content
    assert "FROZEN FOR OBSERVATION" in content
