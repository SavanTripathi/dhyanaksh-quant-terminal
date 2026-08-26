import React from 'react';
import { TradePlan } from '../../services/types';
import { Flame, CheckCircle2, TrendingUp, TrendingDown, Layers } from 'lucide-react';

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
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center text-xs gap-3">
        <div className="animate-spin rounded-full h-7 w-7 border-2 border-[#2962ff] border-t-transparent" />
        <div className="flex flex-col gap-1">
          <span className={`font-semibold ${isDark ? 'text-white' : 'text-slate-800'}`}>
            Ingesting Verified Market Data...
          </span>
          <span className="text-[11px] text-[#787b86]">
            Evaluating HTF Supply/Demand Confluences & Conviction Scores
          </span>
        </div>
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
        <Layers className="w-8 h-8 mb-2 opacity-40 text-[#2962ff]" />
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

              {/* Conviction Score Badge & Achievement Badge */}
              <div className="flex items-center gap-1.5">
                {plan.conviction_score !== undefined && (
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-extrabold font-mono flex items-center gap-0.5 ${
                      plan.conviction_score >= 85
                        ? 'bg-amber-400/20 text-amber-400 border border-amber-400/30'
                        : plan.conviction_score >= 75
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                    }`}
                  >
                    <Flame className="w-2.5 h-2.5" />
                    {plan.conviction_score} pts
                  </span>
                )}

                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-extrabold font-mono ${
                    is3Ach
                      ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                      : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  }`}
                >
                  {plan.achievements} ACH
                </span>
              </div>
            </div>

            {/* Card Metrics Grid: LIVE CMP, ENTRY, SL, TARGET 1 */}
            <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[11px] font-mono mb-2">
              {/* 1. Dedicated Live CMP Badge */}
              <div className={`flex items-center justify-between px-1.5 py-0.5 rounded border ${isDark ? 'bg-[#131722] border-cyan-900/60' : 'bg-cyan-50 border-cyan-200'}`}>
                <span className={`text-[10px] uppercase font-sans font-semibold ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>CMP:</span>
                <div className="flex items-center gap-1">
                  <span className="text-cyan-400 font-extrabold">₹{plan.current_price ? plan.current_price.toFixed(2) : (plan.cmp ? plan.cmp.toFixed(2) : "---")}</span>
                  {plan.change_pct !== undefined && plan.change_pct !== 0 && (
                    <span className={`text-[9px] font-bold ${plan.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {plan.change_pct >= 0 ? '+' : ''}{plan.change_pct.toFixed(2)}%
                    </span>
                  )}
                </div>
              </div>

              {/* 2. Proximal Entry */}
              <div className={`flex items-center justify-between px-1.5 py-0.5 rounded ${isDark ? 'bg-[#131722]/50' : 'bg-slate-100'}`}>
                <span className={`text-[10px] uppercase font-sans ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Entry:</span>
                <span className="text-emerald-400 font-bold">₹{plan.entry_price?.toFixed(2)}</span>
              </div>

              {/* 3. Stop Loss */}
              <div className={`flex items-center justify-between px-1.5 py-0.5 rounded ${isDark ? 'bg-[#131722]/50' : 'bg-slate-100'}`}>
                <span className={`text-[10px] uppercase font-sans ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>SL:</span>
                <span className="text-rose-400 font-bold">₹{plan.stop_loss?.toFixed(2)}</span>
              </div>

              {/* 4. Target 1 */}
              <div className={`flex items-center justify-between px-1.5 py-0.5 rounded ${isDark ? 'bg-[#131722]/50' : 'bg-slate-100'}`}>
                <span className={`text-[10px] uppercase font-sans ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>T1 (2R):</span>
                <span className="text-sky-400 font-bold">₹{plan.target_1?.toFixed(2)}</span>
              </div>
            </div>

            {/* Timeframes & Proximity / MA Tag */}
            <div className="flex items-center justify-between text-[11px] pt-1 border-t border-[#2a2e39]/50">
              <div className="flex items-center gap-1">
                {plan.participating_timeframes.map((tf) => (
                  <span
                    key={tf}
                    className={`px-1 rounded text-[9px] font-bold ${
                      tf === '3M'
                        ? 'bg-rose-500/20 text-rose-300'
                        : tf === '1M'
                        ? 'bg-amber-500/20 text-amber-300'
                        : tf === '1W'
                        ? 'bg-cyan-500/20 text-cyan-300'
                        : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    {tf}
                  </span>
                ))}
              </div>

              <div className="flex items-center gap-1.5">
                {plan.has_ma_confluence && (
                  <span
                    title={typeof plan.ma_confluence_details === 'string' ? plan.ma_confluence_details : JSON.stringify(plan.ma_confluence_details || '')}
                    className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-0.5"
                  >
                    <CheckCircle2 className="w-2.5 h-2.5" />
                    MA CONF
                  </span>
                )}

                {plan.is_approaching && (
                  <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-0.5 animate-pulse">
                    <Flame className="w-2.5 h-2.5" />
                    APPROACHING ({plan.distance_pct.toFixed(1)}%)
                  </span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
