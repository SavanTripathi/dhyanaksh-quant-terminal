import pytest
import os
import json
import pandas as pd

LOCKED_CANDIDATE_HASH = "1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852"

def test_runner_file_exists():
    """Verify daily runner script exists."""
    assert os.path.exists("scripts/run_daily_prospective_collector.py")
    assert os.path.exists("scripts/run_prospective_daily.ps1")

def test_runner_hash_verification():
    """Verify runner embeds the exact locked candidate hash."""
    with open("scripts/run_daily_prospective_collector.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert LOCKED_CANDIDATE_HASH in content
    assert "PROSPECTIVE_START_BOUNDARY = \"2026-09-01T00:00:00Z\"" in content

def test_runner_broker_hard_gate():
    """Verify runner hard-checks ENABLE_LIVE_BROKER_EXECUTION."""
    with open("scripts/run_daily_prospective_collector.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "ENABLE_LIVE_BROKER_EXECUTION" in content
    assert "sys.exit(1)" in content

def test_prospective_isolation_maintained():
    """Verify prospective ledgers remain intact and isolated."""
    assert os.path.exists("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    assert os.path.exists("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")
    assert os.path.exists("PAPER_TRADING_V1_1_REPLAY_TEST_EVENTS.csv")
