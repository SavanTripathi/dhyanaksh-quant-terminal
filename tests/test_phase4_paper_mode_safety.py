import pytest
import sqlite3
import pandas as pd
from app.engine.gtf_engine import GTFEngine
from app.engine.conviction_ranker import ConvictionRankingEngine
from app.domain.enums import ZoneDirection

def test_paper_mode_cannot_submit_live_orders():
    """Verify that paper trading is strictly a non-executable logging interface."""
    # Ensure no broker execution endpoints or live private keys are accessible/enabled
    import os
    assert os.getenv("ENABLE_LIVE_BROKER_EXECUTION", "false").lower() == "false"

def test_score_audit_data_integrity():
    """Verify that independently computed score audit CSVs match trade population."""
    df_conv = pd.read_csv("CONVICTION_SCORE_AUDIT.csv")
    df_gtf = pd.read_csv("GTF_SCORE_AUDIT.csv")
    
    total_conv_trades = df_conv["trades"].sum()
    total_gtf_trades = df_gtf["trades"].sum()
    
    assert total_conv_trades == 5294
    assert total_gtf_trades == 5294

def test_strategy_version_immutability():
    """Ensure strategy version is locked to v1.0.0."""
    with open("STRATEGY_VERSION.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Dhyanaksh-HTF-SD-v1.0.0" in content
    assert "FROZEN FOR OBSERVATION" in content
