import React from 'react';
import { RefreshCw, Bell, ShieldCheck, Sun, Moon } from 'lucide-react';

interface HeaderProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
  onTriggerBatchScan: () => void;
  onToggleAlertDrawer: () => void;
  isScanning: boolean;
  activeAlertCount: number;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
  activeView: 'TERMINAL' | 'BACKTEST';
  onToggleView: (v: 'TERMINAL' | 'BACKTEST') => void;
  analysisMode: 'EOD' | 'LIVE';
  onToggleAnalysisMode: (mode: 'EOD' | 'LIVE') => void;
  asOfDate: string;
  regimeData?: any | null;
}

export const Header: React.FC<HeaderProps> = ({
  selectedSymbol,
  onSymbolChange,
  onTriggerBatchScan,
  onToggleAlertDrawer,
  isScanning,
  activeAlertCount,
  theme,
  onToggleTheme,
  activeView,
  onToggleView,
  analysisMode,
  onToggleAnalysisMode,
  asOfDate,
  regimeData,
}) => {
  const isDark = theme === 'dark';

  return (
    <header
      className={`h-12 border-b px-4 flex items-center justify-between transition-colors ${
        isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200'
      }`}
    >
      {/* Brand & Terminal Identity */}
      <div className="flex items-center gap-3">
        {/* Logo Icon / Symbol */}
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30 shrink-0">
          <span className="text-white font-black text-base tracking-tighter">ध</span>
        </div>

        {/* Brand Name & Tagline Stack */}
        <div className="flex flex-col justify-center">
          <div className="flex items-center gap-2 leading-none">
            <span className="font-extrabold text-sm md:text-base tracking-wider bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-500 bg-clip-text text-transparent">
              DHYANAKSH
            </span>
            <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-blue-950/80 text-cyan-300 border border-cyan-800/60 uppercase">
              PRO v4.0
            </span>
          </div>
          <span className="text-[9.5px] font-medium text-slate-400 tracking-tight mt-0.5 select-none hidden sm:inline">
            The Meditative Eye for Precision Market Pivots.
          </span>
        </div>

        <div className={`h-4 w-px mx-2 ${isDark ? 'bg-[#2a2e39]' : 'bg-slate-200'}`} />

        {/* Active Tabs: Live Terminal vs Backtest Analytics */}
        <div className="flex items-center gap-1 bg-[#131722] p-0.5 rounded border border-[#2a2e39]">
          <button
            onClick={() => onToggleView('TERMINAL')}
            className={`px-2.5 py-1 rounded text-xs font-bold transition-colors ${
              activeView === 'TERMINAL'
                ? 'bg-[#2962ff] text-white shadow-sm'
                : 'text-[#787b86] hover:text-white'
            }`}
          >
            Live Terminal
          </button>
          <button
            onClick={() => onToggleView('BACKTEST')}
            className={`px-2.5 py-1 rounded text-xs font-bold transition-colors ${
              activeView === 'BACKTEST'
                ? 'bg-[#2962ff] text-white shadow-sm'
                : 'text-[#787b86] hover:text-white'
            }`}
          >
            Backtest Analytics
          </button>
        </div>

        <div className={`h-4 w-px mx-1.5 ${isDark ? 'bg-[#2a2e39]' : 'bg-slate-200'}`} />

        {/* Dual Analysis Mode Switcher: EOD Analysis vs LIVE Analysis */}
        <div className="flex items-center gap-1.5">
          <div className="flex items-center bg-[#131722] p-0.5 rounded border border-[#2a2e39]">
            <button
              onClick={() => onToggleAnalysisMode('EOD')}
              title={`EOD Mode: Strict immutable snapshot as of ${asOfDate} EOD`}
              className={`px-2 py-0.5 rounded text-[11px] font-extrabold flex items-center gap-1.5 transition-all ${
                analysisMode === 'EOD'
                  ? 'bg-blue-600 text-white shadow-sm border border-blue-400/40'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-blue-300 animate-pulse" />
              EOD ANALYSIS
            </button>
            <button
              onClick={() => onToggleAnalysisMode('LIVE')}
              title="LIVE Mode: Latest streaming intraday and current session candles"
              className={`px-2 py-0.5 rounded text-[11px] font-extrabold flex items-center gap-1.5 transition-all ${
                analysisMode === 'LIVE'
                  ? 'bg-emerald-600 text-white shadow-sm border border-emerald-400/40'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-300 animate-pulse" />
              LIVE ANALYSIS
            </button>
          </div>

          <div className="hidden lg:flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-[#131722] border border-[#2a2e39]">
            <span className="text-slate-400">{analysisMode === 'EOD' ? 'As-Of:' : 'Market:'}</span>
            <span className={`font-bold ${analysisMode === 'EOD' ? 'text-blue-400' : 'text-emerald-400'}`}>
              {analysisMode === 'EOD' ? `${asOfDate} EOD` : 'OPEN (Live Stream)'}
            </span>
          </div>
        </div>

        <div className={`h-4 w-px mx-2 hidden xl:block ${isDark ? 'bg-[#2a2e39]' : 'bg-slate-200'}`} />

        {/* Global Market Regime & Net Flow Indicators (Dynamic) */}
        <div className="hidden xl:flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 font-mono">
            <span className="text-[#787b86] text-[11px]">NIFTY 50:</span>
            <span className={`font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
              {regimeData?.nifty_50_price ? `₹${Number(regimeData.nifty_50_price).toFixed(0)}` : 'Bullish Consolidation'}
            </span>
            {regimeData?.nifty_50_trend && (
              <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {regimeData.nifty_50_trend}
              </span>
            )}
          </div>

          <div className={`h-3 w-px ${isDark ? 'bg-[#2a2e39]' : 'bg-slate-300'}`} />

          <div className="flex items-center gap-1.5 font-mono">
            <span className="text-[#787b86] text-[11px]">FII/DII Net Flow:</span>
            <span className="font-extrabold text-emerald-400">
              {regimeData?.fii_net_cash_cr ? `${regimeData.fii_net_cash_cr > 0 ? '+' : ''}₹${regimeData.fii_net_cash_cr} Cr` : 'Institutional Support'}
            </span>
          </div>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2.5">
        {/* Theme Toggle (Light / Dark) */}
        <button
          onClick={onToggleTheme}
          title={`Switch to ${isDark ? 'Light' : 'Dark'} Mode`}
          className={`p-1.5 rounded border transition-colors flex items-center gap-1.5 text-xs font-medium ${
            isDark
              ? 'bg-[#131722] border-[#2a2e39] text-amber-400 hover:bg-[#2a2e39]'
              : 'bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200'
          }`}
        >
          {isDark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
          <span className="hidden md:inline text-[11px]">{isDark ? 'Light' : 'Dark'}</span>
        </button>

        {/* Backend Connectivity Status */}
        <div className="flex items-center gap-1.5 text-xs text-emerald-500 font-semibold bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Engine Live (NSE Equities)</span>
        </div>

        {/* Action Button: Scan / Refresh 500 Stocks */}
        <button
          onClick={onTriggerBatchScan}
          disabled={isScanning}
          title="Refresh and scan full NIFTY 500 universe"
          className="px-2 sm:px-3.5 py-1.5 bg-gradient-to-r from-[#2962ff] to-sky-500 hover:from-[#2962ff]/90 hover:to-sky-500/90 text-white rounded-lg text-xs font-extrabold flex items-center gap-1.5 transition-all shadow-md hover:shadow-lg disabled:opacity-50 shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">{isScanning ? 'Scanning 500 Stocks...' : 'Scan All 500 Stocks'}</span>
          <span className="sm:hidden">{isScanning ? 'Scanning...' : 'Refresh'}</span>
        </button>

        {/* Alert Center Trigger */}
        <button
          onClick={onToggleAlertDrawer}
          className={`relative p-1.5 border rounded transition-colors ${
            isDark
              ? 'bg-[#131722] hover:bg-[#2a2e39] border-[#2a2e39] text-[#d1d4dc]'
              : 'bg-slate-100 hover:bg-slate-200 border-slate-300 text-slate-700'
          }`}
        >
          <Bell className="w-4 h-4" />
          {activeAlertCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-amber-500 text-black text-[9px] font-extrabold rounded-full flex items-center justify-center">
              {activeAlertCount}
            </span>
          )}
        </button>
      </div>
    </header>
  );
};
