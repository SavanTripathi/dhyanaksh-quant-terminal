# 🔍 SURVIVORSHIP BIAS & DATA INTEGRITY AUDIT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Audit Date:** September 2026

---

## 1. HISTORICAL CONSTITUENT UNIVERSE LIMITATION

### Finding:
The historical simulation was executed on the current active NIFTY 500 constituents ($N = 492$ equities).

### Impact:
- **Survivorship Bias Present:** Equities that were delisted, entered bankruptcy, or were removed from the index over the 2023–2026 horizon are absent from the historical dataset.
- **Symbol Re-structuring:** Ticker transitions (e.g. `TATAMOTORS.NS` undergoing demerger into `TMPV.NS`) create discontinuous historical quotes in standard vendor APIs unless explicitly mapped.
- **Formal Status:** **SURVIVORSHIP BIAS IS AN UNRESOLVED LIMITATION.** Performance results reflect the performance of current surviving large/mid-cap equities rather than a point-in-time constituent list.

---

## 2. CORPORATE ACTION ADJUSTMENT METHODOLOGY

- **Split & Bonus Normalization:** All historical OHLCV data is ingested using `auto_adjust=True` from official adjusted feeds, scaling prior bars to match current capital structures.
- **Zone Geometric Safety:** Invariant checking rejects price steps or artificial zero-range anomalies resulting from corporate actions.
