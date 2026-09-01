import React from 'react';
import { TradePlan } from '../../services/types';

interface AlertTickerProps {
  shortlist: TradePlan[];
  onSelectStock: (stock: TradePlan) => void;
  theme?: 'dark' | 'light';
}

export const AlertTicker: React.FC<AlertTickerProps> = ({
  shortlist,
  onSelectStock,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  const inZoneStocks = shortlist.filter(
    (s) =>
      s.proximity_state === 'IN_ZONE' ||
      (s.proximity_badge && s.proximity_badge.includes('INSIDE')) ||
      (s.distance_pct !== undefined && s.distance_pct <= 0.3)
  );

  if (inZoneStocks.length === 0) return null;

  return (
    <div
      className={`w-full border-y px-3 py-1 overflow-x-auto flex items-center space-x-3 text-xs scrollbar-none transition-colors ${
        isDark
          ? 'bg-emerald-950/40 border-emerald-800/40 text-slate-200'
          : 'bg-emerald-50 border-emerald-200 text-emerald-900'
      }`}
    >
      <span className="flex items-center text-emerald-400 font-bold tracking-wider shrink-0 uppercase text-[10px]">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping mr-1.5 inline-block" />
        Live In-Zone Alerts ({inZoneStocks.length}):
      </span>
      <div className="flex items-center space-x-2 shrink-0">
        {inZoneStocks.slice(0, 30).map((stock) => {
          const isDemand = stock.direction === 'DEMAND';
          return (
            <button
              key={`${stock.symbol}_${stock.zone_timeframe}`}
              onClick={() => onSelectStock(stock)}
              className={`flex items-center space-x-1.5 border px-2 py-0.5 rounded transition-all cursor-pointer text-xs active:scale-95 ${
                isDark
                  ? 'bg-slate-900/90 hover:bg-slate-800 border-emerald-500/30 hover:border-emerald-400 text-slate-200 shadow-sm'
                  : 'bg-white hover:bg-emerald-50 border-emerald-300 hover:border-emerald-500 text-slate-800 shadow-sm'
              }`}
            >
              <span
                className={`font-bold ${
                  isDemand ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {stock.symbol}
              </span>
              <span className="text-[10px] opacity-70">
                ₹{stock.cmp || stock.current_price}
              </span>
              <span
                className={`text-[9px] px-1 rounded font-mono font-semibold ${
                  isDemand
                    ? isDark
                      ? 'bg-emerald-900/60 text-emerald-300'
                      : 'bg-emerald-100 text-emerald-800'
                    : isDark
                    ? 'bg-rose-900/60 text-rose-300'
                    : 'bg-rose-100 text-rose-800'
                }`}
              >
                {stock.zone_timeframe || '1W'}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
