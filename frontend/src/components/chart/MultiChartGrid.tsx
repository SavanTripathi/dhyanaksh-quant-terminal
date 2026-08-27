import React from 'react';
import { TradingViewChart } from './TradingViewChart';
import { TimeframeToolbar } from './TimeframeToolbar';
import { GridLayout } from './GridSelector';
import { Candle, Zone, SpatialOverlapCluster, TradePlan, Timeframe } from '../../services/types';

interface MultiChartGridProps {
  layout: GridLayout;
  symbol: string;
  candlesMap: Record<Timeframe, Candle[]>;
  zones: Zone[];
  clusters: SpatialOverlapCluster[];
  activeTradePlan: TradePlan | null;
  activeSingleTf: Timeframe;
  onSingleTfChange: (tf: Timeframe) => void;
  theme: 'dark' | 'light';
  showEma20: boolean;
  showEma50: boolean;
  showSma200: boolean;
  showZones: boolean;
  showTradeLevels: boolean;
  showBrokenOpposing?: boolean;
  showVolume: boolean;
}

export const MultiChartGrid: React.FC<MultiChartGridProps> = ({
  layout,
  symbol,
  candlesMap,
  zones,
  clusters,
  activeTradePlan,
  activeSingleTf,
  onSingleTfChange,
  theme,
  showEma20,
  showEma50,
  showSma200,
  showZones,
  showTradeLevels,
  showBrokenOpposing = false,
  showVolume,
}) => {
  const isDark = theme === 'dark';

  // 1x1 Single View
  if (layout === '1x1') {
    return (
      <div className="w-full h-full flex flex-col overflow-hidden relative">
        <TradingViewChart
          candles={candlesMap[activeSingleTf] || []}
          zones={zones}
          clusters={clusters}
          activeTradePlan={activeTradePlan}
          timeframe={activeSingleTf}
          theme={theme}
          showEma20={showEma20}
          showEma50={showEma50}
          showSma200={showSma200}
          showZones={showZones}
          showTradeLevels={showTradeLevels}
          showBrokenOpposing={showBrokenOpposing}
          showVolume={showVolume}
          isMultiGrid={false}
          cmp={activeTradePlan?.current_price || activeTradePlan?.cmp}
        />
      </div>
    );
  }

  // 1x2 Dual View (Left: Weekly 1W, Right: Daily 1D)
  if (layout === '1x2') {
    return (
      <div className="w-full h-full grid grid-cols-2 gap-1 bg-[#2a2e39]/30 overflow-hidden">
        {/* Left Pane: Weekly (1W) */}
        <div className="relative flex flex-col w-full h-full overflow-hidden border-r border-[#2a2e39]/60">
          <div className="absolute top-2 left-3 z-20 px-2 py-0.5 bg-[#1e222d]/90 text-white font-mono text-[10px] font-bold rounded border border-[#2a2e39]">
            {symbol} • 1W (Weekly HTF)
          </div>
          <TradingViewChart
            candles={candlesMap['1W'] || []}
            zones={zones}
            clusters={clusters}
            activeTradePlan={activeTradePlan}
            timeframe={'1W'}
            theme={theme}
            showEma20={showEma20}
            showEma50={showEma50}
            showSma200={showSma200}
            showZones={showZones}
            showTradeLevels={showTradeLevels}
            showBrokenOpposing={showBrokenOpposing}
            showVolume={showVolume}
            isMultiGrid={true}
          />
        </div>

        {/* Right Pane: Daily (1D) */}
        <div className="relative flex flex-col w-full h-full overflow-hidden">
          <div className="absolute top-2 left-3 z-20 px-2 py-0.5 bg-[#1e222d]/90 text-white font-mono text-[10px] font-bold rounded border border-[#2a2e39]">
            {symbol} • 1D (Daily Execution)
          </div>
          <TradingViewChart
            candles={candlesMap['1D'] || []}
            zones={zones}
            clusters={clusters}
            activeTradePlan={activeTradePlan}
            timeframe={'1D'}
            theme={theme}
            showEma20={showEma20}
            showEma50={showEma50}
            showSma200={showSma200}
            showZones={showZones}
            showTradeLevels={showTradeLevels}
            showBrokenOpposing={showBrokenOpposing}
            showVolume={showVolume}
            isMultiGrid={true}
          />
        </div>
      </div>
    );
  }

  // 2x2 Quad View (Top-Left: 3M, Top-Right: 1M, Bottom-Left: 1W, Bottom-Right: 1D)
  return (
    <div className="w-full h-full grid grid-cols-2 grid-rows-2 gap-1 bg-[#2a2e39]/30 overflow-hidden">
      {/* Pane 1: Quarterly (3M) */}
      <div className="relative flex flex-col w-full h-full overflow-hidden border-r border-b border-[#2a2e39]/60">
        <div className="absolute top-2 left-3 z-20 px-2 py-0.5 bg-[#1e222d]/90 text-amber-400 font-mono text-[10px] font-bold rounded border border-amber-500/30">
          {symbol} • 3M (Quarterly Macro)
        </div>
        <TradingViewChart
          candles={candlesMap['3M'] || []}
          zones={zones}
          clusters={clusters}
          activeTradePlan={activeTradePlan}
          timeframe={'3M'}
          theme={theme}
          showEma20={showEma20}
          showEma50={showEma50}
          showSma200={showSma200}
          showZones={showZones}
          showTradeLevels={showTradeLevels}
          showBrokenOpposing={showBrokenOpposing}
          showVolume={showVolume}
          isMultiGrid={true}
        />
      </div>

      {/* Pane 2: Monthly (1M) */}
      <div className="relative flex flex-col w-full h-full overflow-hidden border-b border-[#2a2e39]/60">
        <div className="absolute top-2 left-3 z-20 px-2 py-0.5 bg-[#1e222d]/90 text-blue-400 font-mono text-[10px] font-bold rounded border border-blue-500/30">
          {symbol} • 1M (Monthly HTF)
        </div>
        <TradingViewChart
          candles={candlesMap['1M'] || []}
          zones={zones}
          clusters={clusters}
          activeTradePlan={activeTradePlan}
          timeframe={'1M'}
          theme={theme}
          showEma20={showEma20}
          showEma50={showEma50}
          showSma200={showSma200}
          showZones={showZones}
          showTradeLevels={showTradeLevels}
          showBrokenOpposing={showBrokenOpposing}
          showVolume={showVolume}
          isMultiGrid={true}
        />
      </div>

      {/* Pane 3: Weekly (1W) */}
      <div className="relative flex flex-col w-full h-full overflow-hidden border-r border-[#2a2e39]/60">
        <div className="absolute top-2 left-3 z-20 px-2 py-0.5 bg-[#1e222d]/90 text-emerald-400 font-mono text-[10px] font-bold rounded border border-emerald-500/30">
          {symbol} • 1W (Weekly Trend)
        </div>
        <TradingViewChart
          candles={candlesMap['1W'] || []}
          zones={zones}
          clusters={clusters}
          activeTradePlan={activeTradePlan}
          timeframe={'1W'}
          theme={theme}
          showEma20={showEma20}
          showEma50={showEma50}
          showSma200={showSma200}
          showZones={showZones}
          showTradeLevels={showTradeLevels}
          showBrokenOpposing={showBrokenOpposing}
          showVolume={showVolume}
          isMultiGrid={true}
        />
      </div>

      {/* Pane 4: Daily (1D) */}
      <div className="relative flex flex-col w-full h-full overflow-hidden">
        <div className="absolute top-2 left-3 z-20 px-2 py-0.5 bg-[#1e222d]/90 text-purple-400 font-mono text-[10px] font-bold rounded border border-purple-500/30">
          {symbol} • 1D (Daily Execution)
        </div>
        <TradingViewChart
          candles={candlesMap['1D'] || []}
          zones={zones}
          clusters={clusters}
          activeTradePlan={activeTradePlan}
          timeframe={'1D'}
          theme={theme}
          showEma20={showEma20}
          showEma50={showEma50}
          showSma200={showSma200}
          showZones={showZones}
          showTradeLevels={showTradeLevels}
          showBrokenOpposing={showBrokenOpposing}
          showVolume={showVolume}
          isMultiGrid={true}
        />
      </div>
    </div>
  );
};
