# 📊 PHASE 9 — V1.0.0 VS V1.1.0-RESEARCH COMPARATIVE BENCHMARK

**Baseline Production Strategy:** `Dhyanaksh-HTF-SD-v1.0.0` (`v1.0.0-c90ed1b`) — **FROZEN**  
**Prospective Research Candidate:** `Dhyanaksh-DemandConf-B-v1.1-research` (`Hash: 1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852`) — **FROZEN**

---

## 1. ARCHITECTURAL COMPARISON

| Feature / Dimension | Strategy v1.0.0 (Production Paper Baseline) | Strategy v1.1-research (Prospective Candidate) |
| :--- | :--- | :--- |
| **Execution Trigger** | Blind Limit at Proximal Price (Type 1) | Reversal Rejection Close on LTF (Type 2A) |
| **Directional Universe** | Both Demand & Supply Setups | **Demand Setups Only** |
| **HTF Stop Buffering** | $\text{Distal} \pm 0.20\text{ ATR}$ | $\text{Distal} - 0.20\text{ ATR}$ below confirmed base |
| **Historical Full PF** | **0.78** ($-0.16R$) | **1.14 – 1.30** (Demand subset) |
| **Historical OOS PF** | **0.73** ($-0.21R$) | **0.91** (All-direction) / **1.17** (Demand $\times$ Bull) |
| **Ledger Destination** | [`PAPER_TRADING_DAILY.csv`](file:///d:/New%20folder/AI%20Quant/PAPER_TRADING_DAILY.csv) | [`PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv`](file:///d:/New%20folder/AI%20Quant/PAPER_TRADING_V1_1_DEMANDCONF_DAILY.csv) |
| **Safety Guard** | `ENABLE_LIVE_BROKER_EXECUTION=false` | `ENABLE_LIVE_BROKER_EXECUTION=false` |
