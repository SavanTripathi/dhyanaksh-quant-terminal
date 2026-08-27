# STRICT FRONTEND UI/UX DIRECTIVE — CRYSTAL-CLEAR TRADINGVIEW HTF CHARTING WITH TOGGLEABLE OVERLAYS (ZERO BACKEND TOUCH)

## Project Name
**Dhyanaksh — HTF Supply & Demand Quant Terminal**

---

### Core UI/UX Objective & Visual Standard
Eliminate all visual clutter, messy overlapping lines, and in-chart text boxes. Replicate the minimalist, crystal-clear TradingView HTF mobile/desktop layout shown in the reference charts (`COFORGE`, `HFCL`, `LICHSGFIN`):

1. **Clean Default State (Zone-Type Aware):**
   - **For Demand Zone Stocks:** Default chart displays **ONLY the 3 Blue HTF Lines** on the right price axis:
     - **Proximal (Entry):** Solid Royal Blue (`#2563EB` / `#3B82F6`)
     - **Distal (Floor):** Solid Royal Blue (`#2563EB` / `#3B82F6`)
     - **Broken Opposing Supply:** Sky Blue (`#38BDF8` / `#60A5FA`)
   - **For Supply Zone Stocks:** Default chart displays **ONLY the 3 Zone Lines**:
     - **Proximal (Entry):** Solid Royal Blue (`#2563EB` / `#3B82F6`)
     - **Distal (Ceiling):** Solid Royal Blue (`#2563EB` / `#3B82F6`)
     - **Broken Opposing Demand:** Sky Blue (`#38BDF8` / `#60A5FA`)
   - **Continuous CMP Line:** Clean right-axis settlement close tag.

2. **On-Demand Toggleable Overlays:**
   - **EMAs (20 / 50 / 200):** Hidden by default (or clean toggle). Render their price curves ONLY when their respective pill buttons are clicked/active.
   - **Trade Plan Lines (`SL / T1 / T2 / T3`):** Hidden by default. Render execution lines ONLY when the `Trade Plan (SL / T1-T3)` toggle button is active.
   - **Volume:** Clean, subtle histogram confined strictly to the bottom 18% of the pane (`top: 0.82, bottom: 0.0`).

3. **Zero Clutter Inside the Canvas:**
   - Remove floating boxes, semi-transparent overlays, and heavy text badges inside the candlestick area.
   - All setup metadata (confluences, scores, risk/reward) remains cleanly structured inside the **Center Conviction Card** and **Left Sidebar**.

---

### Strict Implementation Guardrails
> 1. **ZERO BACKEND MODIFICATIONS:** Zero edits permitted in `app/`, database schemas, or python scan scripts.
> 2. **FRONTEND UI/CHART REFACTOR ONLY:** Focus strictly on `frontend/src/components/chart/TradingViewChart.tsx`.
