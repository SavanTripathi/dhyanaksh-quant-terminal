import sys
import os
import json
import time
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.engine.universe import UniverseRepository
from app.engine.data_feed import fetch_nse_market_data, generate_calibrated_nifty_data
from app.engine.pipeline import ScannerPipeline
from app.engine.trade_engine import TradeEngine
from app.domain.enums import Timeframe, ZoneDirection, FreshnessStatus


def run_scanner():
    print("=" * 60)
    print("GTF NIFTY 500 QUANTITATIVE SCANNER EXECUTION")
    print("=" * 60)
    t_start = time.time()
    pipeline = ScannerPipeline()
    trade_engine = TradeEngine()
    
    # 1. Canonical Universe Verification
    all_stocks = UniverseRepository.get_all_stocks()
    universe = [s["symbol"] for s in all_stocks]
    unique_symbols = list(dict.fromkeys(universe))
    
    duplicate_count = len(universe) - len(unique_symbols)
    # Check for any test/mock tokens
    extra_symbols_list = [s for s in unique_symbols if "TEST" in s or "MOCK" in s or "EXCLUDED" in s]
    extra_count = len(extra_symbols_list)

    print(f"Canonical Universe Source: app/engine/nifty500_universe.json")
    print(f"Effective Constituent Count: {len(universe)}")
    print(f"Duplicates: {duplicate_count}")
    print(f"Extra / Mock Symbols: {extra_count}")

    results = {
        "total_universe": len(unique_symbols),
        "successfully_processed": 0,
        "failed": 0,
        "missing_ohlcv": 0,
        "duplicates": duplicate_count,
        "extra_symbols": extra_count,
        "zones_detected": 0,
        "demand_zones": 0,
        "supply_zones": 0,
        "fresh_zones": 0,
        "tested_zones": 0,
        "breached_zones": 0,
        "approaching": 0,
        "in_zone": 0,
        "reacting": 0
    }

    scan_timeframes = [
        Timeframe.QUARTERLY,
        Timeframe.MONTHLY,
        Timeframe.WEEKLY,
        Timeframe.DAILY
    ]

    for idx, symbol in enumerate(unique_symbols):
        try:
            # Deterministic calibrated data for consistent scanning across entire universe
            df = generate_calibrated_nifty_data(symbol, days=365)

            if df is None or df.empty or len(df) < 10:
                results["missing_ohlcv"] += 1
                continue

            current_price = float(df["close"].iloc[-1])
            close_price = current_price
            open_price = float(df["open"].iloc[-1])
            high_price = float(df["high"].iloc[-1])
            low_price = float(df["low"].iloc[-1])

            # Run strict MTF GTF Scan
            scan_res = pipeline.run_scan_on_dataframe(
                symbol=symbol,
                df_intraday_or_daily=df,
                timeframes=scan_timeframes,
                min_achievements=2
            )

            results["successfully_processed"] += 1
            results["zones_detected"] += scan_res.total_zones_detected

            # Count zones from all_zones
            if scan_res.all_zones:
                for z in scan_res.all_zones:
                    if z.direction == ZoneDirection.DEMAND:
                        results["demand_zones"] += 1
                    else:
                        results["supply_zones"] += 1

                    if z.is_breached:
                        results["breached_zones"] += 1
                    elif z.retest_count == 0:
                        results["fresh_zones"] += 1
                    else:
                        results["tested_zones"] += 1

            # Formulate trade plans for spatial clusters to evaluate proximity states
            indicators = {
                "atr_1d_14": max(1.0, round(current_price * 0.02, 2)),
                "atr_buffer": max(0.2, round(current_price * 0.004, 2)),
                "current_price": current_price,
                "open_price": open_price,
                "is_bullish_candle": close_price > open_price,
                "is_bearish_candle": close_price < open_price
            }

            for cluster in scan_res.clusters:
                plan = trade_engine.generate_trade_plan(
                    cluster=cluster,
                    daily_indicators=indicators
                )
                if plan.proximity_state == "APPROACHING":
                    results["approaching"] += 1
                elif plan.proximity_state == "IN_ZONE":
                    results["in_zone"] += 1
                elif plan.proximity_state == "REACTING":
                    results["reacting"] += 1

            if (idx + 1) % 50 == 0 or (idx + 1) == len(unique_symbols):
                print(f"Processed [{idx + 1}/{len(unique_symbols)}] stocks... (Detected {results['zones_detected']} zones)")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            results["failed"] += 1

    elapsed = round(time.time() - t_start, 2)
    print(f"\nNIFTY 500 Scan Complete in {elapsed}s!")
    print(json.dumps(results, indent=2))

    with open("nifty500_gtf_scan_report.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    run_scanner()
