import React, { useState } from 'react';
import { TradePlan } from '../../services/types';
import { Calculator, DollarSign, Percent, ArrowUpRight } from 'lucide-react';

interface RiskRewardSummaryProps {
  plan: TradePlan | null;
  theme?: 'dark' | 'light';
}

export const RiskRewardSummary: React.FC<RiskRewardSummaryProps> = ({
  plan,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';
  const [accountSize, setAccountSize] = useState<number>(500000); // default ₹5 Lakhs
  const [riskPercent, setRiskPercent] = useState<number>(1.0); // default 1%

  if (!plan) return null;

  const riskAmount = (accountSize * riskPercent) / 100.0;
  const riskPerShare = Math.max(plan.risk_per_share, 0.05);
  const positionQty = Math.floor(riskAmount / riskPerShare);
  const totalCapitalRequired = positionQty * plan.entry_price;

  const profitT1 = positionQty * Math.abs(plan.target_1 - plan.entry_price);
  const profitT2 = positionQty * Math.abs(plan.target_2 - plan.entry_price);
  const profitT3 = positionQty * Math.abs(plan.target_3 - plan.entry_price);

  return (
    <div
      className={`p-3.5 rounded-lg border text-xs space-y-3 transition-colors ${
        isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
      }`}
    >
      {/* Title */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 font-bold">
          <Calculator className="w-4 h-4 text-[#2962ff]" />
          <span className={isDark ? 'text-white' : 'text-slate-900'}>
            Quantitative Position Sizing & Target Payoffs
          </span>
        </div>
        <span className="text-[10px] text-[#787b86] font-mono">
          Risk/Share: ₹{plan.risk_per_share.toFixed(2)}
        </span>
      </div>

      {/* Inputs for Capital & Risk % */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div>
          <label className="text-[10px] text-[#787b86] block mb-1">Account Capital (₹):</label>
          <input
            type="number"
            value={accountSize}
            onChange={(e) => setAccountSize(Math.max(Number(e.target.value), 1000))}
            className={`w-full px-2.5 py-1 rounded border font-mono text-xs focus:outline-none ${
              isDark
                ? 'bg-[#131722] border-[#2a2e39] text-white focus:border-[#2962ff]'
                : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-blue-500'
            }`}
          />
        </div>
        <div>
          <label className="text-[10px] text-[#787b86] block mb-1">Risk per Trade (%):</label>
          <input
            type="number"
            step="0.25"
            value={riskPercent}
            onChange={(e) => setRiskPercent(Math.max(Number(e.target.value), 0.1))}
            className={`w-full px-2.5 py-1 rounded border font-mono text-xs focus:outline-none ${
              isDark
                ? 'bg-[#131722] border-[#2a2e39] text-white focus:border-[#2962ff]'
                : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-blue-500'
            }`}
          />
        </div>
      </div>

      {/* Sizing Results */}
      <div
        className={`grid grid-cols-3 gap-2 p-2 rounded border font-mono text-[11px] ${
          isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
        }`}
      >
        <div>
          <span className="text-[#787b86] text-[9px] block">MAX RISK</span>
          <span className="text-rose-400 font-bold">₹{riskAmount.toFixed(0)}</span>
        </div>
        <div>
          <span className="text-[#787b86] text-[9px] block">POSITION QTY</span>
          <span className={`font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
            {positionQty} Shares
          </span>
        </div>
        <div>
          <span className="text-[#787b86] text-[9px] block">CAPITAL OUTLAY</span>
          <span className="text-sky-400 font-bold">₹{totalCapitalRequired.toFixed(0)}</span>
        </div>
      </div>

      {/* Projected Multi-Tier Rewards */}
      <div className="grid grid-cols-3 gap-2 text-center font-mono">
        {/* T1 */}
        <div
          className={`p-2 rounded border ${
            isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-sky-50 border-sky-200'
          }`}
        >
          <span className="text-[10px] font-bold text-sky-400 block">T1 [2.0R]</span>
          <span className="text-xs font-bold text-sky-500">₹{plan.target_1.toFixed(2)}</span>
          <span className="text-[10px] text-emerald-400 block mt-0.5">+₹{profitT1.toFixed(0)}</span>
        </div>

        {/* T2 */}
        <div
          className={`p-2 rounded border ${
            isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-emerald-50 border-emerald-200'
          }`}
        >
          <span className="text-[10px] font-bold text-emerald-400 block">T2 [3.5R]</span>
          <span className="text-xs font-bold text-emerald-500">₹{plan.target_2.toFixed(2)}</span>
          <span className="text-[10px] text-emerald-400 block mt-0.5">+₹{profitT2.toFixed(0)}</span>
        </div>

        {/* T3 */}
        <div
          className={`p-2 rounded border ${
            isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-amber-50 border-amber-200'
          }`}
        >
          <span className="text-[10px] font-bold text-amber-400 block">T3 [5.0R]</span>
          <span className="text-xs font-bold text-amber-500">₹{plan.target_3.toFixed(2)}</span>
          <span className="text-[10px] text-emerald-400 block mt-0.5">+₹{profitT3.toFixed(0)}</span>
        </div>
      </div>
    </div>
  );
};
