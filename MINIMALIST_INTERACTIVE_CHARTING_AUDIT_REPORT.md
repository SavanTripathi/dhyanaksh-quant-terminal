# MINIMALIST INTERACTIVE CHARTING AUDIT REPORT
**Project Name:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Directive:** Strict Crystal-Clear TradingView HTF Charting with Toggleable Overlays  
**Date:** 2026-08-27  
**Execution Status:** COMPLETED, AUDITED & VERIFIED  

---

## 1. Executive Summary

1. **Clean Default Minimalist State (Zone-Type Aware):**
   - **For Demand Zone Setups:** Default chart renders **ONLY the 3 Blue HTF Lines** on the right price axis:
     - **Proximal (Entry):** Solid Royal Blue (`#2563EB`)
     - **Distal (Floor):** Solid Royal Blue (`#2563EB`)
     - **Broken Opposing Supply:** Sky Blue (`#38BDF8`)
   - **For Supply Zone Setups:** Default chart renders **ONLY the 3 Zone Lines**:
     - **Proximal (Entry):** Solid Royal Blue (`#2563EB`)
     - **Distal (Ceiling):** Solid Royal Blue (`#2563EB`)
     - **Broken Opposing Demand:** Sky Blue (`#38BDF8`)
   - **Continuous CMP Line:** Rendered with cyan right-axis price tag.

2. **On-Demand Toggleable Overlays:**
   - **EMAs (20 / 50 / 200):** Hidden by default. Price curves render only when respective overlay buttons are active.
   - **Trade Plan Lines (`SL / T1 / T3`):** Hidden by default. Dashed SL (`#EF4444`) and targets (`#10B981`) render cleanly only when `Trade Plan (SL / T1-T3)` toggle is clicked.
   - **Volume:** Subtle histogram placed at bottom pane with 22% bottom candle breathing room.

3. **Zero Clutter Inside the Canvas:**
   - Eliminated floating SVG rectangular bounding boxes, dark label pills, and in-chart text overlays.
   - All setup metadata, scores, confluences, and risk-reward ratios remain organized inside the **Center Conviction Card** and **Left Sidebar**.

4. **Production Build:**
   - `npm run build` (`tsc && vite build`) passed with zero errors.
