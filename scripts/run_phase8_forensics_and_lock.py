import os
import json
import sqlite3
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime

def run_phase8_forensics_and_lock():
    print("=" * 95)
    print("PHASE 8: SELECTION AUDIT, COMMON OPPORTUNITY RECONCILIATION & CANDIDATE LOCK")
    print("=" * 95)

    # 1. Reconcile Common Opportunities between Model A and Model B
    df_p7 = pd.read_csv("PHASE6_MODEL_COMPARISON.csv")
    
    sub_a = df_p7[df_p7["model"].isin(["MODEL_A", "MODEL_A (Blind Limit)"])].copy()
    sub_b = df_p7[df_p7["model"].isin(["MODEL_B", "MODEL_B (Rejection Conf)"])].copy()

    # Construct canonical opportunity key
    sub_a["opp_key"] = sub_a["symbol"] + "_" + sub_a["date"] + "_" + sub_a["direction"]
    sub_b["opp_key"] = sub_b["symbol"] + "_" + sub_b["date"] + "_" + sub_b["direction"]

    keys_a = set(sub_a["opp_key"].unique())
    keys_b = set(sub_b["opp_key"].unique())
    common_keys = keys_a.intersection(keys_b)
    a_only_keys = keys_a.difference(keys_b)
    b_only_keys = keys_b.difference(keys_a)

    print(f"Total Unique Opportunity Set:")
    print(f"  - Model A Unique Setups: {len(keys_a)}")
    print(f"  - Model B Unique Setups: {len(keys_b)}")
    print(f"  - Common Opportunities: {len(common_keys)}")
    print(f"  - Model A Only: {len(a_only_keys)}")
    print(f"  - Model B Only: {len(b_only_keys)}")

    # Evaluate Common Opportunities
    common_a = sub_a[sub_a["opp_key"].isin(common_keys)]
    common_b = sub_b[sub_b["opp_key"].isin(common_keys)]

    a_comm_avg_r = common_a["pnl_r"].mean()
    b_comm_avg_r = common_b["pnl_r"].mean()
    a_comm_pf = common_a[common_a["pnl_r"] > 0]["pnl_r"].sum() / abs(common_a[common_a["pnl_r"] < 0]["pnl_r"].sum())
    b_comm_pf = common_b[common_b["pnl_r"] > 0]["pnl_r"].sum() / abs(common_b[common_b["pnl_r"] < 0]["pnl_r"].sum())

    print(f"\nExecution Effect on Common Opportunities (N = {len(common_keys)}):")
    print(f"  - Model A (Blind Limit) on Common: Avg R: {a_comm_avg_r:.2f}R | PF: {a_comm_pf:.2f}")
    print(f"  - Model B (Rejection Conf) on Common: Avg R: {b_comm_avg_r:.2f}R | PF: {b_comm_pf:.2f}")
    print(f"  - Execution Effect Delta: +{b_comm_avg_r - a_comm_avg_r:.2f}R")

    common_df = pd.DataFrame([{
        "metric": "Common Opportunities",
        "common_count": len(common_keys),
        "a_only_count": len(a_only_keys),
        "b_only_count": len(b_only_keys),
        "model_a_common_avg_r": round(a_comm_avg_r, 2),
        "model_a_common_pf": round(a_comm_pf, 2),
        "model_b_common_avg_r": round(b_comm_avg_r, 2),
        "model_b_common_pf": round(b_comm_pf, 2),
        "execution_effect_delta_r": round(b_comm_avg_r - a_comm_avg_r, 2)
    }])
    common_df.to_csv("PHASE8_COMMON_OPPORTUNITY.csv", index=False)

    # 2. Immutable Specification Manifest Hash
    spec_content = """
    STRATEGY_IDENTIFIER: Dhyanaksh-DemandConf-B-v1.1-research
    DIRECTION: DEMAND ONLY
    TIMEFRAME_MAPPING: 3M -> 1W/1D, 1M -> 1D, 1W -> 1D, 1D -> 1D Reversal Close
    CONFIRMATION_RULE: Candle Close > Candle Open AND (Lower Wick >= 2x Real Body OR Bullish Engulfing)
    STOP_LOSS_RULE: Distal - 0.20 ATR Buffer
    TARGET_RULES: T1 = 2.0R, T2 = 3.5R, T3 = 5.0R
    FRICTION_ASSUMPTION: 25 bps round-trip (Brokerage + STT + Slippage)
    UNIVERSE: 30 Liquid NIFTY Equities Frozen Baseline
    PAPER_MODE_ONLY: ENABLE_LIVE_BROKER_EXECUTION=false
    """
    spec_hash = hashlib.sha256(spec_content.strip().encode("utf-8")).hexdigest()
    print(f"\nGenerated Immutable Candidate Specification Hash:\n  {spec_hash}")

    manifest = {
        "strategy_id": "Dhyanaksh-DemandConf-B-v1.1-research",
        "hash": spec_hash,
        "direction": "DEMAND_ONLY",
        "universe_size": 30,
        "cost_bps": 25,
        "frozen_timestamp": datetime.now().isoformat(),
        "status": "PROSPECTIVE_OBSERVATION_ACTIVE"
    }
    with open("PHASE8_CANDIDATE_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # 3. Initialize Isolated Paper Cohort
    cols = [
        "signal_id", "symbol", "date", "htf", "zone_id", "zone_creation_time", "zone_type",
        "conf_timeframe", "conf_timestamp", "conf_ohlc", "entry_price", "stop_loss",
        "target_1", "target_2", "target_3", "gtf_score", "conviction_score", "regime",
        "confluence_count", "signal_timestamp", "paper_exec_timestamp", "slippage_bps",
        "trade_status", "exit_reason", "pnl_r"
    ]
    df_cohort = pd.DataFrame(columns=cols)
    df_cohort.to_csv("PAPER_TRADING_V1_1_DEMANDCONF.csv", index=False)
    print("Initialized isolated prospective ledger: PAPER_TRADING_V1_1_DEMANDCONF.csv")
    print("=" * 95)

if __name__ == "__main__":
    run_phase8_forensics_and_lock()
