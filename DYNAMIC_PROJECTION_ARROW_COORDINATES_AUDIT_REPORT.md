# DYNAMIC CHART COORDINATE PROJECTION ARROW AUDIT REPORT
**Project Name:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Directive Reference:** [`SURGICAL_FIX_DYNAMIC_PROJECTION_ARROW_COORDINATES_STRICT_NO_BACKEND.md`](file:///d:/New%20folder/AI%20Quant/SURGICAL_FIX_DYNAMIC_PROJECTION_ARROW_COORDINATES_STRICT_NO_BACKEND.md)  
**Date:** 2026-08-27  
**Execution Status:** COMPLETED, AUDITED & VERIFIED  

---

## 1. Executive Summary

1. **Root Cause Resolved:**
   - The projection arrow was previously rendered in a static SVG overlay that did not follow zoom and pan events on the Lightweight Charts time and price axes.
   - Replaced static positioning with a high-performance transparent canvas overlay bound directly to the Lightweight Charts Coordinate API:
     - `startX = timeScale.timeToCoordinate(lastCandle.time)`
     - `startY = candlestickSeries.priceToCoordinate(entry_price)`
     - `endY = candlestickSeries.priceToCoordinate(target_3 || target_1)`

2. **Pan, Zoom & Viewport Synchronization:**
   - Added subscriptions to `timeScale.subscribeVisibleLogicalRangeChange()`, `timeScale.subscribeVisibleTimeRangeChange()`, `chart.subscribeCrosshairMove()`, and `window.addEventListener('resize')`.
   - On every pan, zoom, or drag frame, `drawDynamicProjectionArrow()` recalculates exact `(X, Y)` canvas pixels so the arrow remains locked to its entry origin and target ceiling.

3. **Strict Zero Backend Modification Guardrail:**
   - Only frontend chart component ([`TradingViewChart.tsx`](file:///d:/New%20folder/AI%20Quant/frontend/src/components/chart/TradingViewChart.tsx)) was modified.
   - Continuous closing CMPs, SQLite database persistence, GTF zone models, and schedulers remain intact.

4. **Production Build:**
   - `npm run build` (`tsc && vite build`) passed with zero errors.
