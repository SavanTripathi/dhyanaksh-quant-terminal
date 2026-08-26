import React from 'react';
import { Layers, ShieldCheck, TrendingUp, TrendingDown, Target, Lock } from 'lucide-react';

interface DerivativesPanelProps {
  foData: any | null;
  theme?: 'dark' | 'light';
}

export const DerivativesPanel: React.FC<DerivativesPanelProps> = ({
  foData,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  if (!foData) return null;

  const strikes = foData.strikes || [];
  const maxOI = Math.max(
    ...strikes.map((s: any) => Math.max(s.call_oi, s.put_oi)),
    1
  );

  return (
    <div
      className={`p-3.5 rounded-lg border text-xs space-y-3 transition-colors ${
        isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
      }`}
    >
      {/* Title & Key Metrics */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-[#2962ff]" />
          <div>
            <h3 className={`font-bold text-xs ${isDark ? 'text-white' : 'text-slate-900'}`}>
              Derivatives (F&O) Open Interest Walls & Max Pain
            </h3>
            <p className="text-[10px] text-[#787b86]">
              Real-time Option Chain Resistance/Support Key Levels
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-[10px]">
          <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 font-bold border border-purple-500/30">
            PCR: {foData.pcr_oi} ({foData.buildup_type})
          </span>
        </div>
      </div>

      {/* Summary KPI Badges */}
      <div
        className={`grid grid-cols-3 gap-2 p-2 rounded border font-mono text-[11px] ${
          isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
        }`}
      >
        <div>
          <span className="text-[#787b86] text-[9px] block">PUT SUPPORT FLOOR</span>
          <span className="text-emerald-400 font-bold">₹{foData.put_support_floor.toFixed(0)}</span>
        </div>
        <div>
          <span className="text-[#787b86] text-[9px] block">MAX PAIN STRIKE</span>
          <span className="text-amber-400 font-bold">₹{foData.max_pain_strike.toFixed(0)}</span>
        </div>
        <div>
          <span className="text-[#787b86] text-[9px] block">CALL RESISTANCE WALL</span>
          <span className="text-rose-400 font-bold">₹{foData.call_resistance_wall.toFixed(0)}</span>
        </div>
      </div>

      {/* Horizontal Open Interest Strike Distribution Bars */}
      <div className="space-y-1.5 pt-1">
        <div className="flex justify-between text-[10px] font-mono text-[#787b86] pb-1 border-b border-[#2a2e39]/40">
          <span>PUT OI (SUPPORT BARS)</span>
          <span>STRIKE</span>
          <span>CALL OI (RESISTANCE BARS)</span>
        </div>

        <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
          {strikes.map((s: any, idx: number) => {
            const isSpot = Math.abs(s.strike_price - foData.spot_price) < 25;
            const isMaxPain = s.strike_price === foData.max_pain_strike;
            const isPutWall = s.strike_price === foData.put_support_floor;
            const isCallWall = s.strike_price === foData.call_resistance_wall;

            const putWidth = (s.put_oi / maxOI) * 100;
            const callWidth = (s.call_oi / maxOI) * 100;

            return (
              <div
                key={idx}
                className={`grid grid-cols-12 items-center text-[10px] font-mono py-0.5 rounded px-1 ${
                  isSpot ? 'bg-blue-500/10 border border-blue-500/30' : ''
                }`}
              >
                {/* Put OI Bar (Left) */}
                <div className="col-span-5 flex items-center justify-end gap-1">
                  <span className="text-[9px] text-[#787b86]">{(s.put_oi / 1000).toFixed(0)}k</span>
                  <div className="w-24 bg-[#2a2e39]/40 h-2.5 rounded-l overflow-hidden flex justify-end">
                    <div
                      style={{ width: `${putWidth}%` }}
                      className={`h-full rounded-l ${
                        isPutWall ? 'bg-emerald-400' : 'bg-emerald-500/60'
                      }`}
                    />
                  </div>
                </div>

                {/* Strike (Center) */}
                <div className="col-span-2 text-center font-bold text-white flex items-center justify-center gap-0.5">
                  <span className={isMaxPain ? 'text-amber-400' : isSpot ? 'text-sky-400' : ''}>
                    ₹{s.strike_price.toFixed(0)}
                  </span>
                </div>

                {/* Call OI Bar (Right) */}
                <div className="col-span-5 flex items-center justify-start gap-1">
                  <div className="w-24 bg-[#2a2e39]/40 h-2.5 rounded-r overflow-hidden">
                    <div
                      style={{ width: `${callWidth}%` }}
                      className={`h-full rounded-r ${
                        isCallWall ? 'bg-rose-400' : 'bg-rose-500/60'
                      }`}
                    />
                  </div>
                  <span className="text-[9px] text-[#787b86]">{(s.call_oi / 1000).toFixed(0)}k</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
