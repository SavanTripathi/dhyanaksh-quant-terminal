"""
Automated Daily Prospective Paper Trading Collector
Candidate: Dhyanaksh-DemandConf-B-v1.1-research
Candidate Hash: 1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852
"""
import os
import sys
import json
import logging
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from app.engine.data_feed import fetch_nse_market_data
from app.engine.aggregator import CandleAggregator
from app.engine.zone_detector import detect_htf_supply_demand_zone
from app.engine.gtf_engine import GTFEngine
from app.engine.conviction_ranker import ConvictionRankingEngine
from app.domain.enums import Timeframe, ZoneDirection

# --- IMMUTABLE CONSTANTS ---
LOCKED_CANDIDATE_HASH = "1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852"
PROSPECTIVE_START_BOUNDARY = "2026-09-01T00:00:00Z"
FIXED_COST_BPS = 25
UNIVERSE = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC",
    "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN",
    "BAJFINANCE", "ULTRACEMCO", "NTPC", "ONGC", "WIPRO", "HCLTECH",
    "POWERGRID", "COALINDIA", "TATASTEEL", "TMPV", "BERGEPAINT", "EMAMILTD",
    "TITAGARH", "MAZDOCK", "BIKAJI"
]

LOG_FILE = "logs/prospective_daily_runner.log"
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_daily_prospective_collector():
    logging.info("=" * 80)
    logging.info("STARTING PROSPECTIVE DAILY COLLECTOR SESSION")
    
    # 1. Safety Hard-Gate: Live broker execution must be disabled
    live_broker = os.getenv("ENABLE_LIVE_BROKER_EXECUTION", "false").lower()
    if live_broker == "true":
        logging.critical("LIVE BROKER EXECUTION ENABLED! ABORTING PROSPECTIVE COLLECTOR.")
        sys.exit(1)
        
    # 2. Immutability Guard: Verify Candidate Hash
    if not os.path.exists("V1.1_DEMANDCONF_MANIFEST.json"):
        logging.critical("V1.1_DEMANDCONF_MANIFEST.json NOT FOUND! ABORTING.")
        sys.exit(1)
        
    with open("V1.1_DEMANDCONF_MANIFEST.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    if manifest.get("candidate_hash") != LOCKED_CANDIDATE_HASH:
        logging.critical(f"CANDIDATE HASH MISMATCH! Expected {LOCKED_CANDIDATE_HASH}, got {manifest.get('candidate_hash')}")
        sys.exit(1)

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_iso = datetime.now(timezone.utc).isoformat()

    # 3. Idempotency Guard: Check if today's snapshot is already finalized
    daily_file = "PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv"
    events_file = "PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv"

    if os.path.exists(daily_file):
        df_daily = pd.read_csv(daily_file)
        if today_str in df_daily["date"].values:
            logging.info(f"Today's date {today_str} already finalized in daily ledger. Exiting idempotently.")
            return

    # 4. Ingest and Evaluate 30 Equities
    logging.info(f"Evaluating {len(UNIVERSE)} universe equities on prospective boundary >= {PROSPECTIVE_START_BOUNDARY}")
    
    gtf_engine = GTFEngine()
    conviction_engine = ConvictionRankingEngine()

    new_signals_count = 0
    confirmed_count = 0
    filled_count = 0
    closed_count = 0

    # Ensure ledgers exist with headers
    if not os.path.exists(events_file):
        df_init_events = pd.DataFrame(columns=[
            "event_id", "setup_id", "symbol", "timestamp", "event_type", "state", "details", "candidate_hash"
        ])
        df_init_events.to_csv(events_file, index=False)

    df_events = pd.read_csv(events_file)
    event_id_seq = len(df_events) + 1

    for sym in UNIVERSE:
        try:
            df = fetch_nse_market_data(sym, days=365)
            if df.empty or len(df) < 50:
                continue
            
            latest_bar_date = df.index[-1].strftime("%Y-%m-%d")
            # Strict boundary check
            if latest_bar_date < "2026-09-01":
                continue # Pre-boundary data is ignored by prospective runner

            # HTF Aggregation and Zone Scan
            c_1d = df.to_dict('records')
            schema_1w = CandleAggregator.aggregate_from_df(df, Timeframe.WEEKLY, sym)
            c_1w = [c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in schema_1w]
            
            z_1d = detect_htf_supply_demand_zone(c_1d, "1D")
            z_1w = detect_htf_supply_demand_zone(c_1w, "1W") if len(c_1w) >= 15 else None
            primary_zone = z_1d or z_1w

            if not primary_zone or primary_zone["direction"] != "DEMAND":
                continue

            proximal = primary_zone["proximal"]
            distal = primary_zone["distal"]
            curr_bar = df.iloc[-1]
            h, l, o, c = curr_bar["high"], curr_bar["low"], curr_bar["open"], curr_bar["close"]

            setup_id = f"{sym}_DEMAND_{latest_bar_date}"
            
            # Check if setup touched zone and confirmed
            if l <= proximal:
                new_signals_count += 1
                # Rejection confirmation test
                if c > o and (c - l) >= (h - c):
                    confirmed_count += 1
                    # Append Confirmation Event
                    new_evt = {
                        "event_id": f"PROSP-EVT-{event_id_seq:05d}",
                        "setup_id": setup_id,
                        "symbol": sym,
                        "timestamp": now_iso,
                        "event_type": "REJECTION_CONFIRMED",
                        "state": "ENTRY_PENDING",
                        "details": f"Prox: {proximal}, Dist: {distal}, Close: {c}",
                        "candidate_hash": LOCKED_CANDIDATE_HASH
                    }
                    df_events = pd.concat([df_events, pd.DataFrame([new_evt])], ignore_index=True)
                    event_id_seq += 1

        except Exception as e:
            logging.error(f"Error processing symbol {sym}: {e}")
            continue

    df_events.to_csv(events_file, index=False)

    # 5. Append Daily Snapshot
    daily_snapshot = {
        "date": today_str,
        "active_signals": 0,
        "new_signals": new_signals_count,
        "filled_trades": filled_count,
        "closed_trades": closed_count,
        "wins": 0,
        "losses": 0,
        "open_trades": 0,
        "cumulative_r": 0.0,
        "daily_r": 0.0,
        "avg_r": 0.0,
        "pf": 0.0,
        "win_rate": 0.0,
        "drawdown_r": 0.0,
        "mae_r": 0.0,
        "mfe_r": 0.0,
        "avg_slippage_bps": 0.0,
        "missed_fills": 0,
        "candidate_hash": LOCKED_CANDIDATE_HASH
    }
    
    if os.path.exists(daily_file):
        df_daily = pd.read_csv(daily_file)
        df_daily = pd.concat([df_daily, pd.DataFrame([daily_snapshot])], ignore_index=True)
    else:
        df_daily = pd.DataFrame([daily_snapshot])
    df_daily.to_csv(daily_file, index=False)

    logging.info(f"Prospective Daily Collector Completed Successfully for {today_str}. New Signals: {new_signals_count}, Confirmed: {confirmed_count}")
    print(f"Prospective Daily Collector Completed. Date: {today_str} | Candidate: {LOCKED_CANDIDATE_HASH[:16]}... | Status: SUCCESS")

if __name__ == "__main__":
    run_daily_prospective_collector()
