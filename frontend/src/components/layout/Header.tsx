import React from 'react';
import { RefreshCw, Bell, Terminal, ShieldCheck, Sun, Moon } from 'lucide-react';

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
}) => {
  const quickStocks = ['RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'INFY', 'LT', 'SBIN', 'BHARTIARTL'];
  const isDark = theme === 'dark';

  return (
    <header
      className={`h-12 border-b px-4 flex items-center justify-between transition-colors ${
        isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200'
      }`}
    >
      {/* Brand & Terminal Identity */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-[#2962ff] flex items-center justify-center text-white shadow-sm">
            <Terminal className="w-3.5 h-3.5" />
          </div>
          <div>
            <h1
              className={`font-extrabold text-xs tracking-tight flex items-center gap-1.5 ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}
            >
              HTF ZONE SCANNER
              <span className="px-1.5 py-0.2 bg-[#2962ff]/20 text-[#2962ff] rounded text-[9px] font-mono font-bold border border-[#2962ff]/30">
                PRO v4.0
              </span>
            </h1>
          </div>
        </div>

        <div className={`h-4 w-px mx-2 ${isDark ? 'bg-[#2a2e39]' : 'bg-slate-200'}`} />

        {/* View Switcher: Terminal Charting vs Backtest Analytics */}
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

        <div className={`h-4 w-px mx-2 hidden lg:block ${isDark ? 'bg-[#2a2e39]' : 'bg-slate-200'}`} />

        {/* Quick Switcher Buttons */}
        <div className="hidden lg:flex items-center gap-1">
          {quickStocks.map((sym) => (
            <button
              key={sym}
              onClick={() => onSymbolChange(sym)}
              className={`px-2 py-1 rounded text-xs font-mono font-semibold transition-colors ${
                selectedSymbol === sym
                  ? 'bg-[#2962ff] text-white shadow-sm'
                  : isDark
                  ? 'text-[#787b86] hover:bg-[#2a2e39] hover:text-[#d1d4dc]'
                  : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              {sym}
            </button>
          ))}
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

        {/* Run Full NIFTY 500 Batch Scan Button */}
        <button
          onClick={onTriggerBatchScan}
          disabled={isScanning}
          className="px-3.5 py-1.5 bg-gradient-to-r from-[#2962ff] to-sky-500 hover:from-[#2962ff]/90 hover:to-sky-500/90 text-white rounded-lg text-xs font-extrabold flex items-center gap-1.5 transition-all shadow-md hover:shadow-lg disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
          <span>{isScanning ? 'Scanning 500 Stocks...' : '⚡ Scan All 500 Stocks'}</span>
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
