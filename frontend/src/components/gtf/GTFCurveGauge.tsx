import React from 'react';

interface GTFCurveGaugeProps {
  curvePercent?: number;
  curveLocation?: string;
  theme?: 'dark' | 'light';
}

export const GTFCurveGauge: React.FC<GTFCurveGaugeProps> = ({
  curvePercent = 18.5,
  curveLocation = 'VERY_LOW_ON_CURVE',
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  const isLow = curveLocation === 'VERY_LOW_ON_CURVE' || curvePercent <= 33.3;
  const isHigh = curveLocation === 'VERY_HIGH_ON_CURVE' || curvePercent >= 66.7;

  return (
    <div
      className={`p-2.5 rounded-lg border text-xs space-y-2 ${
        isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-bold text-[11px] flex items-center gap-1.5">
          <span>📐</span>
          <span className={isDark ? 'text-white' : 'text-slate-900'}>GTF Location on Curve:</span>
        </span>
        <span
          className={`px-2 py-0.5 rounded text-[10px] font-mono font-extrabold ${
            isLow
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : isHigh
              ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
              : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
          }`}
        >
          {curveLocation.replace(/_/g, ' ')} ({curvePercent.toFixed(1)}%)
        </span>
      </div>

      {/* Horizontal Multi-Band Curve Meter */}
      <div className="relative w-full h-3.5 bg-[#1e222d] rounded overflow-hidden flex border border-[#2a2e39]">
        {/* Demand Zone (0 - 33.3%) */}
        <div className="w-1/3 h-full bg-emerald-500/40 border-r border-[#2a2e39] flex items-center justify-center text-[8px] font-bold text-emerald-300">
          DEMAND
        </div>
        {/* Equilibrium (33.3 - 66.7%) */}
        <div className="w-1/3 h-full bg-amber-500/30 border-r border-[#2a2e39] flex items-center justify-center text-[8px] font-bold text-amber-300">
          EQ
        </div>
        {/* Supply Zone (66.7 - 100%) */}
        <div className="w-1/3 h-full bg-rose-500/40 flex items-center justify-center text-[8px] font-bold text-rose-300">
          SUPPLY
        </div>

        {/* Needle Marker */}
        <div
          style={{ left: `${Math.max(2, Math.min(98, curvePercent))}%` }}
          className="absolute top-0 bottom-0 w-1.5 bg-white shadow-[0_0_8px_rgba(255,255,255,0.9)] -ml-0.5 rounded-full"
        />
      </div>

      <div className="flex justify-between text-[9px] text-[#787b86] font-mono">
        <span>0% (HTF Demand Floor)</span>
        <span>50% (Equilibrium)</span>
        <span>100% (HTF Supply Ceiling)</span>
      </div>
    </div>
  );
};
