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
import { AlertTicker } from './components/alerts/AlertTicker';
import { MobileBottomNav, MobileTab } from './components/mobile/MobileBottomNav';
import { MobileAlertsView } from './components/mobile/MobileAlertsView';
import { PWAInstallPrompt } from './components/mobile/PWAInstallPrompt';
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
import { DEFAULT_INITIAL_SETUPS } from './data/defaultSetups';
import { evaluateZoneMatch, evaluateATZMatch } from './utils/zoneEvaluator';


export function App() {
  // Theme state ('dark' or 'light')
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  // Multi-Chart Grid Layout State ('1x1', '1x2', '2x2')
  const [gridLayout, setGridLayout] = useState<GridLayout>('1x1');

  // Helper to safely get initial shortlist avoiding JS empty array [] trap
  const getInitialShortlist = (): TradePlan[] => {
    try {
      const cached = localStorage.getItem('dhyanaksh_cached_plans');
      if (cached) {
        const parsed = JSON.parse(cached);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {}
    return DEFAULT_INITIAL_SETUPS;
  };

  const initialSeed = getInitialShortlist();

  // Active Stock & Timeframe Selection (Dynamic initialization)
  const [selectedSymbol, setSelectedSymbol] = useState<string>(initialSeed[0].symbol);
  const [timeframe, setTimeframe] = useState<Timeframe>('1W');

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
  const [activeTradePlan, setActiveTradePlan] = useState<TradePlan | null>(initialSeed[0]);

  // Screener State
  const [allPlans, setAllPlans] = useState<TradePlan[]>(initialSeed);
  const [filteredPlans, setFilteredPlans] = useState<TradePlan[]>(initialSeed);
  const [isScreenerLoading, setIsScreenerLoading] = useState<boolean>(false);

  const [isScanning, setIsScanning] = useState<boolean>(false);

  // Filter Bar State (Defaults: ALL, ensuring all detected setups display immediately)
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [tierFilter, setTierFilter] = useState<'ALL' | '3_ACH' | '2_ACH'>('ALL');
  const [directionFilter, setDirectionFilter] = useState<'ALL' | ZoneDirection>('ALL');
  const [approachingOnly, setApproachingOnly] = useState<boolean>(false);
  const [maConfluenceOnly, setMaConfluenceOnly] = useState<boolean>(false);
  const [topPicksFilter, setTopPicksFilter] = useState<'ALL' | 'ATZ' | 'APP_WDZ' | 'APP_MDZ' | 'APP_QDZ' | 'APP_DDZ' | 'TOP_3' | 'TOP_5' | 'TOP_10' | 'SCORE_85' | 'GTF_11_5'>('ALL');

  // Indicators Overlays State (Clean Default: Exactly 2 Royal Blue Lines + CMP Axis Badge; Overlays Toggleable On-Demand)
  const [showEma20, setShowEma20] = useState<boolean>(false);
  const [showEma50, setShowEma50] = useState<boolean>(false);
  const [showSma200, setShowSma200] = useState<boolean>(false);
  const [showZones, setShowZones] = useState<boolean>(true);
  const [showBrokenOpposing, setShowBrokenOpposing] = useState<boolean>(false);
  const [showTradeLevels, setShowTradeLevels] = useState<boolean>(false);
  const [showVolume, setShowVolume] = useState<boolean>(true);

  // Bottom Analytics Drawer / Panel Toggle
  const [showProjectionPanel, setShowProjectionPanel] = useState<boolean>(true);

  // Alert Drawer State
  const [isAlertDrawerOpen, setIsAlertDrawerOpen] = useState<boolean>(false);
  const [alertsHistory, setAlertsHistory] = useState<AlertNotification[]>([]);
  const [isAlertLoading, setIsAlertLoading] = useState<boolean>(false);

  // Active View ('TERMINAL' or 'BACKTEST')
  const [activeView, setActiveView] = useState<'TERMINAL' | 'BACKTEST'>('TERMINAL');

  // Mobile Bottom Navigation Tab ('SCREENER' | 'CHARTS' | 'PLAN' | 'ALERTS') - Default: SCREENER
  const [activeMobileTab, setActiveMobileTab] = useState<MobileTab>('SCREENER');

  // Institutional Context States
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

  // Load Institutional Context Data (Regime, Sectors, F&O)
  const loadContextData = async (sym: string) => {
    if (!sym) return;
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
    if (!symbol) return;
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

  // Load Screener Shortlist (Zero hardcoding - dynamically populates plans & auto-selects top qualifying stock)
  const loadScreener = async () => {
    setIsScreenerLoading(true);
    try {
      const res = await api.fetchScreenerShortlist({ min_achievements: 2 });
      if (res && Array.isArray(res.plans)) {
        setAllPlans(res.plans);
        if (res.plans.length > 0) {
          const topStock = res.plans[0];
          setSelectedSymbol((curr) => {
            if (curr && res.plans.some((p) => p.symbol === curr)) {
              return curr;
            }
            setActiveTradePlan(topStock);
            loadChartData(topStock.symbol, timeframe);
            loadContextData(topStock.symbol);
            return topStock.symbol;
          });
          setActiveTradePlan((prev) => prev || topStock);
        }
      }
    } catch (err) {
      console.error('Failed to load dynamic screener shortlist:', err);
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

  // Clean Dynamic Startup Flow: Query GET /api/v1/screener/shortlist with Persistent Local Cache Backup
  useEffect(() => {
    let isMounted = true;

    // 1. Immediately hydrate with pre-bundled default setups or localStorage cache (ZERO BLANK STATE)
    let initialList = DEFAULT_INITIAL_SETUPS;
    try {
      const cached = localStorage.getItem('dhyanaksh_cached_plans');
      if (cached) {
        const parsed = JSON.parse(cached);
        if (Array.isArray(parsed) && parsed.length > 0) {
          initialList = parsed;
        }
      }
    } catch {}

    setAllPlans(initialList);
    const topStock = initialList[0];
    setSelectedSymbol((curr) => curr || topStock.symbol);
    setActiveTradePlan((curr) => curr || topStock);
    setIsScreenerLoading(false);
    loadChartData(topStock.symbol, timeframe || '1W');
    loadContextData(topStock.symbol);

    const initApp = async () => {
      try {
        const res = await api.fetchScreenerShortlist({ min_achievements: 2 });
        if (!isMounted) return;
        if (res && res.plans && res.plans.length > 0) {
          setAllPlans(res.plans);
          try {
            localStorage.setItem('dhyanaksh_cached_plans', JSON.stringify(res.plans));
          } catch {}
          setIsScreenerLoading(false);
          // Only update selectedStock if none was active
          setSelectedSymbol((curr) => curr || res.plans[0].symbol);
          setActiveTradePlan((curr) => curr || res.plans[0]);
        } else {
          setIsScreenerLoading(false);
        }
      } catch (err) {
        console.warn('Backend loading in progress, retaining current view state.');
        if (isMounted) setIsScreenerLoading(false);
      }
      loadAlerts();
    };

    initApp();

    return () => {
      isMounted = false;
    };
  }, []);


  // 5-Minute Live CMP Quote Poller for Active Selected Symbol
  useEffect(() => {
    if (!selectedSymbol) return;

    const refreshActiveQuote = async () => {
      try {
        const quote = await api.fetchQuote(selectedSymbol);
        if (quote && quote.ltp) {
          setActiveTradePlan((prev) => (prev ? { ...prev, current_price: quote.ltp } : prev));
        }
      } catch (err) {
        console.warn('Quote polling error:', err);
      }
    };

    const intervalId = setInterval(refreshActiveQuote, 5 * 60 * 1000);
    return () => clearInterval(intervalId);
  }, [selectedSymbol]);

  // Re-fetch candles & context when timeframe, symbol, or grid layout changes
  useEffect(() => {
    if (selectedSymbol) {
      loadChartData(selectedSymbol, timeframe);
      loadContextData(selectedSymbol);
    }
  }, [selectedSymbol, timeframe, gridLayout]);

  // Apply Screener Filtering (Auto-bypass restrictive filters on active search query >= 2 chars)
  useEffect(() => {
    let result = [...allPlans];
    const q = searchQuery.toLowerCase().trim();

    if (q.length >= 2) {
      // Direct global symbol/name search across all plans without conflicting filters blocking results
      result = result.filter((p) => p.symbol.toLowerCase().includes(q));
    } else {
      if (q.length === 1) {
        result = result.filter((p) => p.symbol.toLowerCase().includes(q));
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

      // 👑 ATZ Filter: Strict 4-Timeframe Confluence Intersection (QDZ AND MDZ AND WDZ AND DDZ)
      if (topPicksFilter === 'ATZ') {
        result = result.filter((p) => evaluateATZMatch(p, directionFilter));
      } else if (topPicksFilter === 'APP_WDZ') {
        result = result.filter((p) => evaluateZoneMatch(p, '1W', directionFilter).isMatch);
      } else if (topPicksFilter === 'APP_MDZ') {
        result = result.filter((p) => evaluateZoneMatch(p, '1M', directionFilter).isMatch);
      } else if (topPicksFilter === 'APP_QDZ') {
        result = result.filter((p) => evaluateZoneMatch(p, '3M', directionFilter).isMatch);
      } else if (topPicksFilter === 'APP_DDZ') {
        result = result.filter((p) => evaluateZoneMatch(p, '1D', directionFilter).isMatch);
      } else if (topPicksFilter === 'TOP_3') {
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
    }

    setFilteredPlans(result.length > 0 ? result : (searchQuery.trim().length === 0 && tierFilter === 'ALL' && directionFilter === 'ALL' && !approachingOnly && !maConfluenceOnly && topPicksFilter === 'ALL' ? DEFAULT_INITIAL_SETUPS : result));
  }, [allPlans, searchQuery, tierFilter, directionFilter, approachingOnly, maConfluenceOnly, topPicksFilter]);


  // Active Symbol Click Synchronization
  const handleSelectPlan = (plan: TradePlan) => {
    setActiveTradePlan(plan);
    setSelectedSymbol(plan.symbol);
    loadChartData(plan.symbol, timeframe);
    loadContextData(plan.symbol);
  };

  // 1-Click Stock Selection & Navigation from Alerts
  const handleSelectStockAndGoToChart = async (symbol: string) => {
    setSelectedSymbol(symbol);
    const matched = allPlans.find((p) => p.symbol === symbol);
    if (matched) {
      setActiveTradePlan(matched);
    }
    await loadChartData(symbol, timeframe || '1D');
    await loadContextData(symbol);
    setActiveMobileTab('CHARTS');
    setIsAlertDrawerOpen(false);
  };

  // Select stock directly from NIFTY 500 search
  const handleSelectStockSymbol = async (symbol: string) => {
    setSelectedSymbol(symbol);
    const matched = allPlans.find((p) => p.symbol === symbol);
    if (matched) {
      setActiveTradePlan(matched);
      await loadChartData(symbol, timeframe || '1W');
      await loadContextData(symbol);
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
            zone_timeframe: topCluster.participating_timeframes.includes('1W' as any) ? '1W' : topCluster.participating_timeframes[0] || '1D',
            proximity_state: 'IN_ZONE',
            proximity_pct: 0.85,
          };

          setAllPlans((prev) => [dynamicPlan, ...prev.filter((p) => p.symbol !== symbol)]);
          setActiveTradePlan(dynamicPlan);
        } else {
          setActiveTradePlan(null);
        }
        await loadChartData(symbol, timeframe || '1W');
        await loadContextData(symbol);
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
            if (selectedSymbol) {
              await loadChartData(selectedSymbol, timeframe);
            }
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
      await api.triggerTestAlert(channel, selectedSymbol || 'CHOLAFIN');
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
        regimeData={regimeData}
      />

      {/* Market Regime & Institutional Liquidity Banner (Desktop Only - hidden on mobile PWA) */}
      <div className="hidden lg:block">
        <MarketRegimeBanner
          regimeData={regimeData}
          theme={theme}
          onOpenSectors={() => setIsSectorModalOpen(true)}
        />
      </div>

      {/* Continuous Audio/Visual Proximity Radar Alerts (Desktop Only - hidden on mobile PWA) */}
      <div className="hidden lg:block">
        <RadarAlertSystem
          plans={filteredPlans.length > 0 ? filteredPlans : allPlans}
          selectedSymbol={selectedSymbol}
          onSelectPlan={handleSelectPlan}
          theme={theme}
        />
      </div>

      {/* Live In-Zone Alert Ticker Bar */}
      <AlertTicker
        shortlist={allPlans}
        onSelectStock={handleSelectPlan}
        theme={theme}
      />


      {/* Main Terminal Workspace */}
      {activeView === 'BACKTEST' ? (
        <div className="flex-1 flex overflow-hidden">
          <BacktestDashboard
            initialSymbol={selectedSymbol || 'CHOLAFIN'}
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
                masterPlans={allPlans}
                totalPlansCount={allPlans.length}
                filteredPlansCount={filteredPlans.length}
                theme={theme}
              />

              <ScreenerTable
                plans={filteredPlans}
                selectedSymbol={selectedSymbol}
                onSelectPlan={handleSelectPlan}
                isLoading={isScreenerLoading}
                activeRadarTab={topPicksFilter}
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
              {/* Top Chart Toolbar: Timeframes & Grid Selector */}
              <div
                className={`flex items-center justify-between border-b px-2 sm:px-3 py-0.5 sm:py-1 transition-colors gap-2 overflow-x-auto no-scrollbar shrink-0 ${
                  isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
                }`}
              >
                <div className="flex-1 min-w-0">
                  <TimeframeToolbar
                    symbol={selectedSymbol || (allPlans[0]?.symbol ?? '')}
                    cmp={activeTradePlan?.current_price || (candlesMap[timeframe]?.length ? candlesMap[timeframe][candlesMap[timeframe].length - 1].close : undefined)}
                    changePct={activeTradePlan ? ((activeTradePlan.current_price - activeTradePlan.entry_price) / activeTradePlan.entry_price) * 100 : 0}
                    activeTimeframe={timeframe}
                    onTimeframeChange={(tf) => setTimeframe(tf)}
                    theme={theme}
                  />
                </div>

                <div className="flex items-center gap-1.5 shrink-0 pl-2 border-l border-slate-700/50">
                  <span className="hidden xl:inline text-[10px] text-[#787b86] font-semibold uppercase tracking-wider">
                    Grid:
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
                showBrokenOpposing={showBrokenOpposing}
                setShowBrokenOpposing={setShowBrokenOpposing}
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
                  symbol={selectedSymbol || (allPlans[0]?.symbol ?? '')}
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
                  showBrokenOpposing={showBrokenOpposing}
                  showVolume={showVolume}
                />
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 2. MOBILE RESPONSIVE WORKSPACE */}
          {/* ========================================================================= */}
          <div className="lg:hidden flex-1 flex flex-col overflow-hidden relative">
            {activeMobileTab === 'CHARTS' && (
              <div className="flex-1 flex flex-col overflow-hidden">
                <div
                  className={`flex items-center justify-between border-b px-1.5 sm:px-2 py-1 transition-colors gap-1.5 overflow-x-auto no-scrollbar shrink-0 ${
                    isDark ? 'bg-[#1e222d] border-[#2a2e39]' : 'bg-slate-50 border-slate-200'
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <TimeframeToolbar
                      symbol={selectedSymbol || (allPlans[0]?.symbol ?? '')}
                      cmp={activeTradePlan?.current_price || (candlesMap[timeframe]?.length ? candlesMap[timeframe][candlesMap[timeframe].length - 1].close : undefined)}
                      changePct={activeTradePlan ? ((activeTradePlan.current_price - activeTradePlan.entry_price) / activeTradePlan.entry_price) * 100 : 0}
                      activeTimeframe={timeframe}
                      onTimeframeChange={(tf) => setTimeframe(tf)}
                      theme={theme}
                    />
                  </div>
                  <div className="shrink-0 pl-1">
                    <GridSelector layout={gridLayout} onLayoutChange={setGridLayout} theme={theme} />
                  </div>
                </div>

                {/* Mobile Overlays Bar (EMA 20/50/200, Broken Opposing, Trade Plan) */}
                <IndicatorControls
                  showEma20={showEma20}
                  setShowEma20={setShowEma20}
                  showEma50={showEma50}
                  setShowEma50={setShowEma50}
                  showSma200={showSma200}
                  setShowSma200={setShowSma200}
                  showZones={showZones}
                  setShowZones={setShowZones}
                  showBrokenOpposing={showBrokenOpposing}
                  setShowBrokenOpposing={setShowBrokenOpposing}
                  showTradeLevels={showTradeLevels}
                  setShowTradeLevels={setShowTradeLevels}
                  showVolume={showVolume}
                  setShowVolume={setShowVolume}
                  theme={theme}
                />
                <div className="flex-1 min-h-0 relative">
                  <MultiChartGrid
                    layout={gridLayout}
                    symbol={selectedSymbol || (allPlans[0]?.symbol ?? '')}
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
                    showBrokenOpposing={showBrokenOpposing}
                    showVolume={showVolume}
                  />
                </div>
              </div>
            )}

            {activeMobileTab === 'SCREENER' && (
              <div className="flex-1 flex flex-col overflow-hidden">
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
                  masterPlans={allPlans}
                  totalPlansCount={allPlans.length}
                  filteredPlansCount={filteredPlans.length}
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
                  activeRadarTab={topPicksFilter}
                  theme={theme}
                />
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
              <MobileAlertsView
                alerts={alertsHistory}
                activePlans={allPlans}
                onSelectStockAndGoToChart={handleSelectStockAndGoToChart}
                onTriggerTestAlert={handleTriggerTestAlert}
                isLoading={isAlertLoading}
                theme={theme}
              />
            )}

            {/* Mobile Bottom Navigation */}
            <MobileBottomNav
              activeTab={activeMobileTab}
              onTabChange={setActiveMobileTab}
              shortlistCount={filteredPlans.length}
              alertCount={alertsHistory.length}
              theme={theme}
            />
          </div>
        </>
      )}

      {/* Sector Rotation Heatmap Modal */}
      {isSectorModalOpen && (
        <SectorRotationMatrix
          sectorsData={sectorsData}
          onClose={() => setIsSectorModalOpen(false)}
          theme={theme}
        />
      )}

      {/* Full NIFTY 500 Batch Scan Live Progress Modal */}
      <ScanProgressModal
        isOpen={isScanModalOpen}
        progress={scanProgress}
        onClose={() => setIsScanModalOpen(false)}
        theme={theme}
      />

      {/* Right Drawer: Alerts Management & Dispatcher */}
      <AlertDrawer
        isOpen={isAlertDrawerOpen}
        onClose={() => setIsAlertDrawerOpen(false)}
        alerts={alertsHistory}
        activePlans={allPlans}
        onTriggerTestAlert={handleTriggerTestAlert}
        isLoading={isAlertLoading}
        selectedSymbol={selectedSymbol || 'CHOLAFIN'}
        onSelectStock={handleSelectStockAndGoToChart}
        theme={theme}
      />

      {/* Mobile PWA Install Prompt Banner */}
      <PWAInstallPrompt theme={theme} />
    </div>
  );
}
export default App;
