import React from 'react';

interface GTFTrendMatrixCardProps {
  trendAlignment?: Record<string, string>;
  isSectorSynchronized?: boolean;
  theme?: 'dark' | 'light';
}

export const GTFTrendMatrixCard: React.FC<GTFTrendMatrixCardProps> = ({
  trendAlignment = { HTF: 'UPTREND', ITF: 'UPTREND', LTF: 'UPTREND' },
  isSectorSynchronized = true,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  const renderTrendPill = (label: string, trend: string) => {
    const isUp = trend === 'UPTREND';
    const isDown = trend === 'DOWNTREND';

    return (
      <div
        className={`p-2 rounded border flex flex-col items-center justify-center text-center ${
          isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-white border-slate-200'
        }`}
      >
        <span className="text-[10px] text-[#787b86] font-mono">{label}</span>
        <span
          className={`text-[11px] font-extrabold mt-0.5 ${
            isUp ? 'text-emerald-400' : isDown ? 'text-rose-400' : 'text-amber-400'
          }`}
        >
          {isUp ? '↗ UPTREND' : isDown ? '↘ DOWNTREND' : '→ SIDEWAYS'}
        </span>
      </div>
    );
  };

  return (
    <div
      className={`p-2.5 rounded-lg border text-xs space-y-2 ${
        isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-bold text-[11px] flex items-center gap-1.5">
          <span>🌊</span>
          <span className={isDark ? 'text-white' : 'text-slate-900'}>GTF 3-Step Trend Matrix:</span>
        </span>
        {isSectorSynchronized && (
          <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center gap-1">
            🔥 SECTOR SYNCHRONIZED
          </span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2">
        {renderTrendPill('HTF (Monthly/Weekly)', trendAlignment.HTF || 'UPTREND')}
        {renderTrendPill('ITF (Daily/125M)', trendAlignment.ITF || 'UPTREND')}
        {renderTrendPill('LTF (75M/15M)', trendAlignment.LTF || 'UPTREND')}
      </div>
    </div>
  );
};
