import React from 'react';
import { ShieldCheck, TrendingUp, TrendingDown, DollarSign, Activity, AlertCircle } from 'lucide-react';

interface MarketRegimeBannerProps {
  regimeData: any | null;
  theme?: 'dark' | 'light';
  onOpenSectors?: () => void;
}

export const MarketRegimeBanner: React.FC<MarketRegimeBannerProps> = ({
  regimeData,
  theme = 'dark',
  onOpenSectors,
}) => {
  const isDark = theme === 'dark';

  if (!regimeData) return null;

  const isFiiPositive = regimeData.fii_net_cash_cr > 0;
  const isDiiPositive = regimeData.dii_net_cash_cr > 0;
  const isOversoldSqueeze = regimeData.regime === 'HEAVILY_OVERSOLD';

  return (
    <div
      className={`px-4 py-1.5 border-b flex flex-wrap items-center justify-between text-xs transition-colors ${
        isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
      }`}
    >
      {/* Left: NIFTY 50 Benchmark & Regime Status */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 font-mono">
          <span className="text-[#787b86] text-[10px]">NIFTY 50:</span>
          <span className={`font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
            ₹{regimeData.nifty_50_price.toFixed(0)}
          </span>
          <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            {regimeData.nifty_50_trend}
          </span>
        </div>

        <div className={`h-3 w-px ${isDark ? 'bg-[#2a2e39]' : 'bg-slate-300'}`} />

        {/* FII L/S Ratio Indicator */}
        <div className="flex items-center gap-1.5 font-mono">
          <span className="text-[#787b86] text-[10px]">FII L/S RATIO:</span>
          <span
            className={`font-extrabold ${
              regimeData.long_short_ratio > 1.2
                ? 'text-emerald-400'
                : regimeData.long_short_ratio < 0.35
                ? 'text-rose-400'
                : 'text-amber-400'
            }`}
          >
            {regimeData.long_short_ratio}x
          </span>

          <span
            className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
              isOversoldSqueeze
                ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30 animate-pulse'
                : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
            }`}
          >
            {regimeData.regime}
          </span>
        </div>
      </div>

      {/* Right: Net Institutional Cash Flows & Sector Rotation Quick Trigger */}
      <div className="flex items-center gap-3">
        {/* FII Cash */}
        <div className="flex items-center gap-1 font-mono text-[11px]">
          <span className="text-[#787b86] text-[10px]">FII NET:</span>
          <span className={`font-bold ${isFiiPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {isFiiPositive ? `+₹${regimeData.fii_net_cash_cr} Cr` : `-₹${Math.abs(regimeData.fii_net_cash_cr)} Cr`}
          </span>
        </div>

        {/* DII Cash */}
        <div className="flex items-center gap-1 font-mono text-[11px]">
          <span className="text-[#787b86] text-[10px]">DII NET:</span>
          <span className={`font-bold ${isDiiPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {isDiiPositive ? `+₹${regimeData.dii_net_cash_cr} Cr` : `-₹${Math.abs(regimeData.dii_net_cash_cr)} Cr`}
          </span>
        </div>

        {/* Sector Rotation Button */}
        {onOpenSectors && (
          <button
            onClick={onOpenSectors}
            className="px-2 py-0.5 rounded bg-[#2962ff]/20 hover:bg-[#2962ff]/30 text-[#2962ff] font-bold text-[10px] border border-[#2962ff]/30 transition-colors flex items-center gap-1"
          >
            <Activity className="w-3 h-3" />
            MRS Sector Matrix
          </button>
        )}
      </div>
    </div>
  );
};
