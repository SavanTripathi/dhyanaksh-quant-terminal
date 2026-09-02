# 📋 PAPER TRADING AUDIT & FORWARD VALIDATION REPORT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Strategy Version:** `v1.0.0-c90ed1b`

---

## 1. SCORE DISCRIMINATION FORENSIC AUDIT (INVESTIGATION 4 & 5)

### Core Finding on Conviction Score vs Future Performance:
When evaluated independently across the **5,294 verified trades**:

| Conviction Score Bucket | Historical Trades | Win Rate ($\ge 2.0R$) | Average $R$ | Profit Factor | Empirical Meaning |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Score 60–69** | 2,242 | 29.5% | $-0.08R$ | **0.89** | Single-TF setups (tight ranges) |
| **Score 80–84** | 590 | 28.6% | $-0.10R$ | **0.86** | Moderate confluence |
| **Score 85–89** | 331 | 24.5% | $-0.24R$ | **0.68** | Intermediate confluence |
| **Score 90–93** | 1,535 | 25.0% | $-0.22R$ | **0.71** | Multi-TF setups |
| **Score 94–97** | 170 | 20.0% | $-0.37R$ | **0.53** | Macro setups |
| **Score 98–100** | 426 | 22.3% | $-0.30R$ | **0.62** | Full confluence setups |

### Core Finding on GTF 13-Point Score:
| GTF Score Bucket | Trades | Win Rate | Average $R$ | Profit Factor |
| :--- | :---: | :---: | :---: | :---: |
| **GTF $\le 8.0$** | 906 | **35.1%** | **$+0.10R$** | **1.16** |
| **GTF 8.1–9.0** | 1,825 | 31.4% | $-0.02R$ | 0.97 |
| **GTF 9.1–10.0** | 1,465 | 27.0% | $-0.16R$ | 0.79 |
| **GTF 10.1–11.0** | 738 | 18.4% | $-0.42R$ | 0.48 |
| **GTF $\ge 11.1$** | 360 | 0.3% | $-0.99R$ | 0.01 |

### ⚠️ Critical Discovery: Score Inversion under Unassisted Limit Orders
1. **Why high scores underperform on blind limit orders:**  
   High GTF ($12\text{--}13$) and high conviction ($90\text{--}100$) scores belong to **Higher Timeframe (Quarterly & Monthly) zones**. These macro zones naturally have wider price intervals (e.g. ₹500–₹800 range). Placing a tight 0.20 ATR stop on a Quarterly zone causes normal intraday noise to hit the stop loss before price can travel 2.0R to the macro target.
2. **GTF Theory Parity:**  
   GTF methodology explicitly states: *“Higher Timeframe zones require Lower Timeframe (LTF) confirmation entry (Type 2/3 entry)”*. Blind unassisted limit orders (Type 1) on 3M zones violate the execution requirement and result in negative expectancy.

---

## 2. FORWARD PAPER-TRADING SYSTEM LAUNCH

1. **Non-Executable Safety Assurance:** The terminal's paper trading module is configured as a point-in-time snapshot ledger (`screener_shortlist_cache` / `paper_trading_ledger`) with zero broker API order pathways.
2. **Current Baseline Universe:** 492 active NIFTY 500 equities scanned daily.
3. **Daily Tracking File:** Initialized in [`PAPER_TRADING_DAILY.csv`](file:///d:/New%20folder/AI%20Quant/PAPER_TRADING_DAILY.csv).
