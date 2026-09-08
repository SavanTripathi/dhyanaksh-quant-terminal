import sys
import os
import pandas as pd
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.domain.enums import Timeframe, CandleType, ZoneDirection, ZoneStructure
from app.domain.schemas import CandleSchema, ZoneSchema
from app.engine.aggregator import CandleAggregator
from app.engine.zone_detector import ZoneDetector
from app.core.config import settings

def run_f3():
    print("\n" + "=" * 95)
    print("PHASE F3 — RAW FLOAT VS ROUNDING FORENSIC INVESTIGATION")
    print("=" * 95)
    test_ratios = [
        0.490000000000,
        0.499000000000,
        0.499999000000,
        0.499999900000,
        0.499999999000,
        0.499999999999,
        0.500000000000,
        0.500000000001,
        0.500000001000,
        0.500000100000,
        0.500001000000,
        0.501000000000,
        0.510000000000,
        0.600000000000,
        0.650000000000,
    ]
    erc_ratio = 0.50
    print(f"{'Raw Ratio':<20} | {'round(ratio, 6)':<18} | {'Actual Current':<18} | {'Raw Strict':<12} | {'Same?'}")
    print("-" * 95)
    for r in test_ratios:
        r_round = round(r, 6)
        # Actual current classification in aggregator.py
        if r_round > erc_ratio:
            curr = "ERC"
        elif r_round < erc_ratio:
            curr = "NRC"
        else:
            curr = "NORMAL"
            
        # Raw strict classification
        if r > erc_ratio:
            strict = "ERC"
        elif r < erc_ratio:
            strict = "NRC"
        else:
            strict = "NORMAL"
            
        print(f"{r:<20.12f} | {r_round:<18.6f} | {curr:<18} | {strict:<12} | {curr == strict}")

def run_f4():
    print("\n" + "=" * 95)
    print("PHASE F4 — OHLC-DERIVED REALISTIC BOUNDARY TESTING")
    print("=" * 95)
    
    # Generate candles with various price scales
    fixtures = [
        # Exact 50%
        ("5 / 10", 100.0, 105.0, 110.0, 100.0, "NORMAL"),
        ("50 / 100", 1000.0, 1050.0, 1100.0, 1000.0, "NORMAL"),
        ("0.5 / 1.0", 10.0, 10.5, 11.0, 10.0, "NORMAL"),
        ("500 / 1000", 5000.0, 5500.0, 6000.0, 5000.0, "NORMAL"),
        ("Tick subtraction: 0.10 / 0.20", 100.10, 100.20, 100.30, 100.10, "NORMAL"),
        ("Tick subtraction: 0.15 / 0.30", 250.15, 250.30, 250.45, 250.15, "NORMAL"),
        # Below 50%
        ("499999 / 1000000", 1000000.0, 1499999.0, 2000000.0, 1000000.0, "NRC"),
        ("4999999 / 10000000", 10000000.0, 14999999.0, 20000000.0, 10000000.0, "NRC"),
        ("4.99 / 10.0", 100.0, 104.99, 110.0, 100.0, "NRC"),
        # Above 50%
        ("500001 / 1000000", 1000000.0, 1500001.0, 2000000.0, 1000000.0, "ERC"),
        ("5000001 / 10000000", 10000000.0, 15000001.0, 20000000.0, 10000000.0, "ERC"),
        ("5.01 / 10.0", 100.0, 105.01, 110.0, 100.0, "ERC"),
    ]
    
    print(f"{'Description':<32} | {'Raw Ratio':<18} | {'round(r,6)':<12} | {'Current Cls':<12} | {'Expected':<10} | {'Match?'}")
    print("-" * 95)
    for desc, o, c, h, l, exp in fixtures:
        row = pd.Series({"open": o, "close": c, "high": h, "low": l, "volume": 1000})
        res = CandleAggregator.classify_candle(row, 0.50)
        c_type = res["candle_type"].value
        
        tr_raw = h - l
        br_raw = abs(c - o)
        ratio_raw = br_raw / tr_raw if tr_raw > 0 else 0.0
        
        print(f"{desc:<32} | {ratio_raw:<18.12f} | {round(ratio_raw, 6):<12.6f} | {c_type:<12} | {exp:<10} | {c_type == exp}")

