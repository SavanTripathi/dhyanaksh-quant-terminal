# 🔒 STRATEGY VERSION & IMMUTABLE QUANT SPECIFICATION

**Strategy Identifier:** `Dhyanaksh-HTF-SD-v1.0.0`  
**Git Commit Baseline:** `c90ed1b`  
**Status:** **FROZEN FOR OBSERVATION (NO TUNING PERMITTED)**

---

## 1. COMPONENT VERSIONS

| Subsystem | File & Function | Version | Specification |
| :--- | :--- | :---: | :--- |
| **Zone Detector** | `zone_detector.py:detect_htf_supply_demand_zone` | `v1.0.0` | 50% ERC departure, 1-6 base candles |
| **Aggregator** | `aggregator.py:CandleAggregator` | `v1.0.0` | Pandas resampling (1D, W-FRI, ME, QE) |
| **Freshness Evaluator** | `freshness.py:FreshnessEvaluator` | `v1.0.0` | Untouched origin base (0 retests) |
| **GTF 7-Point Engine** | `gtf_engine.py:calculate_gtf_7_point_trade_score` | `v1.0.0` | Freshness (3.0), Departure (2.0), Base (2.0) |
| **GTF 13-Point Engine**| `gtf_engine.py:score_gtf_13_point_odds` | `v1.0.0` | Core 7 + Confluence (3.0) + Curve (3.0) |
| **6-Pillar Conviction**| `conviction_ranker.py:compute_conviction_score` | `v1.0.0` | Zone (35), Sector (20), F&O (15), MA (15), Prox (10), FII (5) |
| **Trade Engine** | `trade_engine.py:generate_trade_plan` | `v1.0.0` | Entry=Proximal, SL=Distal ± 0.20 ATR, T1=2R, T2=3.5R, T3=5R |
| **ATZ Confluence** | `zoneEvaluator.ts:evaluateATZMatch` | `v1.0.0` | Strict 4/4 Confluence (3M ∧ 1M ∧ 1W ∧ 1D) |

---

## 2. IMMUTABILITY RULES

1. No threshold adjustments, weight modifications, or exit rule changes are allowed during live paper trading.
2. If any logic is modified, a new version tag (e.g. `v1.1.0`) must be instantiated as an independent cohort.
