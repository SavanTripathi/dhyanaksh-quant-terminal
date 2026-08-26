import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import {
  TrendingUp,
  TrendingDown,
  Play,
  RotateCcw,
  BarChart3,
  Calendar,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Award,
  Layers,
  Percent,
} from 'lucide-react';

interface BacktestDashboardProps {
  initialSymbol?: string;
  theme?: 'dark' | 'light';
  onClose?: () => void;
}

export const BacktestDashboard: React.FC<BacktestDashboardProps> = ({
  initialSymbol = 'RELIANCE',
  theme = 'dark',
  onClose,
}) => {
  const isDark = theme === 'dark';

  const [symbol, setSymbol] = useState<string>(initialSymbol);
  const [lookbackDays, setLookbackDays] = useState<number>(730);
  const [minAchievements, setMinAchievements] = useState<number>(2);
  const [accountCapital, setAccountCapital] = useState<number>(500000);
  const [riskPercent, setRiskPercent] = useState<number>(1.0);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [results, setResults] = useState<any | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<'ALL' | 'WIN' | 'LOSS'>('ALL');

  // Trigger Backtest
  const handleRunBacktest = async () => {
    setIsLoading(true);
    try {
      const data = await api.runBacktest({
        symbol,
        lookback_days: lookbackDays,
        min_achievements: minAchievements,
        account_size: accountCapital,
        risk_per_trade_pct: riskPercent,
      });
      setResults(data);
    } catch (err) {
      console.error('Backtest run failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleRunBacktest();
  }, [symbol]);

  const filteredTrades = results?.trades?.filter((t: any) => {
    if (selectedFilter === 'WIN') return t.exit_reason.startsWith('WIN');
    if (selectedFilter === 'LOSS') return t.exit_reason === 'LOSS_SL';
    return true;
  }) || [];

  return (
    <div
      className={`h-full w-full flex flex-col overflow-y-auto p-4 space-y-4 transition-colors ${
        isDark ? 'bg-[#131722] text-[#d1d4dc]' : 'bg-slate-50 text-slate-800'
      }`}
    >
      {/* Header & Controls Toolbar */}
      <div
        className={`p-3.5 rounded-lg border flex flex-wrap items-center justify-between gap-3 ${
          isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
        }`}
      >
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-[#2962ff]" />
          <div>
            <h2 className={`font-bold text-sm ${isDark ? 'text-white' : 'text-slate-900'}`}>
              Historical Backtesting & Hit-Rate Analytics
            </h2>
            <p className="text-[10px] text-[#787b86]">
              Point-in-Time Event Simulator across Strict Fresh HTF Confluence Setups
            </p>
          </div>
        </div>

        {/* Inputs */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {/* Symbol */}
          <div className="flex items-center gap-1">
            <span className="text-[10px] text-[#787b86]">Stock:</span>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              className={`w-24 px-2 py-1 rounded border font-mono uppercase focus:outline-none ${
                isDark ? 'bg-[#131722] border-[#2a2e39] text-white' : 'bg-slate-50 border-slate-300'
              }`}
            />
          </div>

          {/* Lookback */}
          <div className="flex items-center gap-1">
            <span className="text-[10px] text-[#787b86]">Lookback:</span>
            <select
              value={lookbackDays}
              onChange={(e) => setLookbackDays(Number(e.target.value))}
              className={`px-2 py-1 rounded border focus:outline-none ${
                isDark ? 'bg-[#131722] border-[#2a2e39] text-white' : 'bg-slate-50 border-slate-300'
              }`}
            >
              <option value={365}>1 Year (365D)</option>
              <option value={730}>2 Years (730D)</option>
              <option value={1095}>3 Years (3Y)</option>
              <option value={1825}>5 Years (5Y)</option>
            </select>
          </div>

          {/* Min Achievements */}
          <div className="flex items-center gap-1">
            <span className="text-[10px] text-[#787b86]">Threshold:</span>
            <select
              value={minAchievements}
              onChange={(e) => setMinAchievements(Number(e.target.value))}
              className={`px-2 py-1 rounded border focus:outline-none ${
                isDark ? 'bg-[#131722] border-[#2a2e39] text-white' : 'bg-slate-50 border-slate-300'
              }`}
            >
              <option value={2}>Achievements &gt; 1 (Tier 2 & 3)</option>
              <option value={3}>Achievements &gt;= 3 (Tier 3 Only)</option>
            </select>
          </div>

          {/* Run Button */}
          <button
            onClick={handleRunBacktest}
            disabled={isLoading}
            className="flex items-center gap-1 px-3 py-1 bg-[#2962ff] hover:bg-[#1e4bd8] text-white rounded font-bold text-xs transition-colors shadow-sm disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-white" />
                Simulating...
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5" />
                Run Backtest
              </>
            )}
          </button>
        </div>
      </div>

      {/* KPI Metric Summary Cards */}
      {results && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {/* Total Setups */}
          <div
            className={`p-3 rounded-lg border font-mono ${
              isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
            }`}
          >
            <span className="text-[10px] text-[#787b86] block">TOTAL SETUPS</span>
            <span className="text-lg font-bold text-[#2962ff]">{results.total_trades}</span>
            <span className="text-[9px] text-[#787b86] block">
              {results.winning_trades_t1} Wins / {results.loss_trades_sl} Loss
            </span>
          </div>

          {/* Win Rate T1 */}
          <div
            className={`p-3 rounded-lg border font-mono ${
              isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
            }`}
          >
            <span className="text-[10px] text-[#787b86] block">WIN RATE (T1 2.0R)</span>
            <span
              className={`text-lg font-bold ${
                results.win_rate_t1 >= 60 ? 'text-emerald-400' : 'text-amber-400'
              }`}
            >
              {results.win_rate_t1}%
            </span>
            <span className="text-[9px] text-[#787b86] block">
              T2: {results.win_rate_t2}% | T3: {results.win_rate_t3}%
            </span>
          </div>

          {/* Profit Factor */}
          <div
            className={`p-3 rounded-lg border font-mono ${
              isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
            }`}
          >
            <span className="text-[10px] text-[#787b86] block">PROFIT FACTOR</span>
            <span
              className={`text-lg font-bold ${
                results.profit_factor >= 2.0 ? 'text-emerald-400' : 'text-sky-400'
              }`}
            >
              {results.profit_factor}
            </span>
            <span className="text-[9px] text-[#787b86] block">Gross Gain / Loss</span>
          </div>

          {/* Expectancy */}
          <div
            className={`p-3 rounded-lg border font-mono ${
              isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
            }`}
          >
            <span className="text-[10px] text-[#787b86] block">EXPECTANCY (R)</span>
            <span className="text-lg font-bold text-purple-400">+{results.expectancy_r} R</span>
            <span className="text-[9px] text-[#787b86] block">Per closed setup</span>
          </div>

          {/* Max Adverse Excursion */}
          <div
            className={`p-3 rounded-lg border font-mono ${
              isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
            }`}
          >
            <span className="text-[10px] text-[#787b86] block">AVG MAE (DRAWDOWN)</span>
            <span className="text-lg font-bold text-rose-400">{results.avg_mae_pct}%</span>
            <span className="text-[9px] text-[#787b86] block">Zone penetration</span>
          </div>

          {/* Avg Holding Days */}
          <div
            className={`p-3 rounded-lg border font-mono ${
              isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
            }`}
          >
            <span className="text-[10px] text-[#787b86] block">AVG HOLDING BARS</span>
            <span className="text-lg font-bold text-sky-400">{results.avg_holding_days} Days</span>
            <span className="text-[9px] text-[#787b86] block">To trade resolution</span>
          </div>
        </div>
      )}

      {/* Confluence Tier Breakdown Matrix */}
      {results?.tier_comparison && (
        <div
          className={`p-4 rounded-lg border space-y-2 ${
            isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
          }`}
        >
          <div className="flex items-center gap-2 font-bold text-xs">
            <Award className="w-4 h-4 text-amber-400" />
            <span className={isDark ? 'text-white' : 'text-slate-900'}>
              Confluence Tier Statistical Comparison Matrix
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead
                className={`border-b text-[10px] uppercase text-[#787b86] ${
                  isDark ? 'border-[#2a2e39]' : 'border-slate-200'
                }`}
              >
                <tr>
                  <th className="py-2 px-3">Confluence Tier</th>
                  <th className="py-2 px-3">Setups</th>
                  <th className="py-2 px-3">Win Rate (T1)</th>
                  <th className="py-2 px-3">Win Rate (T2)</th>
                  <th className="py-2 px-3">Profit Factor</th>
                  <th className="py-2 px-3">Expectancy (R)</th>
                  <th className="py-2 px-3">Avg Zone MAE</th>
                </tr>
              </thead>
              <tbody
                className={`divide-y text-[11px] ${
                  isDark ? 'divide-[#2a2e39]' : 'divide-slate-100'
                }`}
              >
                {results.tier_comparison.map((tier: any, idx: number) => (
                  <tr key={idx} className="hover:bg-blue-500/5">
                    <td className="py-2.5 px-3 font-semibold text-[#2962ff]">{tier.tier_name}</td>
                    <td className="py-2.5 px-3">{tier.total_setups}</td>
                    <td className="py-2.5 px-3 text-emerald-400 font-bold">{tier.win_rate_t1}%</td>
                    <td className="py-2.5 px-3 text-emerald-500">{tier.win_rate_t2}%</td>
                    <td className="py-2.5 px-3 font-bold text-sky-400">{tier.profit_factor}</td>
                    <td className="py-2.5 px-3 font-bold text-purple-400">+{tier.expectancy_r} R</td>
                    <td className="py-2.5 px-3 text-rose-400">{tier.avg_mae_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Historical Trade Execution Log Table */}
      {results?.trades && (
        <div
          className={`p-4 rounded-lg border space-y-3 flex-1 ${
            isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200 shadow-sm'
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-xs">
              <Layers className="w-4 h-4 text-[#2962ff]" />
              <span className={isDark ? 'text-white' : 'text-slate-900'}>
                Simulated Historical Trade Logs ({filteredTrades.length} Trades)
              </span>
            </div>

            {/* Filter Buttons */}
            <div className="flex items-center gap-1 text-[10px] font-mono">
              <button
                onClick={() => setSelectedFilter('ALL')}
                className={`px-2 py-0.5 rounded ${
                  selectedFilter === 'ALL'
                    ? 'bg-[#2962ff] text-white font-bold'
                    : isDark
                    ? 'bg-[#131722] text-[#787b86]'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                ALL
              </button>
              <button
                onClick={() => setSelectedFilter('WIN')}
                className={`px-2 py-0.5 rounded ${
                  selectedFilter === 'WIN'
                    ? 'bg-emerald-500 text-white font-bold'
                    : isDark
                    ? 'bg-[#131722] text-[#787b86]'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                WINS (T1/T2/T3)
              </button>
              <button
                onClick={() => setSelectedFilter('LOSS')}
                className={`px-2 py-0.5 rounded ${
                  selectedFilter === 'LOSS'
                    ? 'bg-rose-500 text-white font-bold'
                    : isDark
                    ? 'bg-[#131722] text-[#787b86]'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                LOSSES (SL)
              </button>
            </div>
          </div>

          <div className="overflow-x-auto max-h-72">
            <table className="w-full text-left text-xs font-mono">
              <thead
                className={`border-b text-[10px] uppercase text-[#787b86] sticky top-0 ${
                  isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200'
                }`}
              >
                <tr>
                  <th className="py-2 px-2.5">Date</th>
                  <th className="py-2 px-2.5">Symbol</th>
                  <th className="py-2 px-2.5">Direction</th>
                  <th className="py-2 px-2.5">Tier</th>
                  <th className="py-2 px-2.5">Entry</th>
                  <th className="py-2 px-2.5">SL</th>
                  <th className="py-2 px-2.5">Target 1</th>
                  <th className="py-2 px-2.5">Exit Reason</th>
                  <th className="py-2 px-2.5">PnL (R)</th>
                  <th className="py-2 px-2.5">Holding</th>
                  <th className="py-2 px-2.5">MAE %</th>
                </tr>
              </thead>
              <tbody
                className={`divide-y text-[10px] ${
                  isDark ? 'divide-[#2a2e39]' : 'divide-slate-100'
                }`}
              >
                {filteredTrades.map((t: any, idx: number) => {
                  const isWin = t.exit_reason.startsWith('WIN');
                  return (
                    <tr key={idx} className="hover:bg-blue-500/5">
                      <td className="py-2 px-2.5 text-[#787b86]">{t.entry_date}</td>
                      <td className="py-2 px-2.5 font-bold text-white">{t.symbol}</td>
                      <td className="py-2 px-2.5">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                            t.direction === 'DEMAND'
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : 'bg-rose-500/20 text-rose-400'
                          }`}
                        >
                          {t.direction}
                        </span>
                      </td>
                      <td className="py-2 px-2.5">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                            t.achievements >= 3
                              ? 'bg-amber-500/20 text-amber-400'
                              : 'bg-blue-500/20 text-blue-400'
                          }`}
                        >
                          {t.achievements} ACH
                        </span>
                      </td>
                      <td className="py-2 px-2.5">₹{t.entry_price.toFixed(2)}</td>
                      <td className="py-2 px-2.5 text-rose-400">₹{t.sl_price.toFixed(2)}</td>
                      <td className="py-2 px-2.5 text-sky-400">₹{t.target_1.toFixed(2)}</td>
                      <td className="py-2 px-2.5">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                            isWin
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : 'bg-rose-500/20 text-rose-400'
                          }`}
                        >
                          {t.exit_reason}
                        </span>
                      </td>
                      <td
                        className={`py-2 px-2.5 font-bold ${
                          t.pnl_r > 0 ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {t.pnl_r > 0 ? `+${t.pnl_r} R` : `${t.pnl_r} R`}
                      </td>
                      <td className="py-2 px-2.5 text-[#787b86]">{t.holding_days} d</td>
                      <td className="py-2 px-2.5 text-rose-400">{t.mae_pct.toFixed(2)}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
