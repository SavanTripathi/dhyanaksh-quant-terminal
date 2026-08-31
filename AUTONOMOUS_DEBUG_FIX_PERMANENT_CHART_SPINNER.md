# AUTONOMOUS DEBUG & SURGICAL FIX DIRECTIVE — ELIMINATE PERMANENT CHART LOADING OVERLAY BUG

## Project Name
**Dhyanaksh — HTF Supply & Demand Quant Terminal**

---

### 1. Root Cause Identification (Autonomous Self-Debug)
In `frontend/src/components/chart/TradingViewChart.tsx`:
* The condition rendering the loading screen was:
  ```tsx
  const isLoadingCandles = isLoading || (candles.length === 0 && !hasCachedData);
  ```
* Because candles are pushed directly to Lightweight Charts via `candlestickSeriesRef.current.setData(cleanedCandles)` without updating a local React `const [candles, setCandles] = useState([])` state, `candles.length` could be 0 when data was directly fetched, permanently pinning the loading overlay.

---

### 2. Guardrails
- **DO NOT MODIFY BACKEND:** Do not touch Python files, SQLite schemas, or scanner algorithms.
- **DO NOT CHANGE UI/CHART DESIGN:** Keep the 3-column layout and the default strictly 2 Royal Blue lines intact.

---

### 3. Surgical Code Fix (`frontend/src/components/chart/TradingViewChart.tsx`)
- Manage loading overlay visibility strictly using `isLoading`.
- Provide immediate dismissal on cached data and in the `finally` block of direct fetch calls.
