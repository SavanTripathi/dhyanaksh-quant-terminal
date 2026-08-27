# CHART VIEWPORT & MARGIN CALIBRATION AUDIT REPORT
**Project Name:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Directive Reference:** Strict Frontend Surgical Directive — Fix Chart Vertical Overflow & Configure Top/Bottom Autoscale Margins  
**Date:** 2026-08-27  
**Execution Status:** COMPLETED, AUDITED & VERIFIED  

---

## 1. Executive Summary

1. **Top Toolbar Overflow & Clipping Resolved ([`TradingViewChart.tsx`](file:///d:/New%20folder/AI%20Quant/frontend/src/components/chart/TradingViewChart.tsx)):**
   - Calibrated right price scale with `scaleMargins.top = 0.18` (18% top padding clearance).
   - Prevents upper target badges (T3, Broken Supply levels) and high-peak candlesticks from hiding behind the timeframe toolbar and top HUD.

2. **Volume Sub-Pane Clean Separation:**
   - Calibrated right price scale with `scaleMargins.bottom = 0.22` (22% bottom margin).
   - Dedicated volume histogram sub-pane configured with `volume_scale` margins `top: 0.82, bottom: 0.0` (occupying only the bottom 18% of canvas).
   - Candlestick wicks and bodies stay cleanly above volume histogram bars without overlapping.

3. **TimeScale Right-Offset:**
   - Set `rightOffset = 16` (10 in multi-chart grid) providing generous horizontal clearance for right price axis labels and CMP badges.

4. **Dynamic Re-scaling on Timeframe / Symbol Switch:**
   - Integrated dynamic `applyOptions` in the candlestick data lifecycle hook to guarantee proper scale margins on every symbol selection.

5. **Production Build:**
   - `npm run build` (`tsc && vite build`) passed with zero errors.
