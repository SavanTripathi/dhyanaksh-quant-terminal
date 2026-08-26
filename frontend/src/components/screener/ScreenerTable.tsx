import React from 'react';
import { TradePlan } from '../../services/types';
import { Flame, CheckCircle2, TrendingUp, TrendingDown } from 'lucide-react';

interface ScreenerTableProps {
  plans: TradePlan[];
  selectedSymbol: string;
  onSelectPlan: (plan: TradePlan) => void;
  isLoading: boolean;
  theme?: 'dark' | 'light';
}

export const ScreenerTable: React.FC<ScreenerTableProps> = ({
  plans,
  selectedSymbol,
  onSelectPlan,
  isLoading,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-[#787b86] text-xs">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-[#2962ff] mr-2" />
        Scanning NIFTY 500 Confluences...
      </div>
    );
  }

  if (plans.length === 0) {
    return (
      <div
        className={`flex-1 flex flex-col items-center justify-center p-6 text-center text-xs ${
          isDark ? 'text-[#787b86]' : 'text-slate-400'
        }`}
      >
        <p className={`font-semibold text-sm mb-1 ${isDark ? 'text-[#d1d4dc]' : 'text-slate-700'}`}>
          No Trade Plans Found
        </p>
        <p>No securities currently match the selected filter criteria with Achievements &gt; 1.</p>
      </div>
    );
  }

  return (
    <div
      className={`flex-1 overflow-y-auto overflow-x-hidden divide-y ${
        isDark ? 'divide-[#2a2e39]' : 'divide-slate-200'
      }`}
    >
      {plans.map((plan) => {
        const isSelected = selectedSymbol === plan.symbol;
        const isDemand = plan.direction === 'DEMAND';
        const is3Ach = plan.achievements >= 3;

        return (
          <div
            key={`${plan.symbol}-${plan.direction}-${plan.entry_price}`}
            onClick={() => onSelectPlan(plan)}
            className={`p-3 cursor-pointer transition-all ${
              isSelected
                ? isDark
                  ? 'bg-[#2a2e39] border-l-4 border-[#2962ff]'
                  : 'bg-blue-50 border-l-4 border-blue-600'
                : isDark
                ? 'bg-[#1e222d] hover:bg-[#2a2e39]/60'
                : 'bg-white hover:bg-slate-50'
            }`}
          >
            {/* Top row: Symbol, Direction, Tier Badge */}
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span
                  className={`font-bold text-sm font-mono ${
                    isDark ? 'text-white' : 'text-slate-900'
                  }`}
                >
                  {plan.symbol}
                </span>
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 ${
                    isDemand
                      ? 'bg-emerald-500/20 text-emerald-500'
                      : 'bg-rose-500/20 text-rose-500'
                  }`}
                >
                  {isDemand ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  {plan.direction}
                </span>
              </div>

              {/* Step 9: Conviction Score Badge & Achievement Badge */}
              <div className="flex items-center gap-1.5">
                {plan.conviction_score !== undefined && (
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-extrabold font-mono flex items-center gap-0.5 ${
                      plan.conviction_score >= 85
                        ? 'bg-amber-400/20 text-amber-400 border border-amber-400/30'
                        : plan.conviction_score >= 75
                        ? 'bg-sky-400/20 text-sky-400 border border-sky-400/30'
                        : 'bg-slate-500/20 text-slate-400 border border-slate-500/30'
                    }`}
                  >
                    {plan.conviction_score >= 85 ? '👑' : plan.conviction_score >= 75 ? '🔥' : '📊'}{' '}
                    {plan.conviction_score}
                  </span>
                )}

                <span
                  className={`px-1.5 py-0.5 rounded text-[9px] font-bold flex items-center gap-1 ${
                    is3Ach
                      ? 'bg-amber-500/20 text-amber-500 border border-amber-500/30'
                      : 'bg-blue-500/20 text-blue-500 border border-blue-500/30'
                  }`}
                >
                  {is3Ach ? '🥇 3-ACH' : '🥈 2-ACH'}
                </span>
              </div>
            </div>

            {/* Timeframe Badges & Approaching Pill */}
            <div className="flex items-center justify-between text-[11px] mb-2">
              <div className="flex items-center gap-1">
                {plan.participating_timeframes.map((tf) => (
                  <span
                    key={tf}
                    className={`px-1.5 py-0.2 rounded border font-mono text-[10px] ${
                      isDark
                        ? 'bg-[#131722] border-[#2a2e39] text-[#d1d4dc]'
                        : 'bg-slate-100 border-slate-200 text-slate-700'
                    }`}
                  >
                    #{tf}
                  </span>
                ))}
              </div>

              {plan.is_approaching && (
                <span className="px-2 py-0.5 bg-amber-500/20 text-amber-600 dark:text-amber-300 font-semibold text-[10px] rounded-full flex items-center gap-1 animate-pulse">
                  <Flame className="w-3 h-3" />
                  {plan.distance_pct.toFixed(2)}% Away
                </span>
              )}
            </div>

            {/* Quantitative Level Matrix with Live CMP */}
            <div
              className={`grid grid-cols-4 gap-1 text-[11px] p-2 rounded border font-mono ${
                isDark
                  ? 'bg-[#131722] border-[#2a2e39]/60'
                  : 'bg-slate-50 border-slate-200'
              }`}
            >
              <div>
                <span className="text-[#38bdf8] text-[9px] font-bold block">LIVE CMP</span>
                <span className="font-bold text-[#38bdf8]">
                  ₹{plan.current_price.toFixed(2)}
                </span>
              </div>
              <div>
                <span className="text-[#787b86] text-[9px] block">ENTRY</span>
                <span className={`font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                  ₹{plan.entry_price.toFixed(2)}
                </span>
              </div>
              <div>
                <span className="text-[#787b86] text-[9px] block">SL (0.2ATR)</span>
                <span className="text-rose-500 font-semibold">₹{plan.stop_loss.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-[#787b86] text-[9px] block">T1 [2.0R]</span>
                <span className="text-sky-500 font-semibold">₹{plan.target_1.toFixed(2)}</span>
              </div>
            </div>

            {/* Bottom Row: MA Confluence Status */}
            {plan.has_ma_confluence && (
              <div className="mt-2 flex items-center gap-1 text-[10px] text-purple-500 font-medium">
                <CheckCircle2 className="w-3 h-3" />
                50 EMA / 200 SMA Confluence Inside Zone
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