def run_f7():
    print("\n" + "=" * 95)
    print("PHASE F7 — ZONE DETECTOR BOUNDARY FORENSICS")
    print("=" * 95)
    
    detector = ZoneDetector(max_base_candles=3)
    from datetime import datetime, timezone
    
    base_time = datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc)
    
    # Helper to make candle
    def make_c(o, h, l, c, i):
        ts = datetime(2026, 1, 1 + i, 9, 15, tzinfo=timezone.utc)
        row = pd.Series({"open": o, "high": h, "low": l, "close": c, "volume": 1000})
        cls_dict = CandleAggregator.classify_candle(row, 0.50)
        return CandleSchema(
            timestamp=ts,
            symbol="TEST",
            timeframe=Timeframe.DAILY,
            open=o, high=h, low=l, close=c, volume=1000,
            candle_type=cls_dict["candle_type"],
            total_range=cls_dict["total_range"],
            body_range=cls_dict["body_range"],
            body_ratio=cls_dict["body_ratio"]
        )

    # Leg-Out valid Bullish ERC: 100 -> 110, H=110, L=100 (Ratio = 1.0)
    leg_out = make_c(100.0, 110.0, 100.0, 110.0, 2)
    # Valid Base NRC: 100 -> 102, H=110, L=100 (Ratio = 0.20)
    valid_base = [make_c(100.0, 110.0, 100.0, 102.0, 1)]
    
    cases = [
        # CASE A: Below Boundary Leg-In (Ratio = 0.499999 -> NRC)
        ("CASE A: Leg-In ratio 0.499999 (NRC)", make_c(1000000.0, 2000000.0, 1000000.0, 1499999.0, 0), valid_base, leg_out, 0),
        # CASE B: Exact Boundary Leg-In (Ratio = 0.500000 -> NORMAL)
        ("CASE B: Leg-In ratio 0.500000 (NORMAL)", make_c(100.0, 110.0, 100.0, 105.0, 0), valid_base, leg_out, 0),
        # CASE C: Above Boundary Leg-In (Ratio = 0.500001 -> ERC)
        ("CASE C: Leg-In ratio 0.500001 (ERC)", make_c(1000000.0, 2000000.0, 1000000.0, 1500001.0, 0), valid_base, leg_out, 1),
        # CASE D: Invalid ERC Base (Ratio = 0.600000 -> ERC)
        ("CASE D: Base ratio 0.600000 (ERC)", make_c(100.0, 110.0, 90.0, 90.0, 0), [make_c(90.0, 100.0, 90.0, 96.0, 1)], make_c(90.0, 110.0, 90.0, 110.0, 2), 0),
        # CASE E: Exact 0.50 Base (Ratio = 0.500000 -> NORMAL)
        ("CASE E: Base ratio 0.500000 (NORMAL)", make_c(100.0, 110.0, 90.0, 90.0, 0), [make_c(90.0, 100.0, 90.0, 95.0, 1)], make_c(90.0, 110.0, 90.0, 110.0, 2), 0),
        # CASE F: Valid NRC Base (Ratio = 0.499999 -> NRC)
        ("CASE F: Base ratio 0.499999 (NRC)", make_c(1800000.0, 1900000.0, 900000.0, 900000.0, 0), [make_c(900000.0, 1900000.0, 900000.0, 1399999.0, 1)], make_c(900000.0, 2100000.0, 900000.0, 2100000.0, 2), 1),
    ]

    print(f"{'Case Description':<40} | {'Expected Zones':<15} | {'Actual Zones':<15} | {'Match?'}")
    print("-" * 95)
    for desc, li, basing, lo, exp_count in cases:
        candles = [li] + basing + [lo]
        detected = detector.detect_zones(candles)
        print(f"{desc:<40} | {exp_count:<15} | {len(detected):<15} | {len(detected) == exp_count}")

if __name__ == "__main__":
    run_f3()
    run_f4()
    run_f7()
