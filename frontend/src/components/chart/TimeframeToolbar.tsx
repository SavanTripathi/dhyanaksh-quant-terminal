import React from 'react';
import { Timeframe } from '../../services/types';

interface TimeframeToolbarProps {
  activeTimeframe: Timeframe;
  onTimeframeChange: (tf: Timeframe) => void;
  theme?: 'dark' | 'light';
}

export const TimeframeToolbar: React.FC<TimeframeToolbarProps> = ({
  activeTimeframe,
  onTimeframeChange,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';
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
      className={`flex items-center gap-1.5 px-3 py-2 border-b text-xs transition-colors ${
        isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
      }`}
    >
      <span className="text-[#787b86] font-semibold text-[10px] uppercase tracking-wider mr-1">
        Timeframe:
      </span>
      <div
        className={`flex items-center gap-1 p-0.5 rounded border ${
          isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-white border-slate-300'
        }`}
      >
        {timeframes.map((tf) => {
          const isActive = activeTimeframe === tf.value;
          return (
            <button
              key={tf.value}
              onClick={() => onTimeframeChange(tf.value)}
              className={`px-2.5 py-1 rounded font-mono font-medium transition-all ${
                isActive
                  ? 'bg-[#2962ff] text-white shadow-sm'
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
  );
};
