import React from 'react';
import { AlertNotification, TradePlan } from '../../services/types';

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
  payload?: any;
  rendered_message?: string;
}

interface MobileAlertsViewProps {
  alerts: (AlertNotification | AlertItem)[];
  activePlans?: TradePlan[];
  onSelectStock?: (symbol: string) => void;
  onSelectStockAndGoToChart?: (symbol: string) => void;
  onTriggerTestAlert?: (channel: string) => void;
  isLoading?: boolean;
  theme?: 'dark' | 'light';
}

export const MobileAlertsView: React.FC<MobileAlertsViewProps> = ({
  alerts,
  activePlans = [],
  onSelectStock,
  onSelectStockAndGoToChart,
  onTriggerTestAlert,
  isLoading = false,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  const handleStockClick = (symbol: string) => {
    if (onSelectStock) {
      onSelectStock(symbol);
    } else if (onSelectStockAndGoToChart) {
      onSelectStockAndGoToChart(symbol);
    }
  };

  // Filter alerts strictly to Demand Zone stocks
  const demandPlans = activePlans.filter((p) => p.direction === 'DEMAND' || !p.direction);
  
  const rawAlertItems = alerts.length > 0
    ? alerts.filter((a) => {
        const planMatch = activePlans.find((p) => p.symbol === a.symbol);
        const dir = (a as any).direction || (a as any).zone_type || planMatch?.direction || 'DEMAND';
        return dir.toUpperCase().includes('DEMAND') || dir.toUpperCase().includes('BULLISH');
      })
    : demandPlans.map((p) => ({
        symbol: p.symbol,
        direction: 'DEMAND',
        zone_type: 'DEMAND',
        cmp: p.current_price || p.cmp,
        entry_price: p.entry_price,
        distance_pct: p.distance_pct,
        message: `Fresh Demand Zone (${p.achievements}-ACH) entry at ₹${p.entry_price?.toFixed(2)} (${p.distance_pct?.toFixed(2)}% away).`
      }));

  const alertItems = rawAlertItems.length > 0 ? rawAlertItems : demandPlans.slice(0, 15).map((p) => ({
    symbol: p.symbol,
    direction: 'DEMAND',
    zone_type: 'DEMAND',
    cmp: p.current_price || p.cmp,
    entry_price: p.entry_price,
    distance_pct: p.distance_pct,
    message: `High-Conviction Demand Setup: ₹${p.entry_price?.toFixed(2)}`
  }));

  return (
    <div className={`flex-1 overflow-y-auto p-3 space-y-3 pb-24 ${isDark ? 'bg-[#0B0E14]' : 'bg-slate-50'}`}>
      <div className="flex items-center justify-between px-1 mb-1">
        <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Active Live Alerts ({alertItems.length})
        </span>
        {onTriggerTestAlert && (
          <button
            onClick={() => onTriggerTestAlert('IN_APP')}
            disabled={isLoading}
            className="px-2.5 py-1 bg-[#2962ff] text-white text-xs font-bold rounded flex items-center gap-1 shadow-sm"
          >
            Test In-App
          </button>
        )}
      </div>

      {alertItems.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-500 text-xs">
          <span>🔔 No active alerts recorded</span>
        </div>
      ) : (
        alertItems.map((alert: any, idx: number) => {
          const planMatch = activePlans.find((p) => p.symbol === alert.symbol);
          const zone = alert.direction || alert.zone_type || planMatch?.direction || (alert.payload as any)?.direction || 'DEMAND';
          const isDemand = zone.toUpperCase().includes('DEMAND') || zone.toUpperCase().includes('BULLISH');
          
          const rawCmp = alert.cmp || alert.current_price || planMatch?.current_price || (alert.payload as any)?.cmp || (alert.payload as any)?.current_price;
          const rawEntry = alert.entry_price || planMatch?.entry_price || (alert.payload as any)?.entry_price;

          const rawMessage = typeof alert.rendered_message === 'string'
            ? alert.rendered_message
            : typeof alert.message === 'string'
            ? alert.message
            : typeof alert.payload?.message === 'string'
            ? alert.payload.message
            : `Approaching ${zone} zone level`;

          const cleanMessage = rawMessage.replace(/[{}"*]/g, '');

          return (
            <div
              key={`${alert.symbol}-${idx}`}
              onClick={() => handleStockClick(alert.symbol)}
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
                  ₹{rawCmp ? Number(rawCmp).toFixed(2) : '---'}
                </span>
              </div>

              <p className="text-xs text-slate-300 line-clamp-2 my-1.5 font-sans leading-relaxed">
                {cleanMessage}
              </p>

              <div className="flex items-center justify-between text-[10px] pt-2 border-t border-slate-800/80 text-slate-400">
                <span className="font-mono text-emerald-400 font-semibold">
                  Entry: ₹{rawEntry ? Number(rawEntry).toFixed(2) : '---'}
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
