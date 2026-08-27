import React from 'react';

interface IndicatorControlsProps {
  showEma20: boolean;
  setShowEma20: (v: boolean) => void;
  showEma50: boolean;
  setShowEma50: (v: boolean) => void;
  showSma200: boolean;
  setShowSma200: (v: boolean) => void;
  showZones: boolean;
  setShowZones: (v: boolean) => void;
  showTradeLevels: boolean;
  setShowTradeLevels: (v: boolean) => void;
  showBrokenOpposing: boolean;
  setShowBrokenOpposing: (v: boolean) => void;
  showVolume: boolean;
  setShowVolume: (v: boolean) => void;
  theme?: 'dark' | 'light';
}

export const IndicatorControls: React.FC<IndicatorControlsProps> = ({
  showEma20,
  setShowEma20,
  showEma50,
  setShowEma50,
  showSma200,
  setShowSma200,
  showZones,
  setShowZones,
  showTradeLevels,
  setShowTradeLevels,
  showBrokenOpposing,
  setShowBrokenOpposing,
  showVolume,
  setShowVolume,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  return (
    <div
      className={`flex items-center gap-1.5 px-3 py-1.5 border-b text-xs transition-colors overflow-x-auto no-scrollbar shrink-0 ${
        isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
      }`}
    >
      <span className="text-[#787b86] font-bold text-[9px] uppercase tracking-wider shrink-0 mr-1">
        OVERLAYS:
      </span>

      {/* EMA 20 */}
      <button
        onClick={() => setShowEma20(!showEma20)}
        className={`px-2 py-0.5 rounded border transition-colors flex items-center gap-1.5 ${
          showEma20
            ? 'bg-[#ff9800]/10 border-[#ff9800] text-[#ff9800]'
            : isDark
            ? 'border-[#2a2e39] text-[#787b86] hover:text-[#d1d4dc]'
            : 'border-slate-300 text-slate-500 hover:text-slate-800'
        }`}
      >
        <span className="w-2 h-2 rounded-full bg-[#ff9800]" />
        EMA 20
      </button>

      {/* EMA 50 */}
      <button
        onClick={() => setShowEma50(!showEma50)}
        className={`px-2 py-0.5 rounded border transition-colors flex items-center gap-1.5 ${
          showEma50
            ? 'bg-[#2962ff]/10 border-[#2962ff] text-[#2962ff]'
            : isDark
            ? 'border-[#2a2e39] text-[#787b86] hover:text-[#d1d4dc]'
            : 'border-slate-300 text-slate-500 hover:text-slate-800'
        }`}
      >
        <span className="w-2 h-2 rounded-full bg-[#2962ff]" />
        EMA 50
      </button>

      {/* SMA 200 */}
      <button
        onClick={() => setShowSma200(!showSma200)}
        className={`px-2 py-0.5 rounded border transition-colors flex items-center gap-1.5 ${
          showSma200
            ? 'bg-[#ab47bc]/10 border-[#ab47bc] text-[#ab47bc]'
            : isDark
            ? 'border-[#2a2e39] text-[#787b86] hover:text-[#d1d4dc]'
            : 'border-slate-300 text-slate-500 hover:text-slate-800'
        }`}
      >
        <span className="w-2 h-2 rounded-full bg-[#ab47bc]" />
        SMA 200
      </button>

      <div className={`w-px h-3.5 mx-1 ${isDark ? 'bg-[#2a2e39]' : 'bg-slate-300'}`} />

      {/* HTF Zones (2 Royal Blue Lines Default) */}
      <button
        onClick={() => setShowZones(!showZones)}
        className={`px-2 py-0.5 rounded border transition-colors flex items-center gap-1.5 ${
          showZones
            ? 'bg-[#2563eb]/10 border-[#2563eb] text-[#3b82f6]'
            : isDark
            ? 'border-[#2a2e39] text-[#787b86] hover:text-[#d1d4dc]'
            : 'border-slate-300 text-slate-500 hover:text-slate-800'
        }`}
      >
        <span className="w-2 h-2 rounded-sm bg-[#2563eb]" />
        HTF Zones (2 Blue Lines)
      </button>

      {/* Broken Opposing (Sky Blue Achievement Line) */}
      <button
        onClick={() => setShowBrokenOpposing(!showBrokenOpposing)}
        className={`px-2 py-0.5 rounded border transition-colors flex items-center gap-1.5 ${
          showBrokenOpposing
            ? 'bg-[#38bdf8]/10 border-[#38bdf8] text-[#38bdf8]'
            : isDark
            ? 'border-[#2a2e39] text-[#787b86] hover:text-[#d1d4dc]'
            : 'border-slate-300 text-slate-500 hover:text-slate-800'
        }`}
      >
        <span className="w-2 h-2 rounded-sm bg-[#38bdf8]" />
        Broken Opposing
      </button>

      {/* Trade Levels (Entry / SL / Targets) */}
      <button
        onClick={() => setShowTradeLevels(!showTradeLevels)}
        className={`px-2 py-0.5 rounded border transition-colors flex items-center gap-1.5 ${
          showTradeLevels
            ? 'bg-[#10b981]/10 border-[#10b981] text-[#10b981]'
            : isDark
            ? 'border-[#2a2e39] text-[#787b86] hover:text-[#d1d4dc]'
            : 'border-slate-300 text-slate-500 hover:text-slate-800'
        }`}
      >
        <span className="w-2 h-2 rounded-sm bg-[#10b981]" />
        Trade Plan (SL / T1–T3)
      </button>

      {/* Volume */}
      <button
        onClick={() => setShowVolume(!showVolume)}
        className={`px-2 py-0.5 rounded border transition-colors flex items-center gap-1.5 ${
          showVolume
            ? 'bg-[#00bcd4]/10 border-[#00bcd4] text-[#00bcd4]'
            : isDark
            ? 'border-[#2a2e39] text-[#787b86] hover:text-[#d1d4dc]'
            : 'border-slate-300 text-slate-500 hover:text-slate-800'
        }`}
      >
        Volume
      </button>
    </div>
  );
};
