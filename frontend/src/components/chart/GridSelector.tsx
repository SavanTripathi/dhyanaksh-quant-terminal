import React from 'react';
import { Square, Columns, Grid2X2 } from 'lucide-react';

export type GridLayout = '1x1' | '1x2' | '2x2';

interface GridSelectorProps {
  layout: GridLayout;
  onLayoutChange: (layout: GridLayout) => void;
  theme?: 'dark' | 'light';
}

export const GridSelector: React.FC<GridSelectorProps> = ({
  layout,
  onLayoutChange,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  return (
    <div className="flex items-center gap-1 bg-[#131722] dark:bg-[#131722] p-0.5 rounded border border-[#2a2e39] dark:border-[#2a2e39]">
      {/* 1x1 Single */}
      <button
        onClick={() => onLayoutChange('1x1')}
        title="Single View (1x1)"
        className={`p-1 rounded transition-colors ${
          layout === '1x1'
            ? 'bg-[#2962ff] text-white shadow-sm'
            : isDark
            ? 'text-[#787b86] hover:text-[#d1d4dc] hover:bg-[#2a2e39]'
            : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
        }`}
      >
        <Square className="w-3.5 h-3.5" />
      </button>

      {/* 1x2 Dual */}
      <button
        onClick={() => onLayoutChange('1x2')}
        title="Dual Split View (1x2 - Weekly + Daily)"
        className={`p-1 rounded transition-colors ${
          layout === '1x2'
            ? 'bg-[#2962ff] text-white shadow-sm'
            : isDark
            ? 'text-[#787b86] hover:text-[#d1d4dc] hover:bg-[#2a2e39]'
            : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
        }`}
      >
        <Columns className="w-3.5 h-3.5" />
      </button>

      {/* 2x2 Quad */}
      <button
        onClick={() => onLayoutChange('2x2')}
        title="Quad Multi-Timeframe View (2x2 - 3M, 1M, 1W, 1D)"
        className={`p-1 rounded transition-colors ${
          layout === '2x2'
            ? 'bg-[#2962ff] text-white shadow-sm'
            : isDark
            ? 'text-[#787b86] hover:text-[#d1d4dc] hover:bg-[#2a2e39]'
            : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
        }`}
      >
        <Grid2X2 className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
