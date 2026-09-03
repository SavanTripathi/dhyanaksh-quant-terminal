# 🔒 DHYANAKSH QUANT TERMINAL — MASTER PRODUCTION FREEZE MANIFEST

**Release Version:** `v3.0.0-PROD-DUALMODE`  
**Freeze Date:** `2026-09-03`  
**Active EOD Snapshot Boundary:** `2026-09-02T23:59:59+05:30`  
**Candidate Hash:** `1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852`  
**Operational Modes:**
1. `EOD ANALYSIS MODE` (Authoritative Point-in-Time Frozen Snapshot)
2. `LIVE ANALYSIS MODE` (Real-Time Intraday Session Stream)

---

## 1. FROZEN ARCHITECTURE SPECIFICATION

1. **GTF Methodology & Core Engine:**
   - 7-Point Scoring Algorithm (Freshness 3.0, Departure 2.0, Base Duration 2.0).
   - 4-Timeframe Zone Detection (Quarterly, Monthly, Weekly, Daily).
   - Strict Location-on-the-Curve & 50 SMA Trend Vector rules.
   - Dual-zone Type 1/2/3 entry archetypes and 2:1 Reward-to-Risk geometry.

2. **Intraday Mathematical Slicing:**
   - **75M:** 5 exact session buckets per trading day ($09:15, 10:30, 11:45, 13:00, 14:15$) resampled from 15m raw bars.
   - **125M:** 3 exact session buckets per trading day ($09:15, 11:20, 13:25$) resampled from 5m granular raw bars.

3. **Data Isolation & PWA Security:**
   - Backend API enforces `mode=EOD` cutoff $\le \text{as_of_date 23:59:59 IST}$.
   - Service worker bypasses cache for all `/api/v1/*` routes to guarantee snapshot integrity.
   - Zero forward lookahead leakage into historical replay or prospective daily ledgers.

---

## 2. PRODUCTION STATUS

$$\mathbf{\Huge \text{🟢 PRODUCTION FROZEN \& DEPLOYED}}$$
