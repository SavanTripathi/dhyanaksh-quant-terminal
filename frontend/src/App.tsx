import React, { useState, useEffect } from 'react';
import { Header } from './components/layout/Header';
import { MultiChartGrid } from './components/chart/MultiChartGrid';
import { TimeframeToolbar } from './components/chart/TimeframeToolbar';
import { IndicatorControls } from './components/chart/IndicatorControls';
import { GridSelector, GridLayout } from './components/chart/GridSelector';
import { ScreenerTable } from './components/screener/ScreenerTable';
import { FilterBar } from './components/screener/FilterBar';
import { AlertDrawer } from './components/alerts/AlertDrawer';
import { TradeProjectionCard } from './components/projection/TradeProjectionCard';
import { RiskRewardSummary } from './components/projection/RiskRewardSummary';
import { BacktestDashboard } from './components/backtest/BacktestDashboard';
import { MarketRegimeBanner } from './components/context/MarketRegimeBanner';
import { SectorRotationMatrix } from './components/context/SectorRotationMatrix';
import { DerivativesPanel } from './components/context/DerivativesPanel';
import { ScanProgressModal } from './components/screener/ScanProgressModal';
import { RadarAlertSystem } from './components/alerts/RadarAlertSystem';
import { MobileBottomNav, MobileTab } from './components/mobile/MobileBottomNav';
import { api } from './services/api';
import {
  Candle,
  Zone,
  SpatialOverlapCluster,
  TradePlan,
  Timeframe,
  ZoneDirection,
  AlertNotification,
} from './services/types';

