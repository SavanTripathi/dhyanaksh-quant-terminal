import React from 'react';
import { Timeframe } from '../../services/types';

interface TimeframeToolbarProps {
  symbol?: string;
  cmp?: number;
  changePct?: number;
  activeTimeframe: Timeframe;
  onTimeframeChange: (tf: Timeframe) => void;
  theme?: 'dark' | 'light';
}

export const TimeframeToolbar: React.FC<TimeframeToolbarProps> = ({
  symbol,
  cmp,
  changePct = 0,
  activeTimeframe,
  onTimeframeChange,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';
  const isPositive = changePct >= 0;
  const timeframes: { label: string; value: Timeframe; category: 'HTF' | 'EXEC' }[] = [
    { label: '3M', value: '3M', category: 'HTF' },
    { label: '1M', value: '1M', category: 'HTF' },
    { label: '1W', value: '1W', category: 'HTF' },
    { label: '1D', value: '1D', category: 'EXEC' },
    { label: '125M', value: '125M', category: 'EXEC' },
    { label: '75M', value: '75M', category: 'EXEC' },
  ];

  return (
    <div
      className={`flex items-center justify-between gap-2 px-2.5 py-1.5 text-xs transition-colors overflow-x-auto no-scrollbar shrink-0 w-full ${
        isDark ? 'bg-[#1e222d]' : 'bg-slate-50'
      }`}
    >
      {/* 1. PROMINENT ACTIVE STOCK IDENTIFIER & LIVE PRICE */}
      {symbol && (
        <div className="flex items-center gap-2 pr-2 border-r border-slate-700/50 shrink-0">
          <div className="flex items-baseline gap-1">
            <span className={`text-sm sm:text-base font-extrabold tracking-wide ${isDark ? 'text-white' : 'text-slate-900'}`}>
              {symbol}
            </span>
            <span className="text-[9px] font-semibold text-slate-400 bg-slate-800/80 px-1 py-0.2 rounded border border-slate-700/50">
              NSE
            </span>
          </div>

          {cmp !== undefined && (
            <div className="flex items-center gap-1 text-[11px] sm:text-xs font-bold font-mono">
              <span className="text-cyan-400">₹{cmp.toFixed(2)}</span>
              <span
                className={`text-[9px] px-1 py-0.2 rounded font-semibold ${
                  isPositive
                    ? 'text-emerald-400 bg-emerald-950/60 border border-emerald-800/50'
                    : 'text-rose-400 bg-rose-950/60 border border-rose-800/50'
                }`}
              >
                {isPositive ? `+${changePct.toFixed(2)}%` : `${changePct.toFixed(2)}%`}
              </span>
            </div>
          )}
        </div>
      )}

      {/* 2. TIMEFRAME SELECTORS */}
      <div className="flex items-center gap-1 shrink-0">
        <div
          className={`flex items-center gap-0.5 p-0.5 rounded border ${
            isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-white border-slate-300'
          }`}
        >
          {timeframes.map((tf) => {
            const isActive = activeTimeframe === tf.value;
            return (
              <button
                key={tf.value}
                onClick={() => onTimeframeChange(tf.value)}
                className={`px-1.5 sm:px-2.5 py-0.5 sm:py-1 text-[10px] sm:text-xs rounded font-mono font-medium transition-all ${
                  isActive
                    ? 'bg-[#2962ff] text-white shadow-sm font-bold'
                    : isDark
                    ? 'text-[#d1d4dc] hover:bg-[#2a2e39] hover:text-white'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                {tf.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
