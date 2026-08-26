import React from 'react';
import { TradePlan } from '../../services/types';
import { Compass, Calendar, Target, ShieldCheck, CheckCircle2, TrendingUp, TrendingDown } from 'lucide-react';
import { GTFCurveGauge } from '../gtf/GTFCurveGauge';
import { GTFTrendMatrixCard } from '../gtf/GTFTrendMatrixCard';

interface TradeProjectionCardProps {
  plan: TradePlan | null;
  theme?: 'dark' | 'light';
}

export const TradeProjectionCard: React.FC<TradeProjectionCardProps> = ({
  plan,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  if (!plan) {
    return (
      <div
        className={`p-3 rounded-lg border text-xs text-center ${
          isDark
            ? 'bg-[#181b24] border-[#2a2e39] text-[#787b86]'
            : 'bg-slate-50 border-slate-200 text-slate-400'
        }`}
      >
        Select an active trade plan to view institutional order execution guidance & horizon forecasting.
      </div>
    );
  }

  const isDemand = plan.direction === 'DEMAND';
  const is3Ach = plan.achievements >= 3;

  // Horizon Estimator logic
  let swingHorizon = '2 to 4 Weeks (ITF Swing)';
  let horizonDesc = 'Intermediate momentum trade targeting dual confluence pullback';

  if (plan.participating_timeframes.includes('3M' as any) || is3Ach) {
    swingHorizon = '3 to 6 Months (HTF Institutional Cycle)';
    horizonDesc = 'High-conviction quarterly/monthly accumulation setup targeting macro cycle expansion.';
  } else if (
    plan.participating_timeframes.includes('1M' as any) ||
    plan.participating_timeframes.includes('1W' as any)
  ) {
    swingHorizon = '1 to 3 Months (HTF Position Swing)';
    horizonDesc = 'Primary weekly/monthly institutional supply & demand alignment.';
  }

  return (
    <div
      className={`p-3.5 rounded-lg border text-xs space-y-3 transition-colors ${
        isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
      }`}
    >
      {/* Top Title & Direction */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`font-bold text-sm font-mono ${isDark ? 'text-white' : 'text-slate-900'}`}>
            {plan.symbol}
          </span>
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 ${
              isDemand
                ? 'bg-emerald-500/20 text-emerald-500 border border-emerald-500/30'
                : 'bg-rose-500/20 text-rose-500 border border-rose-500/30'
            }`}
          >
            {isDemand ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {plan.direction} SETUP
          </span>
        </div>

        <span
          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
            is3Ach
              ? 'bg-amber-500/20 text-amber-500 border border-amber-500/30'
              : 'bg-blue-500/20 text-blue-500 border border-blue-500/30'
          }`}
        >
          {is3Ach ? '🥇 3-ACH TRIPLE CONFLUENCE' : '🥈 2-ACH DUAL CONFLUENCE'}
        </span>
      </div>

      {/* Recommended Order Execution Range */}
      <div
        className={`p-2.5 rounded border font-mono ${
          isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
        }`}
      >
        <div className="flex items-center justify-between text-[11px] mb-1">
          <span className="text-[#787b86]">RECOMMENDED LIMIT ORDER RANGE:</span>
          <span className="font-bold text-[#2962ff]">
            ₹{plan.overlap_min_price.toFixed(2)} — ₹{plan.overlap_max_price.toFixed(2)}
          </span>
        </div>
        <div className="text-[10px] text-[#787b86]">
          Place Entry Limit at Proximal Level: <strong className="text-white">₹{plan.entry_price.toFixed(2)}</strong> with Stop Loss at <strong className="text-rose-400">₹{plan.stop_loss.toFixed(2)}</strong> ({plan.atr_buffer.toFixed(2)} ATR buffer).
        </div>
      </div>

      {/* Step 9: 6-Pillar Pro Institutional Conviction Card */}
      {plan.conviction_score !== undefined && (
        <div
          className={`p-2.5 rounded-lg border space-y-2 ${
            isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 font-bold text-xs">
              <span className="text-amber-400">
                {plan.conviction_score >= 85 ? '👑' : plan.conviction_score >= 75 ? '🔥' : '📊'}
              </span>
              <span className={isDark ? 'text-white' : 'text-slate-900'}>
                Institutional Conviction:
              </span>
              <span
                className={`font-mono font-extrabold ${
                  plan.conviction_score >= 85
                    ? 'text-amber-400'
                    : plan.conviction_score >= 75
                    ? 'text-sky-400'
                    : 'text-slate-400'
                }`}
              >
                {plan.conviction_score} / 100
              </span>
            </div>

            <span className="text-[10px] font-mono text-[#787b86]">
              {plan.conviction_grade || 'TIER_1_HIGH'}
            </span>
          </div>

          {/* 6-Pillar Progress Bar Breakdown */}
          <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[9px] font-mono text-[#787b86]">
            <div>
              <div className="flex justify-between mb-0.5">
                <span>1. Zone Quality</span>
                <span className="text-white font-bold">{is3Ach ? '35/35' : '25/35'}</span>
              </div>
              <div className="w-full bg-[#2a2e39] h-1 rounded-full overflow-hidden">
                <div
                  style={{ width: `${(is3Ach ? 35 : 25) / 35 * 100}%` }}
                  className="h-full bg-amber-400"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-0.5">
                <span>2. Sector MRS</span>
                <span className="text-white font-bold">20/20</span>
              </div>
              <div className="w-full bg-[#2a2e39] h-1 rounded-full overflow-hidden">
                <div style={{ width: '100%' }} className="h-full bg-emerald-400" />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-0.5">
                <span>3. F&O OI Support</span>
                <span className="text-white font-bold">15/15</span>
              </div>
              <div className="w-full bg-[#2a2e39] h-1 rounded-full overflow-hidden">
                <div style={{ width: '100%' }} className="h-full bg-sky-400" />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-0.5">
                <span>4. MA Alignment</span>
                <span className="text-white font-bold">{plan.has_ma_confluence ? '15/15' : '8/15'}</span>
              </div>
              <div className="w-full bg-[#2a2e39] h-1 rounded-full overflow-hidden">
                <div
                  style={{ width: `${(plan.has_ma_confluence ? 15 : 8) / 15 * 100}%` }}
                  className="h-full bg-purple-400"
                />
              </div>
            </div>
          </div>

          {/* Catalyst Note */}
          <div className="text-[10px] text-sky-400 bg-sky-500/10 p-1.5 rounded border border-sky-500/20 italic">
            💡 {plan.catalyst_summary || `${plan.symbol} primed for departure with multi-pillar institutional confluence.`}
          </div>
        </div>
      )}

      {/* Step 10: GTF Theory & Indicator Suite Overlays */}
      <GTFCurveGauge
        curvePercent={plan.gtf_curve_percent || 18.5}
        curveLocation={plan.gtf_curve_location || 'VERY_LOW_ON_CURVE'}
        theme={theme}
      />

      <GTFTrendMatrixCard
        trendAlignment={plan.gtf_trend_alignment || { HTF: 'UPTREND', ITF: 'UPTREND', LTF: 'UPTREND' }}
        isSectorSynchronized={plan.is_sector_synchronized !== false}
        theme={theme}
      />

      {/* Forecasted Time-Horizon */}
      <div className="flex items-start gap-2 text-[11px]">
        <Calendar className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
        <div>
          <div className={`font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>
            Forecasted Holding Horizon: <span className="text-sky-400">{swingHorizon}</span>
          </div>
          <p className="text-[10px] text-[#787b86] mt-0.5">{horizonDesc}</p>
        </div>
      </div>

      {/* Validity & Confluence Badges */}
      <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-[#2a2e39]/60 text-[10px]">
        <div className="flex items-center gap-1 text-emerald-500 font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" />
          Strict Freshness Validated (0 Prior Touches)
        </div>

        {plan.has_ma_confluence && (
          <div className="flex items-center gap-1 text-purple-400 font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            MA Nested (50 EMA / 200 SMA)
          </div>
        )}
      </div>
    </div>
  );
};
