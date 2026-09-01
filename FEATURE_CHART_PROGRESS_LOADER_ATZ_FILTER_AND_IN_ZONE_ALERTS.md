# AUTONOMOUS MASTER DIRECTIVE — PROGRESSIVE 1-100% CHART LOADER, ATZ (ALL TIMEFRAME ZONES) CONFLUENCE FILTER, LIVE IN-ZONE ALERT BAR & MANDATORY VISUAL SELF-DEBUG

## Project Name
**Dhyanaksh — HTF Supply & Demand Quant Terminal**
**Execution Mode:** Full-Stack Feature Addition with Mandatory Autonomous Headless Browser Visual Self-Audit & Dual Deployment.

---

### ⚠️ IMMUTABLE QUANT & UI GUARDRAILS (PRESERVE WORKING FOUNDATION)
> 1. **DO NOT MODIFY CORE GTF LOGIC:** 7-Point Scoring (Freshness 3 pts, Departure 2 pts, Time at Base 2 pts), Location on Curve, and 2 Royal Blue lines (`#2563EB`) chart visualization remain locked.
> 2. **DO NOT ALTER 3-COLUMN TERMINAL LAYOUT:** Keep the left shortlist, center conviction card, and right chart pane.
> 3. **PRESERVE ALL 490+ NIFTY 500 PERSISTED DATABASE SETUPS:** Build directly upon the existing SQLite database and cached endpoints.

---

### 1. Mandatory Autonomous Self-Audit Directive (Antigravity Requirement)
> **Antigravity Action Requirement:**
> Before reporting completion, you MUST launch a local dev server or headless browser session (using Playwright, Puppeteer, or built-in browser inspection), interact with every new element, take a screenshot, and autonomously verify:
> 1. **Progress Loader Check:** When clicking any stock in the left panel, the right chart area displays the **1% to 100% numerical progress loader** before cleanly rendering candlesticks and the 2 Royal Blue lines.
> 2. **ATZ Filter Check:** Clicking **`👑 ATZ (All TF Zones)`** successfully filters and isolates high-confluence multi-timeframe stocks ($\ge 3$ active timeframes).
> 3. **Live In-Zone Alert Ticker Check:** The top ticker bar renders clickable badges for all stocks currently inside a Demand/Supply zone. Clicking a ticker immediately loads that stock.
> 4. **PWA & Responsiveness Check:** PWA manifest and service worker load cleanly with zero console runtime errors.

---

### 2. Feature 1: Right-Side 1%–100% Chart Progress Loader (`TradingViewChart.tsx`)
When switching stocks, render a smooth numerical progress loader overlay (1% to 100%) inside the chart container while candles and zone coordinates are fetched and painted.

---

### 3. Feature 2: 👑 ATZ (All Timeframe Zones) Confluence Filter (`FilterBar.tsx` & `App.tsx`)
Add a dedicated filter pill for stocks with Triple/Quadruple Confluence (e.g., active simultaneously in QDZ, MDZ, and WDZ).

---

### 4. Feature 3: Live In-Zone Alert Ticker Bar (`frontend/src/components/AlertTicker.tsx`)
Add a dynamic top ticker bar showing all stocks currently 🟢 INSIDE ZONE with live pulse badges.

---

### 5. Acceptance & Visual Audit Checklist
- [ ] Clicking any stock displays a smooth 1% to 100% progress bar in the chart area until candlestick data is ready.
- [ ] Clicking 👑 ATZ (All TF Zones) filters the sidebar to show only multi-timeframe confluence stocks ($\ge 3$ active timeframes).
- [ ] The top Live In-Zone Alert Bar displays clickable badges for all stocks currently inside a Demand or Supply zone.
- [ ] PWA installability and manifest remain fully active with zero console errors.
- [ ] npm run build succeeds with 0 errors.