export function App() {
  // Theme state ('dark' or 'light')
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  // Multi-Chart Grid Layout State ('1x1', '1x2', '2x2')
  const [gridLayout, setGridLayout] = useState<GridLayout>('1x1');

  // Active Stock & Timeframe Selection
  const [selectedSymbol, setSelectedSymbol] = useState<string>('RELIANCE');
  const [timeframe, setTimeframe] = useState<Timeframe>('1D');

  // Multi-timeframe Candles Map for Grid syncing
  const [candlesMap, setCandlesMap] = useState<Record<Timeframe, Candle[]>>({
    '3M': [],
    '1M': [],
    '1W': [],
    '1D': [],
    '125M': [],
    '75M': [],
  });

  // Zones and Clusters State
  const [zones, setZones] = useState<Zone[]>([]);
  const [clusters, setClusters] = useState<SpatialOverlapCluster[]>([]);
  const [activeTradePlan, setActiveTradePlan] = useState<TradePlan | null>(null);

  // Screener State
  const [allPlans, setAllPlans] = useState<TradePlan[]>([]);
  const [filteredPlans, setFilteredPlans] = useState<TradePlan[]>([]);
  const [isScreenerLoading, setIsScreenerLoading] = useState<boolean>(false);
  const [isScanning, setIsScanning] = useState<boolean>(false);

  // Filter Bar State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [tierFilter, setTierFilter] = useState<'ALL' | '3_ACH' | '2_ACH'>('ALL');
  const [directionFilter, setDirectionFilter] = useState<'ALL' | ZoneDirection>('ALL');
  const [approachingOnly, setApproachingOnly] = useState<boolean>(false);
  const [maConfluenceOnly, setMaConfluenceOnly] = useState<boolean>(false);
  const [topPicksFilter, setTopPicksFilter] = useState<'ALL' | 'TOP_3' | 'TOP_5' | 'TOP_10' | 'SCORE_85' | 'GTF_11_5'>('ALL');

  // Indicators Overlays State
  const [showEma20, setShowEma20] = useState<boolean>(true);
  const [showEma50, setShowEma50] = useState<boolean>(true);
  const [showSma200, setShowSma200] = useState<boolean>(true);
  const [showZones, setShowZones] = useState<boolean>(true);
  const [showTradeLevels, setShowTradeLevels] = useState<boolean>(true);
  const [showVolume, setShowVolume] = useState<boolean>(true);

  // Bottom Analytics Drawer / Panel Toggle
  const [showProjectionPanel, setShowProjectionPanel] = useState<boolean>(true);

  // Alert Drawer State
  const [isAlertDrawerOpen, setIsAlertDrawerOpen] = useState<boolean>(false);
  const [alertsHistory, setAlertsHistory] = useState<AlertNotification[]>([]);
  const [isAlertLoading, setIsAlertLoading] = useState<boolean>(false);

  // Active View ('TERMINAL' or 'BACKTEST')
  const [activeView, setActiveView] = useState<'TERMINAL' | 'BACKTEST'>('TERMINAL');

  // Mobile Bottom Navigation Tab ('CHARTS' | 'SCREENER' | 'TOP_ALPHA' | 'ALERTS')
  const [activeMobileTab, setActiveMobileTab] = useState<MobileTab>('CHARTS');

  // Step 7: Institutional Context States
  const [regimeData, setRegimeData] = useState<any | null>(null);
  const [sectorsData, setSectorsData] = useState<any | null>(null);
  const [foData, setFoData] = useState<any | null>(null);
  const [isSectorModalOpen, setIsSectorModalOpen] = useState<boolean>(false);

  const isDark = theme === 'dark';

  // Toggle Theme
  const handleToggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Load Step 7 Context Data (Regime, Sectors, F&O)
  const loadContextData = async (sym: string) => {
    try {
      const reg = await api.fetchMarketRegime();
      setRegimeData(reg);
      const sec = await api.fetchSectorRotation();
      setSectorsData(sec);
      const fo = await api.fetchFOIntelligence(sym);
      setFoData(fo);
    } catch (err) {
      console.error('Failed to load institutional context data:', err);
    }
  };

  // Load Chart Candles & Zones for active symbol across relevant timeframes
  const loadChartData = async (symbol: string, activeTf: Timeframe) => {
    try {
      // Load active single timeframe
      const candleRes = await api.fetchCandles(symbol, activeTf, 2520);
      setCandlesMap((prev) => ({ ...prev, [activeTf]: candleRes.candles }));

      // If in Dual or Quad Grid, fetch additional synchronized timeframes in parallel
      if (gridLayout === '1x2' || gridLayout === '2x2') {
        const requiredTfs: Timeframe[] = gridLayout === '1x2' ? ['1W', '1D'] : ['3M', '1M', '1W', '1D'];
        for (const tf of requiredTfs) {
          if (tf !== activeTf) {
            api.fetchCandles(symbol, tf, 2520).then((res) => {
              setCandlesMap((prev) => ({ ...prev, [tf]: res.candles }));
            });
          }
        }
      }

      // Fetch zones and clusters
      const zoneRes = await api.fetchZones(symbol, 2520, 2);
      setZones(zoneRes.zones);
      setClusters(zoneRes.clusters);
    } catch (err) {
      console.error('Failed to load chart data:', err);
    }
  };

  // Load Screener Shortlist (Preserving active user selection across refreshes)
  const loadScreener = async () => {
    setIsScreenerLoading(true);
    try {
      const res = await api.fetchScreenerShortlist({ min_achievements: 2 });
      if (res && Array.isArray(res.plans)) {
        setAllPlans(res.plans);
        if (res.plans.length > 0) {
          // Retain active trade plan matching selected symbol or match first plan ONLY if none active
          setActiveTradePlan((prevPlan) => {
            if (prevPlan) {
              const matched = res.plans.find((p) => p.symbol === prevPlan.symbol);
              return matched || prevPlan;
            }
            return res.plans.find((p) => p.symbol === selectedSymbol) || res.plans[0];
          });

          setSelectedSymbol((currentSelected) => {
            if (currentSelected) return currentSelected; // KEEP USER SELECTION LOCKED
            return res.plans[0]?.symbol || 'CHOLAFIN';
          });
        }
      }
    } catch (err) {
      console.error('Failed to load screener:', err);
    } finally {
      setIsScreenerLoading(false);
    }
  };

  // Load Alerts History
  const loadAlerts = async () => {
    try {
      const res = await api.fetchAlertsHistory(30);
      setAlertsHistory(res.alerts);
    } catch (err) {
      console.error('Failed to load alerts history:', err);
    }
  };

  // Initial Load & Automatic Periodic Background Sync (5-minute interval)
  useEffect(() => {
    loadChartData(selectedSymbol, timeframe);
    loadScreener();
    loadAlerts();
    loadContextData(selectedSymbol);

    // Auto-refresh screener shortlist every 5 minutes (300,000 ms) in background
    const interval = setInterval(() => {
      loadScreener();
      loadAlerts();
    }, 300000);

    return () => clearInterval(interval);
  }, []);

  // 5-Minute Live CMP Quote Poller for Active Selected Symbol
  useEffect(() => {
    if (!selectedSymbol) return;

    const refreshActiveQuote = async () => {
      try {
        const quote = await api.fetchQuote(selectedSymbol);
        if (quote && quote.ltp) {
          // Keep active trade plan current price updated
          setActiveTradePlan((prev) => (prev ? { ...prev, current_price: quote.ltp } : prev));
        }
      } catch (err) {
        console.warn('Quote polling error:', err);
      }
    };

    // Poll every 5 minutes (300,000 ms)
    const intervalId = setInterval(refreshActiveQuote, 5 * 60 * 1000);
    return () => clearInterval(intervalId);
  }, [selectedSymbol]);

  // Re-fetch candles & context when timeframe, symbol, or grid layout changes
  useEffect(() => {
    loadChartData(selectedSymbol, timeframe);
    loadContextData(selectedSymbol);
  }, [selectedSymbol, timeframe, gridLayout]);

  // Apply Screener Filtering
  useEffect(() => {
    let result = [...allPlans];

    if (searchQuery.trim()) {
      result = result.filter((p) =>
        p.symbol.toLowerCase().includes(searchQuery.toLowerCase().trim())
      );
    }

    if (tierFilter === '3_ACH') {
      result = result.filter((p) => p.achievements >= 3);
    } else if (tierFilter === '2_ACH') {
      result = result.filter((p) => p.achievements === 2);
    }

    if (directionFilter !== 'ALL') {
      result = result.filter((p) => p.direction === directionFilter);
    }

    if (approachingOnly) {
      result = result.filter((p) => p.is_approaching);
    }

    if (maConfluenceOnly) {
      result = result.filter((p) => p.has_ma_confluence);
    }

    // Step 9 & 10: Top Picks & GTF Conviction Filter Logic
    // Sort plans by conviction_score descending first
    result.sort((a, b) => (b.conviction_score || 70) - (a.conviction_score || 70));

    if (topPicksFilter === 'TOP_3') {
      result = result.slice(0, 3);
    } else if (topPicksFilter === 'TOP_5') {
      result = result.slice(0, 5);
    } else if (topPicksFilter === 'TOP_10') {
      result = result.slice(0, 10);
    } else if (topPicksFilter === 'SCORE_85') {
      result = result.filter((p) => (p.conviction_score || 0) >= 85);
    } else if (topPicksFilter === 'GTF_11_5') {
      result = result.filter((p) => (p.gtf_odds_score || 0) >= 11.5);
    }

    setFilteredPlans(result);
  }, [allPlans, searchQuery, tierFilter, directionFilter, approachingOnly, maConfluenceOnly, topPicksFilter]);

  // Fix 1: Active Symbol Click Synchronization (Immediate load of chart, quote, and zones)
  const handleSelectPlan = (plan: TradePlan) => {
    setActiveTradePlan(plan);
    setSelectedSymbol(plan.symbol);
    loadChartData(plan.symbol, timeframe);
    loadContextData(plan.symbol);
  };

  // Select stock directly from NIFTY 500 search
  const handleSelectStockSymbol = async (symbol: string) => {
    setSelectedSymbol(symbol);
    const matched = allPlans.find((p) => p.symbol === symbol);
    if (matched) {
      setActiveTradePlan(matched);
    } else {
      try {
        const zoneRes = await api.fetchZones(symbol, 2520, 2);
        if (zoneRes.clusters.length > 0) {
          const topCluster = zoneRes.clusters[0];
          const isDemand = topCluster.direction === 'DEMAND';
          const entry = isDemand ? topCluster.overlap_max_price : topCluster.overlap_min_price;
          const sl = isDemand
            ? topCluster.overlap_min_price * 0.98
            : topCluster.overlap_max_price * 1.02;
          const r = Math.abs(entry - sl);

          const dynamicPlan: TradePlan = {
            symbol: symbol,
            direction: topCluster.direction,
            current_price: entry,
            overlap_min_price: topCluster.overlap_min_price,
            overlap_max_price: topCluster.overlap_max_price,
            entry_price: entry,
            stop_loss: sl,
            risk_per_share: r,
            target_1: isDemand ? entry + 2.0 * r : entry - 2.0 * r,
            target_2: isDemand ? entry + 3.5 * r : entry - 3.5 * r,
            target_3: isDemand ? entry + 5.0 * r : entry - 5.0 * r,
            atr_1d_14: r * 5.0,
            atr_buffer: r,
            distance_pct: 0.85,
            is_approaching: true,
            has_ma_confluence: false,
            achievements: topCluster.achievements,
            participating_timeframes: topCluster.participating_timeframes,
            status: 'ACTIVE',
          };

          setAllPlans((prev) => [dynamicPlan, ...prev.filter((p) => p.symbol !== symbol)]);
          setActiveTradePlan(dynamicPlan);
        } else {
          setActiveTradePlan(null);
        }
      } catch (err) {
        console.error('Dynamic scan on search failed:', err);
      }
    }
  };

  // Scan Progress State
  const [isScanModalOpen, setIsScanModalOpen] = useState<boolean>(false);
  const [scanProgress, setScanProgress] = useState({
    is_running: false,
    current_index: 0,
    total: 500,
    current_symbol: '',
    percentage: 0,
    found_count: 0,
    status_message: 'Ready',
  });

  // Trigger Full NIFTY 500 Batch Scan with Real-time Progress Polling
  const handleTriggerBatchScan = async () => {
    setIsScanning(true);
    setIsScanModalOpen(true);
    setScanProgress({
      is_running: true,
      current_index: 0,
      total: 500,
      current_symbol: 'INITIALIZING',
      percentage: 0,
      found_count: 0,
      status_message: 'Initializing NIFTY 500 Scan Engine...',
    });

    // Start background polling
    const pollInterval = setInterval(async () => {
      try {
        const prog = await api.fetchBatchProgress();
        if (prog) {
          setScanProgress(prog);
          if (!prog.is_running && prog.percentage >= 100) {
            clearInterval(pollInterval);
            setIsScanning(false);
            await loadScreener();
            await loadChartData(selectedSymbol, timeframe);
            // Auto close modal after 1.5s delay
            setTimeout(() => {
              setIsScanModalOpen(false);
            }, 1500);
          }
        }
      } catch (err) {
        console.error('Progress poll error:', err);
      }
    }, 400);

    try {
      await api.triggerBatchScan(180, 2);
    } catch (err) {
      console.error('Batch scan execution error:', err);
    }
  };

  // Trigger Test Alert
  const handleTriggerTestAlert = async (channel: string) => {
    setIsAlertLoading(true);
    try {
      await api.triggerTestAlert(channel, selectedSymbol);
      await loadAlerts();
    } catch (err) {
      console.error('Test alert failed:', err);
    } finally {
      setIsAlertLoading(false);
    }
  };

  return (
    <div
      className={`h-screen w-screen flex flex-col overflow-hidden transition-colors ${
        isDark ? 'bg-[#131722] text-[#d1d4dc]' : 'bg-slate-100 text-slate-800'
      }`}
    >
      {/* Top Header */}
      <Header
        selectedSymbol={selectedSymbol}
        onSymbolChange={handleSelectStockSymbol}
        onTriggerBatchScan={handleTriggerBatchScan}
        onToggleAlertDrawer={() => setIsAlertDrawerOpen(true)}
        isScanning={isScanning}
        activeAlertCount={alertsHistory.length}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        activeView={activeView}
        onToggleView={setActiveView}
      />

      {/* Step 7: Market Regime & Institutional Liquidity Banner */}
      <MarketRegimeBanner
        regimeData={regimeData}
        theme={theme}
        onOpenSectors={() => setIsSectorModalOpen(true)}
      />

      {/* Step 11: Continuous Audio/Visual Proximity Radar Alerts */}
      <RadarAlertSystem
        plans={filteredPlans.length > 0 ? filteredPlans : allPlans}
        selectedSymbol={selectedSymbol}
        onSelectPlan={handleSelectPlan}
        theme={theme}
      />

      {/* Main Terminal Workspace */}
      {activeView === 'BACKTEST' ? (
        <div className="flex-1 flex overflow-hidden">
          <BacktestDashboard
            initialSymbol={selectedSymbol}
            theme={theme}
            onClose={() => setActiveView('TERMINAL')}
          />
        </div>
      ) : (
        <>
          {/* ========================================================================= */}
          {/* 1. DESKTOP 3-COLUMN WORKSPACE (lg:grid lg:grid-cols-12) */}
          {/* ========================================================================= */}
          <div className="hidden lg:grid lg:grid-cols-12 flex-1 w-full overflow-hidden gap-2 p-2 transition-colors">
            {/* COLUMN 1 (3 of 12 cols -> 25%): NIFTY 500 Shortlist Matrix */}
            <div
              className={`lg:col-span-3 h-full overflow-hidden border rounded-lg flex flex-col transition-colors shadow-sm ${
                isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-white border-slate-200'
              }`}
            >
              <div
                className={`p-3 border-b flex items-center justify-between transition-colors ${
                  isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
                }`}
              >
                <div>
                  <h2
                    className={`font-bold text-xs uppercase tracking-wider ${
                      isDark ? 'text-white' : 'text-slate-900'
                    }`}
                  >
                    NIFTY 500 Shortlist
                  </h2>
                  <p className="text-[10px] text-[#787b86]">Achievements &gt; 1 Only (Tier 2 & 3)</p>
                </div>
                <span className="px-2 py-0.5 bg-[#2962ff]/20 text-[#2962ff] rounded font-mono text-xs font-bold border border-[#2962ff]/30">
                  {filteredPlans.length} Setups
                </span>
              </div>

              <FilterBar
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
                onSelectStockSymbol={handleSelectStockSymbol}
                tierFilter={tierFilter}
                setTierFilter={setTierFilter}
                directionFilter={directionFilter}
                setDirectionFilter={setDirectionFilter}
                approachingOnly={approachingOnly}
                setApproachingOnly={setApproachingOnly}
                maConfluenceOnly={maConfluenceOnly}
                setMaConfluenceOnly={setMaConfluenceOnly}
                topPicksFilter={topPicksFilter}
                setTopPicksFilter={setTopPicksFilter}
                theme={theme}
              />

              <ScreenerTable
                plans={filteredPlans}
                selectedSymbol={selectedSymbol}
                onSelectPlan={handleSelectPlan}
                isLoading={isScreenerLoading}
                theme={theme}
              />
            </div>

            {/* COLUMN 2 (3 of 12 cols -> 25%): Prediction & Trade Plan Intelligence */}
            <div
              className={`lg:col-span-3 h-full overflow-y-auto border rounded-lg p-3 flex flex-col gap-3 transition-colors shadow-sm ${
                isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
              }`}
            >
              <TradeProjectionCard
                plan={
                  activeTradePlan ||
                  (allPlans.length > 0 ? allPlans[0] : null)
                }
                theme={theme}
              />
              <RiskRewardSummary
                plan={
                  activeTradePlan ||
                  (allPlans.length > 0 ? allPlans[0] : null)
                }
                theme={theme}
              />
              <DerivativesPanel foData={foData} theme={theme} />
            </div>

            {/* COLUMN 3 (6 of 12 cols -> 50%): Full-Height Interactive Charting Canvas */}
            <div
              className={`lg:col-span-6 h-full flex flex-col border rounded-lg overflow-hidden transition-colors shadow-sm ${
                isDark ? 'bg-[#131722] border-[#2a2e39]' : 'bg-white border-slate-200'
              }`}
            >
              {/* Top Control Bar: Timeframe Toolbar + Grid Selector */}
              <div
                className={`flex items-center justify-between border-b px-3 transition-colors ${
                  isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
                }`}
              >
                <TimeframeToolbar
                  activeTimeframe={timeframe}
                  onTimeframeChange={(tf) => setTimeframe(tf)}
                  theme={theme}
                />

                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-[#787b86] font-semibold uppercase tracking-wider">
                    Split Grid:
                  </span>
                  <GridSelector layout={gridLayout} onLayoutChange={setGridLayout} theme={theme} />
                </div>
              </div>

              <IndicatorControls
                showEma20={showEma20}
                setShowEma20={setShowEma20}
                showEma50={showEma50}
                setShowEma50={setShowEma50}
                showSma200={showSma200}
                setShowSma200={setShowSma200}
                showZones={showZones}
                setShowZones={setShowZones}
                showTradeLevels={showTradeLevels}
                setShowTradeLevels={setShowTradeLevels}
                showVolume={showVolume}
                setShowVolume={setShowVolume}
                theme={theme}
              />

              {/* Main Full-Height Interactive Chart */}
              <div className="flex-1 min-h-0 w-full relative">
                <MultiChartGrid
                  layout={gridLayout}
                  symbol={selectedSymbol}
                  candlesMap={candlesMap}
                  zones={zones}
                  clusters={clusters}
                  activeTradePlan={activeTradePlan}
                  activeSingleTf={timeframe}
                  onSingleTfChange={setTimeframe}
                  theme={theme}
                  showEma20={showEma20}
                  showEma50={showEma50}
                  showSma200={showSma200}
                  showZones={showZones}
                  showTradeLevels={showTradeLevels}
                  showVolume={showVolume}
                />
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 2. DEDICATED PWA MOBILE VIEWPORT (<lg: Full-Screen Tab Experience) */}
          {/* ========================================================================= */}
          <div className="lg:hidden flex-1 flex flex-col overflow-hidden pb-14">
            {activeMobileTab === 'SCREENER' && (
              <div className="flex-1 flex flex-col overflow-hidden">
                <div
                  className={`p-3 border-b flex items-center justify-between ${
                    isDark ? 'bg-[#181b24] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
                  }`}
                >
                  <h2 className={`font-bold text-xs uppercase tracking-wider ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    NIFTY 500 Shortlist ({filteredPlans.length})
                  </h2>
                </div>
                <FilterBar
                  searchQuery={searchQuery}
                  setSearchQuery={setSearchQuery}
                  onSelectStockSymbol={handleSelectStockSymbol}
                  tierFilter={tierFilter}
                  setTierFilter={setTierFilter}
                  directionFilter={directionFilter}
                  setDirectionFilter={setDirectionFilter}
                  approachingOnly={approachingOnly}
                  setApproachingOnly={setApproachingOnly}
                  maConfluenceOnly={maConfluenceOnly}
                  setMaConfluenceOnly={setMaConfluenceOnly}
                  topPicksFilter={topPicksFilter}
                  setTopPicksFilter={setTopPicksFilter}
                  theme={theme}
                />
                <ScreenerTable
                  plans={filteredPlans}
                  selectedSymbol={selectedSymbol}
                  onSelectPlan={(p) => {
                    handleSelectPlan(p);
                    setActiveMobileTab('CHARTS');
                  }}
                  isLoading={isScreenerLoading}
                  theme={theme}
                />
              </div>
            )}

            {activeMobileTab === 'CHARTS' && (
              <div className="flex-1 flex flex-col overflow-hidden">
                <div
                  className={`flex items-center justify-between border-b px-2 py-1 ${
                    isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
                  }`}
                >
                  <TimeframeToolbar
                    activeTimeframe={timeframe}
                    onTimeframeChange={(tf) => setTimeframe(tf)}
                    theme={theme}
                  />
                  <GridSelector layout={gridLayout} onLayoutChange={setGridLayout} theme={theme} />
                </div>
                <div className="flex-1 min-h-0 w-full relative">
                  <MultiChartGrid
                    layout={gridLayout}
                    symbol={selectedSymbol}
                    candlesMap={candlesMap}
                    zones={zones}
                    clusters={clusters}
                    activeTradePlan={activeTradePlan}
                    activeSingleTf={timeframe}
                    onSingleTfChange={setTimeframe}
                    theme={theme}
                    showEma20={showEma20}
                    showEma50={showEma50}
                    showSma200={showSma200}
                    showZones={showZones}
                    showTradeLevels={showTradeLevels}
                    showVolume={showVolume}
                  />
                </div>
              </div>
            )}

            {activeMobileTab === 'PLAN' && (
              <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-3">
                <TradeProjectionCard
                  plan={
                    activeTradePlan ||
                    (allPlans.length > 0 ? allPlans[0] : null)
                  }
                  theme={theme}
                />
                <RiskRewardSummary
                  plan={
                    activeTradePlan ||
                    (allPlans.length > 0 ? allPlans[0] : null)
                  }
                  theme={theme}
                />
                <DerivativesPanel foData={foData} theme={theme} />
              </div>
            )}

            {activeMobileTab === 'ALERTS' && (
              <div className="flex-1 overflow-y-auto p-3">
                <div className="text-center py-6 text-xs text-[#787b86]">
                  Click the top Bell icon or use the Slide-Over Alert Center for full history.
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* Sector Rotation Matrix Modal */}
      {isSectorModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="max-w-4xl w-full">
            <SectorRotationMatrix
              sectorsData={sectorsData}
              theme={theme}
              onClose={() => setIsSectorModalOpen(false)}
            />
          </div>
        </div>
      )}

      {/* Slide-Over Alert Drawer */}
      <AlertDrawer
        isOpen={isAlertDrawerOpen}
        onClose={() => setIsAlertDrawerOpen(false)}
        alerts={alertsHistory}
        activePlans={filteredPlans.length > 0 ? filteredPlans : allPlans}
        selectedSymbol={selectedSymbol}
        onSelectPlan={(p) => {
          handleSelectPlan(p);
          setIsAlertDrawerOpen(false);
        }}
        onTriggerTestAlert={handleTriggerTestAlert}
        isLoading={isAlertLoading}
        theme={theme}
      />

      {/* Dedicated 4-Tab Mobile Bottom Navigation Bar (<lg) */}
      <MobileBottomNav
        activeTab={activeMobileTab}
        onTabChange={(tab) => {
          setActiveMobileTab(tab);
          if (tab === 'ALERTS') {
            setIsAlertDrawerOpen(true);
          }
        }}
        shortlistCount={filteredPlans.length}
        alertCount={alertsHistory.length}
        theme={theme}
      />
    </div>
  );
}

export default App;
