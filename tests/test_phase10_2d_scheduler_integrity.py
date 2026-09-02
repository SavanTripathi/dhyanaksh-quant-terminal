import pytest
import os
import json
import subprocess
import pandas as pd

LOCKED_CANDIDATE_HASH = "1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852"

def test_scheduler_installed_and_ready():
    """Verify Windows Task Scheduler task is registered and in Ready state."""
    result = subprocess.run(
        ["powershell", "-Command", "Get-ScheduledTask -TaskName 'Dhyanaksh_Prospective_Daily_Monitor' | Select-Object -ExpandProperty State"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Ready" in result.stdout

def test_idempotent_duplicate_protection():
    """Verify that running collector twice for the same date does not duplicate daily snapshots."""
    df_daily = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv")
    assert df_daily["date"].is_unique

def test_prospective_boundary_strictness():
    """Verify that all recorded prospective events strictly respect the prospective boundary."""
    df_events = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    for ts in df_events["timestamp"]:
        assert "2026-09" in ts or ts >= "2026-09-01"

def test_candidate_hash_unbroken():
    """Verify candidate hash is preserved across prospective records."""
    df_events = pd.read_csv("PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv")
    for h in df_events["candidate_hash"]:
        assert h == LOCKED_CANDIDATE_HASH
