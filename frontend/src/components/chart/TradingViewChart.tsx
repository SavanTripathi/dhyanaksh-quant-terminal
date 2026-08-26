import React, { useEffect, useRef } from 'react';
import {
  createChart,
  IChartApi,
  ISeriesApi,
  CandlestickData,
  HistogramData,
  LineData,
  ColorType,
  LineStyle,
  IPriceLine,
} from 'lightweight-charts';
import { Candle, Zone, SpatialOverlapCluster, TradePlan, Timeframe } from '../../services/types';

interface TradingViewChartProps {
  candles: Candle[];
  zones: Zone[];
  clusters: SpatialOverlapCluster[];
  activeTradePlan?: TradePlan | null;
  timeframe: Timeframe;
  theme: 'dark' | 'light';
  showEma20: boolean;
  showEma50: boolean;
  showSma200: boolean;
  showZones: boolean;
  showTradeLevels: boolean;
  showVolume: boolean;
  isMultiGrid?: boolean;
}

export const TradingViewChart: React.FC<TradingViewChartProps> = ({
  candles,
  zones,
  clusters,
  activeTradePlan,
  timeframe,
  theme,
  showEma20,
  showEma50,
  showSma200,
  showZones,
  showTradeLevels,
  showVolume,
  isMultiGrid = false,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const ema20SeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const ema50SeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const sma200SeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const activePriceLinesRef = useRef<IPriceLine[]>([]);
  const areaBandsRef = useRef<ISeriesApi<'Area'>[]>([]);
  const [containerWidth, setContainerWidth] = React.useState<number>(800);

  const isDark = theme === 'dark';

  // Initialize Chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const bgColor = isDark ? '#131722' : '#ffffff';
    const textColor = isDark ? '#d1d4dc' : '#1e293b';
    const gridColor = isDark ? '#1e222d' : '#f1f5f9';
    const borderColor = isDark ? '#2a2e39' : '#e2e8f0';

    const initialWidth = chartContainerRef.current.clientWidth || 400;
    const initialHeight = chartContainerRef.current.clientHeight || 300;
    setContainerWidth(initialWidth);

    const chart = createChart(chartContainerRef.current, {
      width: initialWidth,
      height: initialHeight,
      layout: {
        background: { type: ColorType.Solid, color: bgColor },
        textColor: textColor,
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      },
      grid: {
        vertLines: { color: gridColor },
        horzLines: { color: gridColor },
      },
      crosshair: {
        mode: 1,
        vertLine: { color: '#787b86', width: 1, style: LineStyle.Dashed },
        horzLine: { color: '#787b86', width: 1, style: LineStyle.Dashed },
      },
      rightPriceScale: {
        borderColor: borderColor,
        autoScale: true,
        alignLabels: true,
        scaleMargins: {
          top: isMultiGrid ? 0.15 : 0.12, // Keep candles below top badges
          bottom: showVolume ? 0.22 : 0.10, // Keep candles above bottom volume histogram
        },
      },
      timeScale: {
        borderColor: borderColor,
        timeVisible: true,
        secondsVisible: false,
        rightOffset: isMultiGrid ? 6 : 10, // Prevent latest candle from touching right axis
        barSpacing: isMultiGrid ? 6 : 10,
        minBarSpacing: 1.0,
        fixLeftEdge: false,
        fixRightEdge: false,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    });

    chartRef.current = chart;

    // Add Candlestick Series
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.05,
      },
    });
    candlestickSeriesRef.current = candleSeries;

    // Add Dedicated Translucent Bottom Volume Sub-Pane
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: 'volume_scale',
    });

    chart.priceScale('volume_scale').applyOptions({
      scaleMargins: {
        top: 0.80, // Volume takes bottom 20% of canvas
        bottom: 0.0,
      },
    });
    volumeSeriesRef.current = volumeSeries;

    // Add EMA 20
    const ema20 = chart.addLineSeries({
      color: '#ff9800',
      lineWidth: isMultiGrid ? 1 : 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });
    ema20SeriesRef.current = ema20;

    // Add EMA 50
    const ema50 = chart.addLineSeries({
      color: '#2962ff',
      lineWidth: isMultiGrid ? 1 : 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });
    ema50SeriesRef.current = ema50;

    // Add SMA 200
    const sma200 = chart.addLineSeries({
      color: '#ab47bc',
      lineWidth: isMultiGrid ? 1 : 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });
    sma200SeriesRef.current = sma200;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        const { clientWidth, clientHeight } = chartContainerRef.current;
        if (clientWidth > 0 && clientHeight > 0) {
          setContainerWidth(clientWidth);
          chartRef.current.applyOptions({
            width: clientWidth,
            height: clientHeight,
          });
          chartRef.current.timeScale().fitContent();
        }
      }
    };

    const resizeObserver = new ResizeObserver(() => {
      handleResize();
    });

    if (chartContainerRef.current) {
      resizeObserver.observe(chartContainerRef.current);
    }

    window.addEventListener('resize', handleResize);
    setTimeout(handleResize, 60);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [theme, isMultiGrid, showVolume]);

  // Update Data, Indicators, and Extended Canvas Zone Shading
  useEffect(() => {
    if (!candlestickSeriesRef.current || !volumeSeriesRef.current || candles.length === 0) return;

    const formattedCandles: CandlestickData[] = [];
    const formattedVolume: HistogramData[] = [];
    const closes: number[] = [];

    const sorted = [...candles].sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    sorted.forEach((c) => {
      const timeInSec = Math.floor(new Date(c.timestamp).getTime() / 1000) as any;
      formattedCandles.push({
        time: timeInSec,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      });

      formattedVolume.push({
        time: timeInSec,
        value: c.volume || 100000,
        color: c.close >= c.open ? 'rgba(34, 197, 94, 0.65)' : 'rgba(239, 68, 68, 0.65)',
      });

      closes.push(c.close);
    });

    candlestickSeriesRef.current.setData(formattedCandles);

    if (showVolume && volumeSeriesRef.current) {
      volumeSeriesRef.current.setData(formattedVolume);
    } else if (volumeSeriesRef.current) {
      volumeSeriesRef.current.setData([]);
    }

    // Helper functions for indicators
    const calcEMA = (data: number[], span: number): number[] => {
      const k = 2 / (span + 1);
      const emaArr: number[] = [];
      let ema = data[0];
      for (let i = 0; i < data.length; i++) {
        ema = data[i] * k + ema * (1 - k);
        emaArr.push(ema);
      }
      return emaArr;
    };

    const calcSMA = (data: number[], window: number): (number | null)[] => {
      const smaArr: (number | null)[] = [];
      for (let i = 0; i < data.length; i++) {
        if (i < window - 1) {
          smaArr.push(null);
        } else {
          const slice = data.slice(i - window + 1, i + 1);
          const sum = slice.reduce((a, b) => a + b, 0);
          smaArr.push(sum / window);
        }
      }
      return smaArr;
    };

    // Update EMA 20
    if (showEma20 && ema20SeriesRef.current && closes.length > 0) {
      const ema20Values = calcEMA(closes, 20);
      const ema20Data: LineData[] = formattedCandles.map((c, idx) => ({
        time: c.time,
        value: ema20Values[idx],
      }));
      ema20SeriesRef.current.setData(ema20Data);
    } else if (ema20SeriesRef.current) {
      ema20SeriesRef.current.setData([]);
    }

    // Update EMA 50
    if (showEma50 && ema50SeriesRef.current && closes.length > 0) {
      const ema50Values = calcEMA(closes, 50);
      const ema50Data: LineData[] = formattedCandles.map((c, idx) => ({
        time: c.time,
        value: ema50Values[idx],
      }));
      ema50SeriesRef.current.setData(ema50Data);
    } else if (ema50SeriesRef.current) {
      ema50SeriesRef.current.setData([]);
    }

    // Update SMA 200
    if (showSma200 && sma200SeriesRef.current && closes.length > 0) {
      const sma200Values = calcSMA(closes, Math.min(200, closes.length));
      const sma200Data: LineData[] = [];
      formattedCandles.forEach((c, idx) => {
        const val = sma200Values[idx];
        if (val !== null) {
          sma200Data.push({ time: c.time, value: val });
        }
      });
      sma200SeriesRef.current.setData(sma200Data);
    } else if (sma200SeriesRef.current) {
      sma200SeriesRef.current.setData([]);
    }

    // CLEAR all previous price lines before drawing new ones
    if (candlestickSeriesRef.current) {
      activePriceLinesRef.current.forEach((line) => {
        try {
          candlestickSeriesRef.current?.removePriceLine(line);
        } catch (e) {}
      });
      activePriceLinesRef.current = [];

      // Draw Live Current Market Price (CMP) Line
      let latestClose = 0;
      if (formattedCandles.length > 0) {
        const latestCandle = formattedCandles[formattedCandles.length - 1];
        latestClose = latestCandle.close;
        const lCMP = candlestickSeriesRef.current.createPriceLine({
          price: latestCandle.close,
          color: '#38bdf8',
          lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `CMP: ₹${latestCandle.close.toFixed(2)}`,
        });
        activePriceLinesRef.current.push(lCMP);
      }

      // Trade Plan Price Lines (Compact, clean axis labels)
      if (showTradeLevels && activeTradePlan) {
        const plan = activeTradePlan;
        const isDemand = plan.direction === 'DEMAND';

        // 1. Proximal Entry Line
        const lEntry = candlestickSeriesRef.current.createPriceLine({
          price: plan.entry_price,
          color: isDemand ? '#22c55e' : '#ef4444',
          lineWidth: 2,
          lineStyle: LineStyle.Solid,
          axisLabelVisible: true,
          title: `Entry: ₹${plan.entry_price.toFixed(2)}`,
        });
        activePriceLinesRef.current.push(lEntry);

        // 2. Stop Loss Line
        const lSL = candlestickSeriesRef.current.createPriceLine({
          price: plan.stop_loss,
          color: '#ef4444',
          lineWidth: 2,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `SL: ₹${plan.stop_loss.toFixed(2)}`,
        });
        activePriceLinesRef.current.push(lSL);

        // 3. Target 1 Line (2.0R) - Hide on axis in multi-grid view to prevent clutter
        const lT1 = candlestickSeriesRef.current.createPriceLine({
          price: plan.target_1,
          color: '#38bdf8',
          lineWidth: 1,
          lineStyle: LineStyle.Dotted,
          axisLabelVisible: !isMultiGrid,
          title: `T1: ₹${plan.target_1.toFixed(2)}`,
        });
        activePriceLinesRef.current.push(lT1);

        // 4. Target 3 Line (5.0R) - Hide on axis in multi-grid view
        const lT3 = candlestickSeriesRef.current.createPriceLine({
          price: plan.target_3,
          color: '#38bdf8',
          lineWidth: 1,
          lineStyle: LineStyle.Dotted,
          axisLabelVisible: !isMultiGrid,
          title: `T3: ₹${plan.target_3.toFixed(2)}`,
        });
        activePriceLinesRef.current.push(lT3);
      }

      // Clear any previous area band series
      areaBandsRef.current.forEach((s) => {
        try {
          chartRef.current?.removeSeries(s);
        } catch (e) {}
      });
      areaBandsRef.current = [];

      // Draw Institutional Shaded Demand & Supply Zones (Decluttered: Filter > 15% away & clean axis)
      if (showZones && clusters.length > 0 && formattedCandles.length > 0) {
        const refPrice = activeTradePlan?.current_price || latestClose || clusters[0].overlap_min_price;
        
        // Filter out zones whose proximal boundary is > 15% away from current CMP to eliminate clutter
        const relevantClusters = clusters.filter((cl) => {
          const prox = cl.direction === 'DEMAND' ? cl.overlap_max_price : cl.overlap_min_price;
          const distPct = Math.abs(prox - refPrice) / refPrice;
          return distPct <= 0.18; // Keep only nearby relevant zones (within ~18%)
        });

        // Fallback: If all are > 18% away, keep strictly the nearest 1 single cluster
        const displayClusters = relevantClusters.length > 0 ? relevantClusters.slice(0, 2) : [clusters[0]];
        const startTime = formattedCandles[Math.max(0, formattedCandles.length - 80)].time;

        displayClusters.forEach((cl) => {
          const isDemand = cl.direction === 'DEMAND';
          const topColor = isDemand ? '#22c55e' : '#ef4444';

          // Shaded Rectangular Box Overlay for the Zone
          try {
            const zoneAreaSeries = chartRef.current?.addAreaSeries({
              topColor: isDemand ? 'rgba(34, 197, 94, 0.28)' : 'rgba(239, 68, 68, 0.28)',
              bottomColor: isDemand ? 'rgba(34, 197, 94, 0.08)' : 'rgba(239, 68, 68, 0.08)',
              lineColor: isDemand ? '#22c55e' : '#ef4444',
              lineWidth: 2,
              priceLineVisible: false,
              crosshairMarkerVisible: false,
              autoscaleInfoProvider: () => null, // Do not distort main price scale
            });

            if (zoneAreaSeries) {
              const zoneData = formattedCandles
                .filter((c) => c.time >= startTime)
                .map((c) => ({
                  time: c.time,
                  value: cl.overlap_max_price,
                }));
              zoneAreaSeries.setData(zoneData);
              areaBandsRef.current.push(zoneAreaSeries);
            }
          } catch (e) {}

          // Proximal Line (In multi-grid mode, omit extra label if Entry is already active)
          const lProx = candlestickSeriesRef.current?.createPriceLine({
            price: isDemand ? cl.overlap_max_price : cl.overlap_min_price,
            color: topColor,
            lineWidth: 2,
            lineStyle: LineStyle.Solid,
            axisLabelVisible: !isMultiGrid && !activeTradePlan,
            title: isDemand ? `Demand: ₹${cl.overlap_max_price.toFixed(2)}` : `Supply: ₹${cl.overlap_min_price.toFixed(2)}`,
          });
          if (lProx) activePriceLinesRef.current.push(lProx);

          // Distal Line on Canvas (Keep line visible on chart, but omit bulky axis label)
          const lDist = candlestickSeriesRef.current?.createPriceLine({
            price: isDemand ? cl.overlap_min_price : cl.overlap_max_price,
            color: topColor,
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            axisLabelVisible: false, // Clean price scale without redundant second badge
            title: '',
          });
          if (lDist) activePriceLinesRef.current.push(lDist);
        });
      }
    }

    // Set view window & ensure fit
    if (formattedCandles.length > 0) {
      const totalCandles = formattedCandles.length;
      const visibleCount = Math.min(
        totalCandles,
        timeframe === '3M' ? 30 : timeframe === '1M' ? 50 : timeframe === '1W' ? 100 : 150
      );
      chartRef.current?.timeScale().setVisibleLogicalRange({
        from: Math.max(0, totalCandles - visibleCount),
        to: totalCandles + 5,
      });
      // Auto-fit content if first load
      chartRef.current?.timeScale().fitContent();
    }
  }, [
    candles,
    zones,
    clusters,
    activeTradePlan,
    timeframe,
    theme,
    showEma20,
    showEma50,
    showSma200,
    showZones,
    showTradeLevels,
    showVolume,
  ]);

  // State for zone hover tooltip
  const [hoveredZone, setHoveredZone] = React.useState<{
    x: number;
    y: number;
    plan: TradePlan;
  } | null>(null);

  // Calculate SVG overlay coordinates for shaded boxes, directional arrows & hover tooltips
  const renderZoneOverlays = () => {
    if (!showZones || !candlestickSeriesRef.current || !chartContainerRef.current) return null;

    const overlayPlans = activeTradePlan ? [activeTradePlan] : [];
    if (overlayPlans.length === 0 && clusters.length > 0) {
      const topCl = clusters[0];
      const isDem = topCl.direction === 'DEMAND';
      overlayPlans.push({
        symbol: topCl.symbol,
        direction: topCl.direction,
        current_price: isDem ? topCl.overlap_max_price : topCl.overlap_min_price,
        overlap_min_price: topCl.overlap_min_price,
        overlap_max_price: topCl.overlap_max_price,
        entry_price: isDem ? topCl.overlap_max_price : topCl.overlap_min_price,
        stop_loss: isDem ? topCl.overlap_min_price * 0.98 : topCl.overlap_max_price * 1.02,
        risk_per_share: Math.abs(topCl.overlap_max_price - topCl.overlap_min_price),
        target_1: isDem ? topCl.overlap_max_price * 1.05 : topCl.overlap_min_price * 0.95,
        target_2: isDem ? topCl.overlap_max_price * 1.08 : topCl.overlap_min_price * 0.92,
        target_3: isDem ? topCl.overlap_max_price * 1.12 : topCl.overlap_min_price * 0.88,
        atr_1d_14: 10,
        atr_buffer: 2,
        distance_pct: 0.5,
        is_approaching: true,
        lifecycle_state: 'APPROACHING',
        achievements: topCl.achievements,
        participating_timeframes: topCl.participating_timeframes,
        status: 'ACTIVE',
        created_at: new Date().toISOString(),
      } as TradePlan);
    }

    return (
      <svg className="absolute inset-0 w-full h-full pointer-events-none z-10">
        <defs>
          <linearGradient id="demandGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#22c55e" stopOpacity="0.32" />
            <stop offset="100%" stopColor="#22c55e" stopOpacity="0.10" />
          </linearGradient>
          <linearGradient id="supplyGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ef4444" stopOpacity="0.32" />
            <stop offset="100%" stopColor="#ef4444" stopOpacity="0.10" />
          </linearGradient>
          <marker
            id="bullishArrow"
            viewBox="0 0 10 10"
            refX="6"
            refY="5"
            markerWidth="8"
            markerHeight="8"
            orient="auto-start-reverse"
          >
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981" />
          </marker>
          <marker
            id="bearishArrow"
            viewBox="0 0 10 10"
            refX="6"
            refY="5"
            markerWidth="8"
            markerHeight="8"
            orient="auto-start-reverse"
          >
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#ef4444" />
          </marker>
        </defs>

        {overlayPlans.map((plan, idx) => {
          const isDemand = plan.direction === 'DEMAND';
          const yTop = candlestickSeriesRef.current?.priceToCoordinate(plan.overlap_max_price) ?? null;
          const yBot = candlestickSeriesRef.current?.priceToCoordinate(plan.overlap_min_price) ?? null;

          if (yTop === null || yBot === null || isNaN(yTop) || isNaN(yBot)) return null;

          const boxTop = Math.min(yTop, yBot);
          const boxHeight = Math.max(16, Math.abs(yBot - yTop));
          const boxWidth = '82%';

          return (
            <g key={`svg-zone-${idx}`}>
              {/* Shaded Institutional Demand / Supply Rectangular Box with pointer events for hover */}
              <rect
                x="8%"
                y={boxTop}
                width={boxWidth}
                height={boxHeight}
                fill={isDemand ? 'url(#demandGradient)' : 'url(#supplyGradient)'}
                stroke={isDemand ? '#22c55e' : '#ef4444'}
                strokeWidth="2"
                strokeDasharray="4 2"
                rx="4"
                className="pointer-events-auto cursor-pointer transition-opacity hover:opacity-90"
                onMouseEnter={(e) => {
                  setHoveredZone({
                    x: e.clientX,
                    y: e.clientY,
                    plan: plan,
                  });
                }}
                onMouseLeave={() => setHoveredZone(null)}
              />

              {/* Clean in-box zone label */}
              <text
                x="10%"
                y={boxTop + boxHeight / 2 + 5}
                fill={isDemand ? '#22c55e' : '#ef4444'}
                fontSize="12"
                fontWeight="bold"
                fontFamily="monospace"
              >
                {isDemand ? '🟢 DEMAND ZONE' : '🔴 SUPPLY ZONE'} [₹
                {plan.overlap_min_price.toFixed(2)} – ₹{plan.overlap_max_price.toFixed(2)}]
              </text>

              {/* Impulsive Bullish/Bearish Take-Off Vector Arrow */}
              {isDemand ? (
                <g>
                  <line
                    x1="62%"
                    y1={boxTop}
                    x2="78%"
                    y2={Math.max(20, boxTop - 110)}
                    stroke="#10b981"
                    strokeWidth="4.5"
                    markerEnd="url(#bullishArrow)"
                  />
                  <text
                    x="80%"
                    y={Math.max(30, boxTop - 100)}
                    fill="#10b981"
                    fontSize="12"
                    fontWeight="bold"
                  >
                    🚀 Impulsive Bullish Take-Off (T1/T2/T3)
                  </text>
                </g>
              ) : (
                <g>
                  <line
                    x1="62%"
                    y1={boxTop + boxHeight}
                    x2="78%"
                    y2={boxTop + boxHeight + 110}
                    stroke="#ef4444"
                    strokeWidth="4.5"
                    markerEnd="url(#bearishArrow)"
                  />
                  <text
                    x="80%"
                    y={boxTop + boxHeight + 105}
                    fill="#ef4444"
                    fontSize="12"
                    fontWeight="bold"
                  >
                    🔻 Impulsive Bearish Reversal Drop
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>
    );
  };

  return (
    <div className="relative w-full h-full">
      <div ref={chartContainerRef} className="w-full h-full" />
      {renderZoneOverlays()}

      {/* Floating Decision HUD (Responsive: Top-Left in Multi-Chart, Top-Center in Single 1x1) */}
      {activeTradePlan && (
        <div
          className={`absolute z-20 backdrop-blur-md border rounded-lg shadow-lg pointer-events-none text-xs flex items-center transition-all ${
            isMultiGrid || containerWidth < 550
              ? 'top-2 right-2 px-2 py-1 gap-1.5 text-[10px] max-w-[180px]'
              : 'top-3 left-1/2 -translate-x-1/2 px-3 py-2 gap-3 text-xs'
          } ${
            isDark
              ? 'bg-[#1e222d]/90 border-[#2a2e39] text-[#d1d4dc]'
              : 'bg-white/95 border-slate-200 text-slate-800 shadow-md'
          }`}
        >
          <div className="flex items-center gap-1">
            <span
              className={`px-1.5 py-0.2 rounded font-bold ${
                isMultiGrid || containerWidth < 550 ? 'text-[8px]' : 'text-[10px]'
              } ${
                activeTradePlan.achievements >= 3
                  ? 'bg-amber-500/20 text-amber-500 border border-amber-500/30'
                  : 'bg-blue-500/20 text-blue-500 border border-blue-500/30'
              }`}
            >
              {activeTradePlan.achievements >= 3 ? '🥇 3-ACH' : '🥈 2-ACH'}
            </span>
            <span
              className={`px-1 py-0.2 rounded font-bold ${
                isMultiGrid || containerWidth < 550 ? 'text-[8px]' : 'text-[10px]'
              } ${
                activeTradePlan.direction === 'DEMAND'
                  ? 'bg-green-500/20 text-green-600 dark:text-green-400'
                  : 'bg-red-500/20 text-red-600 dark:text-red-400'
              }`}
            >
              {activeTradePlan.direction}
            </span>
          </div>

          {!(isMultiGrid || containerWidth < 550) && (
            <>
              <div className="font-mono text-[11px] font-semibold">
                Overlap: ₹{activeTradePlan.overlap_min_price.toFixed(1)} – ₹{activeTradePlan.overlap_max_price.toFixed(1)}
              </div>
              <div className="text-[10px] opacity-70">
                TFs: {activeTradePlan.participating_timeframes.join(', ')}
              </div>
              {activeTradePlan.has_ma_confluence && (
                <div className="text-emerald-500 text-[10px] font-semibold flex items-center gap-1">
                  ✓ MA Nested
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* SVG Zone Hover Tooltip */}
      {hoveredZone && (
        <div
          className={`fixed z-50 pointer-events-none p-2.5 rounded-lg shadow-xl text-xs backdrop-blur-md border ${
            isDark ? 'bg-[#181b24]/95 border-[#2a2e39] text-white' : 'bg-white/95 border-slate-200 text-slate-900'
          }`}
          style={{
            left: `${Math.min(window.innerWidth - 220, hoveredZone.x + 12)}px`,
            top: `${Math.max(10, hoveredZone.y - 40)}px`,
          }}
        >
          <div className="font-bold text-[11px] flex items-center gap-1.5 mb-1">
            <span className={hoveredZone.plan.direction === 'DEMAND' ? 'text-green-500' : 'text-red-500'}>
              ● {hoveredZone.plan.direction} ZONE
            </span>
            <span className="text-[10px] font-normal text-[#787b86]">
              ({hoveredZone.plan.achievements}-ACH)
            </span>
          </div>
          <div className="font-mono text-[11px]">
            Proximal: ₹{hoveredZone.plan.overlap_max_price.toFixed(2)}
          </div>
          <div className="font-mono text-[11px]">
            Distal: ₹{hoveredZone.plan.overlap_min_price.toFixed(2)}
          </div>
          <div className="text-[10px] text-[#787b86] mt-0.5">
            TFs: {hoveredZone.plan.participating_timeframes.join(', ')}
          </div>
        </div>
      )}
    </div>
  );
};
