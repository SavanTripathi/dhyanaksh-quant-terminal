import React from 'react';
import { Compass, TrendingUp, TrendingDown, Award, X } from 'lucide-react';

interface SectorRotationMatrixProps {
  sectorsData: any | null;
  theme?: 'dark' | 'light';
  onClose?: () => void;
}

export const SectorRotationMatrix: React.FC<SectorRotationMatrixProps> = ({
  sectorsData,
  theme = 'dark',
  onClose,
}) => {
  const isDark = theme === 'dark';

  if (!sectorsData) return null;

  const sectors = sectorsData.sectors || [];

  const leading = sectors.filter((s: any) => s.quadrant === 'OUTPERFORMING_STRENGTHENING');
  const weakening = sectors.filter((s: any) => s.quadrant === 'OUTPERFORMING_WEAKENING');
  const emerging = sectors.filter((s: any) => s.quadrant === 'UNDERPERFORMING_IMPROVING');
  const lagging = sectors.filter((s: any) => s.quadrant === 'UNDERPERFORMING_DETERIORATING');

  return (
    <div
      className={`p-4 rounded-lg border space-y-3 transition-colors ${
        isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-md'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Compass className="w-4 h-4 text-[#2962ff]" />
          <div>
            <h3 className={`font-bold text-xs ${isDark ? 'text-white' : 'text-slate-900'}`}>
              52-Week Mansfield Relative Strength (MRS) Sector Rotation
            </h3>
            <p className="text-[10px] text-[#787b86]">
              Benchmark: NIFTY 50 • 4-Quadrant Institutional Momentum Mapping
            </p>
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className={`p-1 rounded hover:bg-[#2a2e39] text-[#787b86] hover:text-white`}
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* 4-Quadrant Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
        {/* Quadrant 1: LEADING (Outperforming & Strengthening) */}
        <div
          className={`p-3 rounded-lg border ${
            isDark ? 'bg-[#131722] border-emerald-500/30' : 'bg-emerald-50 border-emerald-200'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5" />
              1. LEADING (High Conviction Demand)
            </span>
            <span className="text-[9px] font-mono text-emerald-500 font-bold px-1.5 py-0.2 rounded bg-emerald-500/10">
              MRS &gt; 0, Vel &gt; 0
            </span>
          </div>
          <div className="space-y-1">
            {leading.map((s: any, idx: number) => (
              <div
                key={idx}
                className="flex items-center justify-between text-[10px] font-mono py-0.5 border-b border-[#2a2e39]/30"
              >
                <span className="font-semibold text-white">{s.sector_name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-emerald-400 font-bold">+{s.mrs_score}%</span>
                  <span className="text-[#787b86]">Rank #{s.rank}</span>
                </div>
              </div>
            ))}
            {leading.length === 0 && (
              <p className="text-[10px] text-[#787b86] italic">No sectors currently leading.</p>
            )}
          </div>
        </div>

        {/* Quadrant 2: WEAKENING LEADER */}
        <div
          className={`p-3 rounded-lg border ${
            isDark ? 'bg-[#131722] border-amber-500/30' : 'bg-amber-50 border-amber-200'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-amber-400 flex items-center gap-1">
              <Compass className="w-3.5 h-3.5" />
              2. WEAKENING (Decelerating Leaders)
            </span>
            <span className="text-[9px] font-mono text-amber-500 font-bold px-1.5 py-0.2 rounded bg-amber-500/10">
              MRS &gt; 0, Vel &le; 0
            </span>
          </div>
          <div className="space-y-1">
            {weakening.map((s: any, idx: number) => (
              <div
                key={idx}
                className="flex items-center justify-between text-[10px] font-mono py-0.5 border-b border-[#2a2e39]/30"
              >
                <span className="font-semibold text-white">{s.sector_name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-amber-400 font-bold">+{s.mrs_score}%</span>
                  <span className="text-[#787b86]">Rank #{s.rank}</span>
                </div>
              </div>
            ))}
            {weakening.length === 0 && (
              <p className="text-[10px] text-[#787b86] italic">No weakening sectors.</p>
            )}
          </div>
        </div>

        {/* Quadrant 3: EMERGING / REVERSAL */}
        <div
          className={`p-3 rounded-lg border ${
            isDark ? 'bg-[#131722] border-sky-500/30' : 'bg-sky-50 border-sky-200'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-sky-400 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5" />
              3. EMERGING (Early Bottom Reversals)
            </span>
            <span className="text-[9px] font-mono text-sky-500 font-bold px-1.5 py-0.2 rounded bg-sky-500/10">
              MRS &le; 0, Vel &gt; 0
            </span>
          </div>
          <div className="space-y-1">
            {emerging.map((s: any, idx: number) => (
              <div
                key={idx}
                className="flex items-center justify-between text-[10px] font-mono py-0.5 border-b border-[#2a2e39]/30"
              >
                <span className="font-semibold text-white">{s.sector_name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sky-400 font-bold">{s.mrs_score}%</span>
                  <span className="text-[#787b86]">Rank #{s.rank}</span>
                </div>
              </div>
            ))}
            {emerging.length === 0 && (
              <p className="text-[10px] text-[#787b86] italic">No emerging sectors.</p>
            )}
          </div>
        </div>

        {/* Quadrant 4: LAGGING */}
        <div
          className={`p-3 rounded-lg border ${
            isDark ? 'bg-[#131722] border-rose-500/30' : 'bg-rose-50 border-rose-200'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-rose-400 flex items-center gap-1">
              <TrendingDown className="w-3.5 h-3.5" />
              4. LAGGING (Avoid Long Setups)
            </span>
            <span className="text-[9px] font-mono text-rose-500 font-bold px-1.5 py-0.2 rounded bg-rose-500/10">
              MRS &le; 0, Vel &le; 0
            </span>
          </div>
          <div className="space-y-1">
            {lagging.map((s: any, idx: number) => (
              <div
                key={idx}
                className="flex items-center justify-between text-[10px] font-mono py-0.5 border-b border-[#2a2e39]/30"
              >
                <span className="font-semibold text-white">{s.sector_name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-rose-400 font-bold">{s.mrs_score}%</span>
                  <span className="text-[#787b86]">Rank #{s.rank}</span>
                </div>
              </div>
            ))}
            {lagging.length === 0 && (
              <p className="text-[10px] text-[#787b86] italic">No lagging sectors.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
