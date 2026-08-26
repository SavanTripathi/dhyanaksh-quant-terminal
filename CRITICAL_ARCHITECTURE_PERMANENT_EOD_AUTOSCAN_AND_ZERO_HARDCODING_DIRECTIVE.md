# CRITICAL ARCHITECTURE DIRECTIVE — REMOVE ALL HARDCODED HEADERS, PURGE MOCK SEEDS, IMPLEMENT AUTOMATED 4:30 PM EOD SCANNER & DEFAULT DYNAMIC RESTORATION

## Project Name
**Dhyanaksh — HTF Supply & Demand Quant Terminal**

---

### Strict Implementation Rules
> **ZERO HARDCODED SYMBOLS ALLOWED ANYWHERE IN THE APP.**
> 1. Remove the static top ticker bar (`RELIANCE`, `TCS`, `HDFCBANK`, `ICICIBANK`, `INFY`, `LT`, `SBIN`, `BHARTIARTL`) from the top global header.
> 2. Purge all static mock lists from the codebase.
> 3. Implement an automated daily **4:30 PM / 5:00 PM IST End-of-Day (EOD) Cron Scanner** that ingests official NSE settlement prices and populates `production_scanner.db` dynamically.
> 4. When the app launches or restarts, it MUST query `GET /api/v1/screener/shortlist` and load only the genuine scanned qualifying stocks (Demand & Supply) sorted by Institutional Conviction Score.

---

### 1. Remove Top Hardcoded Stocks Bar (`frontend/src/components/layout/Navbar.tsx` / `App.tsx`)

* **Remove:** Delete the static array `['RELIANCE', 'TCS', 'HDFCBANK', ...]` and its container from the top header bar.
* **Keep:** Clean top navigation consisting of:
  * Brand Logo & Tagline: **DHYANAKSH** `PRO v4.0`
  * Active Tabs: `Live Terminal` | `Backtest Analytics`
  * Global Market Regime: `NIFTY 50: Bullish Consolidation` | `FII/DII Net Flow` | `Engine Live (NSE Equities)`
  * Action Button: `Scan All 500 Stocks`

---

### 2. Automated 4:30 PM IST EOD Scheduler Pipeline (`app/engine/scheduler.py` & `main.py`)

Implement an automated background scheduler using `APScheduler` that runs every market day at **16:30 IST (4:30 PM)** to ingest official NSE EOD data and refresh all qualifying zones:

```python
import os
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.engine.universe_scanner import UniverseScannerEngine

scheduler = AsyncIOScheduler()
IST = pytz.timezone("Asia/Kolkata")

async def run_daily_eod_scan():
    """
    Automated Institutional EOD Scan:
    1. Fetches official daily NSE Bhavcopy/Adjusted settlement data for all NIFTY 500 symbols.
    2. Recalculates HTF Demand/Supply zones (Quarterly, Monthly, Weekly, Daily).
    3. Evaluates GTF Odds Enhancers & Institutional Conviction Scores.
    4. Updates production_scanner.db.
    """
    print("=" * 60)
    print("[EOD AUTOSCAN] Initiating daily 4:30 PM IST NSE Scan...")
    print("=" * 60)
    engine = UniverseScannerEngine()
    await engine.run_full_universe_scan_async()
    print("[EOD AUTOSCAN] Daily scan completed and production database refreshed.")

def init_eod_scheduler():
    # Runs Monday to Friday at 16:30 IST (4:30 PM)
    trigger = CronTrigger(
        day_of_week="mon-fri",
        hour=16,
        minute=30,
        timezone=IST
    )
    scheduler.add_job(run_daily_eod_scan, trigger=trigger, id="eod_nse_scanner", replace_existing=True)
    scheduler.start()
```

---

### 3. Clean Dynamic Startup Flow (`frontend/src/App.tsx` & `ShortlistSidebar.tsx`)
Purge Fallback Hardcoded Seeds:

- Remove hardcoded static fallbacks (`['RELIANCE', 'TCS']`).
- If loading, display a clean skeleton loader: "Ingesting Verified Market Data...".

Auto-Select Top Qualifying Stock:
- When `res.plans` returns from the database, auto-select `res.plans[0]` (the highest-conviction setup in the scanned universe).

Sidebar Filter Default:
- Initialize with `preset = 'ALL'`, `typeFilter = 'ALL'`, `achievementFilter = 'ALL'`, ensuring all detected setups display immediately without zero-item collision bugs.

```typescript
// frontend/src/App.tsx Initialization
useEffect(() => {
  const initApp = async () => {
    try {
      setLoading(true);
      const res = await api.getScreenerShortlist();
      if (res && res.plans && res.plans.length > 0) {
        setTradePlans(res.plans);
        const firstStock = res.plans[0];
        setSelectedSymbol(firstStock.symbol);
        await loadChartData(firstStock.symbol, '1D');
        await loadContextData(firstStock.symbol);
      }
    } catch (err) {
      console.error("Failed to load dynamic shortlist:", err);
    } finally {
      setLoading(false);
    }
  };
  initApp();
}, []);
```

---

### 4. Verification & Acceptance Criteria
- [ ] Static stock buttons (`RELIANCE`, `TCS`, `HDFCBANK`, etc.) are completely removed from the top navigation bar.
- [ ] App initializes entirely from dynamic API data, displaying only actual scanned stocks matching GTF criteria.
- [ ] APScheduler cron job is registered for 16:30 IST Mon–Fri.
- [ ] No hardcoded stock arrays remain in frontend state or components.
- [ ] Deliver a Permanent Zero-Hardcoding & EOD Auto-Scan Audit Report confirming the fix.
