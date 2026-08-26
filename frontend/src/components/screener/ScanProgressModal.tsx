import React from 'react';
import { Loader2, Zap, CheckCircle2, AlertCircle } from 'lucide-react';

interface ScanProgressModalProps {
  isOpen: boolean;
  progress: {
    is_running: boolean;
    current_index: number;
    total: number;
    current_symbol: string;
    percentage: number;
    found_count: number;
    status_message: string;
  };
  theme?: 'dark' | 'light';
  onClose?: () => void;
}

export const ScanProgressModal: React.FC<ScanProgressModalProps> = ({
  isOpen,
  progress,
  theme = 'dark',
  onClose,
}) => {
  const isDark = theme === 'dark';

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div
        className={`max-w-md w-full p-5 rounded-xl border shadow-2xl space-y-4 transition-colors ${
          isDark ? 'bg-[#1e222d] border-[#2a2e39] text-[#d1d4dc]' : 'bg-white border-slate-200 text-slate-800'
        }`}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-[#2962ff]/20 text-[#2962ff]">
              <Zap className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h3 className={`font-bold text-sm ${isDark ? 'text-white' : 'text-slate-900'}`}>
                NIFTY 500 EOD Multi-Timeframe Scan
              </h3>
              <p className="text-[11px] text-[#787b86]">
                Strict Zero-Touch Freshness • Confluences &gt; 1 Only
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="font-mono text-xs font-bold text-[#2962ff] px-2 py-0.5 rounded bg-[#2962ff]/10 border border-[#2962ff]/20">
              {progress.percentage}%
            </span>
            {onClose && (
              <button
                onClick={onClose}
                className="text-[#787b86] hover:text-white p-1 rounded transition-colors text-sm font-bold"
                title="Dismiss Modal"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Dynamic Progress Bar */}
        <div className="space-y-1.5">
          <div className="w-full bg-[#131722] h-3 rounded-full overflow-hidden border border-[#2a2e39] p-0.5">
            <div
              style={{ width: `${Math.max(5, progress.percentage)}%` }}
              className="h-full rounded-full bg-gradient-to-r from-[#2962ff] via-sky-400 to-emerald-400 transition-all duration-300 shadow-sm"
            />
          </div>

          <div className="flex justify-between text-[11px] font-mono text-[#787b86]">
            <span>{progress.status_message}</span>
            <span>
              {progress.current_index} / {progress.total} Stocks
            </span>
          </div>
        </div>

        {/* Live Counters */}
        <div
          className={`grid grid-cols-2 gap-2 p-3 rounded-lg border font-mono text-xs ${
            isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
          }`}
        >
          <div>
            <span className="text-[10px] text-[#787b86] block">CURRENT TICKER</span>
            <span className="font-bold text-sky-400">
              {progress.current_symbol || 'INITIALIZING'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-[#787b86] block">SETUPS IDENTIFIED</span>
            <span className="font-bold text-emerald-400">
              {progress.found_count} Qualified Plans
            </span>
          </div>
        </div>

        {/* Completion Action */}
        {!progress.is_running && progress.percentage >= 100 && (
          <button
            onClick={onClose}
            className="w-full py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-xs transition-colors flex items-center justify-center gap-1.5"
          >
            <CheckCircle2 className="w-4 h-4" />
            Scan Finished — View Shortlist
          </button>
        )}
      </div>
    </div>
  );
};
