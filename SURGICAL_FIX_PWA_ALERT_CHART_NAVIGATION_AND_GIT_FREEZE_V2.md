# SURGICAL DIRECTIVE — FIX PWA ALERT-TO-CHART NAVIGATION & FREEZE PRODUCTION RELEASE V2.0

## Project Name
**Dhyanaksh — HTF Supply & Demand Quant Terminal**

---

### Strict Implementation Rules
> **PRESERVE ALL PREVIOUS WORK:**
> - Accurate continuous market CMP (e.g. `ICICIBANK = 1434.40`).
> - SQLite database persistence and daily 16:30 IST post-market cron.
> - First-launch-of-day automated scanning engine.
> - Dynamic 37+ multi-stock live alerts.

---

### 1. Fix PWA Mobile Alert-to-Chart Navigation (`frontend/src/App.tsx` & `frontend/src/components/mobile/MobileAlertsView.tsx`)

#### Root Cause
In mobile view, clicking an alert was failing to redirect to the chart because of a tab state mismatch (e.g., casing collision between `'charts'`, `'CHARTS'`, and `'chart'`), or the click event was blocked from switching the global mobile active tab.

#### A. Mobile Alerts View Component (`frontend/src/components/mobile/MobileAlertsView.tsx`)

Ensure every alert card triggers `onSelectStock(alert.symbol)` directly:

```tsx
// frontend/src/components/mobile/MobileAlertsView.tsx
import React from 'react';

interface AlertItem {
  symbol: string;
  direction?: string;
  zone_type?: string;
  cmp?: number;
  entry_price?: number;
  distance_pct?: number;
  proximity_pct?: number;
  message?: string;
  time_display?: string;
}

interface MobileAlertsViewProps {
  alerts: AlertItem[];
  onSelectStock: (symbol: string) => void;
}

export const MobileAlertsView: React.FC<MobileAlertsViewProps> = ({
  alerts,
  onSelectStock,
}) => {
  return (
    <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-[#0B0E14] pb-24">
      <div className="flex items-center justify-between px-1 mb-1">
        <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Active Live Alerts ({alerts.length})
        </span>
      </div>

      {alerts.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-500 text-xs">
          <span>🔔 No active alerts recorded</span>
        </div>
      ) : (
        alerts.map((alert, idx) => {
          const zone = alert.direction || alert.zone_type || 'DEMAND';
          const isDemand = zone.toUpperCase().includes('DEMAND') || zone.toUpperCase().includes('BULLISH');

          return (
            <div
              key={`${alert.symbol}-${idx}`}
              onClick={() => onSelectStock(alert.symbol)}
              className="p-3 bg-[#131B2E] border border-slate-800 hover:border-cyan-500 active:border-cyan-400 rounded-lg cursor-pointer transition-all shadow-md active:scale-[0.99]"
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white text-sm tracking-wide">
                    {alert.symbol}
                  </span>
                  <span
                    className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                      isDemand
                        ? 'bg-emerald-950/90 text-emerald-400 border border-emerald-800/50'
                        : 'bg-rose-950/90 text-rose-400 border border-rose-800/50'
                    }`}
                  >
                    {zone}
                  </span>
                </div>

                <span className="text-[11px] font-mono font-bold text-cyan-400">
                  ₹{alert.cmp ? alert.cmp.toFixed(2) : '---'}
                </span>
              </div>

              <p className="text-xs text-slate-300 line-clamp-2 my-1.5 font-sans leading-relaxed">
                {alert.message ? alert.message.replace(/[{}"*]/g, '') : `Approaching ${zone} zone level`}
              </p>

              <div className="flex items-center justify-between text-[10px] pt-2 border-t border-slate-800/80 text-slate-400">
                <span className="font-mono text-emerald-400">
                  Entry: ₹{alert.entry_price ? alert.entry_price.toFixed(2) : '---'}
                </span>
                <span className="text-cyan-400 font-bold flex items-center gap-1">
                  Open Chart 📈 ➔
                </span>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};
```

#### B. Unified Tab Switch Handler in App Root (`frontend/src/App.tsx`)
Unify mobile tab identifiers so tapping an alert switches the active mobile navigation to the chart tab immediately:

```typescript
// Inside frontend/src/App.tsx

const handleAlertStockSelect = async (symbol: string) => {
  // 1. Set active stock symbol
  setSelectedSymbol(symbol);

  // 2. Hydrate trade plan and chart series
  const matchedPlan = allPlans.find((p) => p.symbol === symbol);
  if (matchedPlan) {
    setActiveTradePlan(matchedPlan);
  }
  await loadChartData(symbol, timeframe || '1D');
  await loadContextData(symbol);

  // 3. Switch Mobile View to Chart Tab (handling all casing variants)
  setActiveMobileTab('CHARTS'); 
  
  // 4. Close desktop alert drawer if open
  setIsAlertDrawerOpen(false);
};
```

---

### 2. Freeze Release & Git Tag v2.0 Execution
Once the fix is validated, execute the production freeze commands:

```bash
# 1. Run frontend production build check
npm run build

# 2. Stage and commit all codebase updates
git add .
git commit -m "feat(release): v2.0 production freeze — live settlement prices, dynamic multi-stock alerts, 1-click PWA navigation & automated EOD scanner"

# 3. Create annotated Git Tag v2.0
git tag -a v2.0 -m "Release v2.0: Dhyanaksh HTF Supply & Demand Quant Terminal"
```

---

### 3. Verification & Acceptance Criteria
- [ ] In PWA mobile view, tapping any alert card switches the active view to the chart tab and loads that stock.
- [ ] In Desktop view, clicking an alert in the Alert Center loads that stock on the main chart workspace.
- [ ] Continuous closing CMPs (e.g. `ICICIBANK = ₹1,434.40`) remain preserved.
- [ ] Automated 16:30 IST cron and first-launch-of-day scans remain functional.
- [ ] `npm run build` exits cleanly with code 0.
- [ ] Git commit and tag v2.0 completed.
- [ ] Deliver a Release v2.0 Verification Report confirming mobile navigation and Git freeze.
