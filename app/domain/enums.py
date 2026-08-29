"""
Domain Enums for HTF Zone Scanner Terminal (Steps 1, 2, and 3).
"""
from enum import Enum


class Timeframe(str, Enum):
    QUARTERLY = "3M"
    MONTHLY = "1M"
    WEEKLY = "1W"
    DAILY = "1D"
    MIN_125 = "125M"
    MIN_75 = "75M"


class ZoneDirection(str, Enum):
    DEMAND = "DEMAND"
    SUPPLY = "SUPPLY"


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    INVALIDATED = "INVALIDATED"


class ZoneStructure(str, Enum):
    # Demand structures
    DBR = "DBR"  # Drop Base Rally (Reversal Demand)
    RBR = "RBR"  # Rally Base Rally (Continuation Demand)
    # Supply structures
    RBD = "RBD"  # Rally Base Drop (Reversal Supply)
    DBD = "DBD"  # Drop Base Drop (Continuation Supply)


class CandleType(str, Enum):
    ERC = "ERC"    # Expanded Range Candle (Institutional momentum)
    NRC = "NRC"    # Narrow Range Candle / Basing Candle
    NORMAL = "NORMAL"


class AlertType(str, Enum):
    APPROACHING = "APPROACHING"          # 0% <= Distance % <= 2.5%
    ZONE_HIT = "ZONE_HIT"                # Price inside [L_common, H_common]
    TARGET_1_HIT = "TARGET_1_HIT"        # Target 1 reached (2.0R)
    TARGET_2_HIT = "TARGET_2_HIT"        # Target 2 reached (3.5R)
    TARGET_3_HIT = "TARGET_3_HIT"        # Target 3 reached (5.0R)
    INVALIDATED = "INVALIDATED"          # Closed beyond Stop Loss / Distal Line
    SYSTEM_TEST = "SYSTEM_TEST"          # Connectivity verification


class AlertChannel(str, Enum):
    TELEGRAM = "TELEGRAM"
    WEBHOOK = "WEBHOOK"
    IN_APP = "IN_APP"


class AlertState(str, Enum):
    MONITORING = "MONITORING"
    APPROACHING = "APPROACHING"
    INSIDE_ZONE = "INSIDE_ZONE"
    TARGET_1_HIT = "TARGET_1_HIT"
    TARGET_2_HIT = "TARGET_2_HIT"
    TARGET_3_HIT = "TARGET_3_HIT"
    INVALIDATED = "INVALIDATED"
