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
  cmp?: number;
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
  cmp,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const arrowCanvasRef = useRef<HTMLCanvasElement | null>(null);
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
          top: 0.18, // 18% clearance from the top edge (prevents candles/T3 hiding under top toolbar)
          bottom: 0.22, // 22% clearance at bottom (keeps candles cleanly separated from volume bars)
        },
      },
      timeScale: {
        borderColor: borderColor,
        timeVisible: true,
        secondsVisible: false,
        rightOffset: isMultiGrid ? 10 : 16, // Generous right-hand breathing room for price labels and badges
        barSpacing: isMultiGrid ? 6 : 8,
        minBarSpacing: 1.5,
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
        top: 0.82, // Volume only occupies the bottom 18% of canvas
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

    // Force synchronize final candle's close with verified CMP if available
    const effectiveCmp = (cmp && cmp > 0) ? cmp : (activeTradePlan?.current_price && activeTradePlan.current_price > 0 ? activeTradePlan.current_price : 0);
    if (effectiveCmp > 0 && formattedCandles.length > 0) {
      const lastIndex = formattedCandles.length - 1;
      const lastCandle = { ...formattedCandles[lastIndex] };
      lastCandle.close = effectiveCmp;
      if (effectiveCmp > lastCandle.high) lastCandle.high = effectiveCmp;
      if (effectiveCmp < lastCandle.low) lastCandle.low = effectiveCmp;
      formattedCandles[lastIndex] = lastCandle;
      closes[lastIndex] = effectiveCmp;
    }

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

      // Draw Live Current Market Price (CMP) Line (Synchronized with verified CMP)
      let latestClose = 0;
      if (formattedCandles.length > 0) {
        const latestCandle = formattedCandles[formattedCandles.length - 1];
        latestClose = effectiveCmp > 0 ? effectiveCmp : latestCandle.close;
        const lCMP = candlestickSeriesRef.current.createPriceLine({
          price: latestClose,
          color: '#06B6D4', // Bright Cyan
          lineWidth: 2,
          lineStyle: LineStyle.Solid,
          axisLabelVisible: true,
          title: 'CMP',
        });
        activePriceLinesRef.current.push(lCMP);
      }

      // Render Minimalist HTF Blue Zone Lines (Default: Proximal, Distal, Broken Opposing Level)
      if (showZones && activeTradePlan) {
        const plan = activeTradePlan;
        const isDemand = plan.direction === 'DEMAND';
        const royalBlue = '#2563EB'; // Solid Royal Blue

        // 1. Proximal Entry Line (Solid Royal Blue)
        const lEntry = candlestickSeriesRef.current.createPriceLine({
          price: plan.entry_price,
          color: royalBlue,
          lineWidth: 2,
          lineStyle: LineStyle.Solid,
          axisLabelVisible: true,
          title: '', // Keep title empty for clean right-axis tag
        });
        activePriceLinesRef.current.push(lEntry);

        // 2. Distal Base Line (Zone Floor / Ceiling) (Solid Royal Blue)
        const distalPrice = isDemand ? plan.overlap_min_price : plan.overlap_max_price;
        const lDistal = candlestickSeriesRef.current.createPriceLine({
          price: distalPrice,
          color: royalBlue,
          lineWidth: 2,
          lineStyle: LineStyle.Solid,
          axisLabelVisible: true,
          title: '',
        });
        activePriceLinesRef.current.push(lDistal);

        // 3. Broken Opposing Zone Line (Sky Blue Achievement)
        const brokenLevel = plan.broken_supply_level || (plan as any).broken_supply_level;
        if (brokenLevel && brokenLevel > 0) {
          const lBroken = candlestickSeriesRef.current.createPriceLine({
            price: brokenLevel,
            color: '#38BDF8', // Sky Blue
            lineWidth: 2,
            lineStyle: LineStyle.Solid,
            axisLabelVisible: true,
            title: '',
          });
          activePriceLinesRef.current.push(lBroken);
        }
      }

      // Conditional Trade Plan Lines (ONLY when Trade Plan toggle is active)
      if (showTradeLevels && activeTradePlan) {
        const plan = activeTradePlan;

        // Stop Loss Line
        if (plan.stop_loss) {
          const lSL = candlestickSeriesRef.current.createPriceLine({
            price: plan.stop_loss,
            color: '#ef4444',
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            axisLabelVisible: true,
            title: 'SL',
          });
          activePriceLinesRef.current.push(lSL);
        }

        // Target 1 Line (2.0R)
        if (plan.target_1) {
          const lT1 = candlestickSeriesRef.current.createPriceLine({
            price: plan.target_1,
            color: '#10B981',
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            axisLabelVisible: true,
            title: 'T1 (2R)',
          });
          activePriceLinesRef.current.push(lT1);
        }

        // Target 3 Line (5.0R)
        if (plan.target_3) {
          const lT3 = candlestickSeriesRef.current.createPriceLine({
            price: plan.target_3,
            color: '#10B981',
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            axisLabelVisible: true,
            title: 'T3 (5R)',
          });
          activePriceLinesRef.current.push(lT3);
        }
      }

      // Clear any previous area band series
      areaBandsRef.current.forEach((s) => {
        try {
          chartRef.current?.removeSeries(s);
        } catch (e) {}
      });
      areaBandsRef.current = [];

      // Draw Institutional Price Line Boundaries
      if (showZones && clusters.length > 0 && formattedCandles.length > 0) {
        const refPrice = activeTradePlan?.current_price || latestClose || clusters[0].overlap_min_price;
        
        // Filter out zones whose proximal boundary is > 18% away from current CMP to eliminate clutter
        const relevantClusters = clusters.filter((cl) => {
          const prox = cl.direction === 'DEMAND' ? cl.overlap_max_price : cl.overlap_min_price;
          const distPct = Math.abs(prox - refPrice) / refPrice;
          return distPct <= 0.18;
        });

        // Fallback: If all are > 18% away, keep strictly the nearest 1 single cluster
        const displayClusters = relevantClusters.length > 0 ? relevantClusters.slice(0, 2) : [clusters[0]];

        displayClusters.forEach((cl) => {
          const isDemand = cl.direction === 'DEMAND';
          const topColor = isDemand ? '#3B82F6' : '#EF4444';

          if (!activeTradePlan) {
            // Proximal Line
            const lProx = candlestickSeriesRef.current?.createPriceLine({
              price: isDemand ? cl.overlap_max_price : cl.overlap_min_price,
              color: topColor,
              lineWidth: 2,
              lineStyle: LineStyle.Solid,
              axisLabelVisible: !isMultiGrid,
              title: isDemand ? `PROXIMAL` : `PROXIMAL`,
            });
            if (lProx) activePriceLinesRef.current.push(lProx);

            // Distal Line
            const lDist = candlestickSeriesRef.current?.createPriceLine({
              price: isDemand ? cl.overlap_min_price : cl.overlap_max_price,
              color: topColor,
              lineWidth: 2,
              lineStyle: LineStyle.Solid,
              axisLabelVisible: !isMultiGrid,
              title: isDemand ? `DISTAL` : `DISTAL`,
            });
            if (lDist) activePriceLinesRef.current.push(lDist);

            // Broken Opposing Line
            if (cl.broken_supply_level) {
              const lBrk = candlestickSeriesRef.current?.createPriceLine({
                price: cl.broken_supply_level,
                color: '#60A5FA',
                lineWidth: 2,
                lineStyle: LineStyle.Solid,
                axisLabelVisible: !isMultiGrid,
                title: isDemand ? 'BROKEN SUPPLY' : 'BROKEN DEMAND',
              });
              if (lBrk) activePriceLinesRef.current.push(lBrk);
            }
          }
        });
      }
    }

    // Set TradingView-calibrated dynamic viewport range (focus on recent bars with crisp candlestick bodies)
    if (formattedCandles.length > 0 && chartRef.current) {
      const totalCandles = formattedCandles.length;
      
      const visibleBarsMap: Record<string, number> = {
        '6M': 30,
        '3M': 40,
        '1M': 50,
        '1W': 75,
        '1D': 120,   // ~5-6 months of crisp, readable daily candles
        '125M': 60,
        '75M': 60,
      };

      const barsToShow = Math.min(
        totalCandles,
        isMultiGrid
          ? Math.floor((visibleBarsMap[timeframe] || 100) * 0.7)
          : (visibleBarsMap[timeframe] || 120)
      );

      const fromIndex = Math.max(0, totalCandles - barsToShow);
      const toIndex = totalCandles + (isMultiGrid ? 3 : 6); // right-side breathing room

      chartRef.current.priceScale('right').applyOptions({
        scaleMargins: {
          top: isMultiGrid ? 0.14 : 0.18,
          bottom: showVolume ? 0.22 : 0.12,
        },
      });

      chartRef.current.timeScale().setVisibleLogicalRange({
        from: fromIndex,
        to: toIndex,
      });
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

  // Dynamic Arrow Draw Function (Lightweight Charts Coordinate API bound)
  const drawDynamicProjectionArrow = React.useCallback(() => {
    if (
      !chartRef.current ||
      !candlestickSeriesRef.current ||
      !arrowCanvasRef.current ||
      !chartContainerRef.current
    ) {
      return;
    }

    const chart = chartRef.current;
    const series = candlestickSeriesRef.current;
    const timeScale = chart.timeScale();
    const canvas = arrowCanvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Match canvas dimensions to container
    const width = chartContainerRef.current.clientWidth;
    const height = chartContainerRef.current.clientHeight;
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }
    ctx.clearRect(0, 0, width, height);

    if (!activeTradePlan || !candles || candles.length === 0) return;

    const isDemand = (activeTradePlan.direction === 'DEMAND');
    const startPrice = activeTradePlan.entry_price;
    const endPrice = activeTradePlan.target_3 || activeTradePlan.target_1 || (isDemand ? startPrice * 1.08 : startPrice * 0.92);

    if (!startPrice || !endPrice) return;

    // Convert Logical/Price Coordinates to Exact Canvas (X, Y) Pixels
    const sortedCandles = [...candles].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    const lastCandle = sortedCandles[sortedCandles.length - 1];
    const timeInSec = Math.floor(new Date(lastCandle.timestamp).getTime() / 1000) as any;

    const startX = timeScale.timeToCoordinate(timeInSec);
    const startY = series.priceToCoordinate(startPrice);
    const endY = series.priceToCoordinate(endPrice);

    if (startX === null || startY === null || endY === null || isNaN(startX) || isNaN(startY) || isNaN(endY)) {
      return; // Price or time coordinate is currently off-screen
    }

    // Project forward ~120px in time
    const endX = Math.min(width - 40, startX + 110);

    // Render Dynamic Arrow & Trajectory
    ctx.save();
    const accentColor = isDemand ? '#06B6D4' : '#F43F5E'; // Bright Cyan for Demand, Rose for Supply
    ctx.strokeStyle = accentColor;
    ctx.fillStyle = accentColor;
    ctx.lineWidth = 2.5;
    ctx.setLineDash([5, 4]);

    // Path line
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.stroke();

    // Arrow Head
    ctx.setLineDash([]);
    const headLength = 10;
    const angle = Math.atan2(endY - startY, endX - startX);
    ctx.beginPath();
    ctx.moveTo(endX, endY);
    ctx.lineTo(endX - headLength * Math.cos(angle - Math.PI / 6), endY - headLength * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(endX - headLength * Math.cos(angle + Math.PI / 6), endY - headLength * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();

    // Target Label Badge
    ctx.font = 'bold 11px Inter, sans-serif';
    const labelText = `${isDemand ? '🚀 Target (3.5R/5R)' : '🔻 Target (3.5R/5R)'} ₹${endPrice.toFixed(2)}`;
    ctx.fillText(labelText, endX + 8, endY + 4);

    ctx.restore();
  }, [activeTradePlan, candles]);

  // State tick to trigger overlay updates on zoom and pan
  const [, setOverlayTick] = React.useState<number>(0);

  // Subscribe to real-time zoom & pan events from TradingView Lightweight Charts
  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;

    let animId: number | null = null;
    const syncOverlayCoordinates = () => {
      if (animId) cancelAnimationFrame(animId);
      animId = requestAnimationFrame(() => {
        setOverlayTick((prev) => (prev + 1) % 100000);
        drawDynamicProjectionArrow();
      });
    };

    // 1. Subscribe to horizontal pan and zoom range changes
    chart.timeScale().subscribeVisibleLogicalRangeChange(syncOverlayCoordinates);
    chart.timeScale().subscribeVisibleTimeRangeChange(syncOverlayCoordinates);

    // 2. Subscribe to crosshair and drag interactions
    chart.subscribeCrosshairMove(syncOverlayCoordinates);
    window.addEventListener('resize', syncOverlayCoordinates);

    // Initial sync
    syncOverlayCoordinates();

    return () => {
      if (animId) cancelAnimationFrame(animId);
      chart.timeScale().unsubscribeVisibleLogicalRangeChange(syncOverlayCoordinates);
      chart.timeScale().unsubscribeVisibleTimeRangeChange(syncOverlayCoordinates);
      chart.unsubscribeCrosshairMove(syncOverlayCoordinates);
      window.removeEventListener('resize', syncOverlayCoordinates);
    };
  }, [chartRef.current, candles, zones, activeTradePlan, drawDynamicProjectionArrow]);

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
          {/* Institutional Sky Blue / Cyan Demand Zone Fill */}
          <linearGradient id="demandGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#0284c7" stopOpacity="0.12" />
          </linearGradient>
          {/* Institutional Crimson Red Supply Zone Fill */}
          <linearGradient id="supplyGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ef4444" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#991b1b" stopOpacity="0.12" />
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
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8" />
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
          const rawHeight = Math.abs(yBot - yTop);
          // 1. Enforce minimum visual height of 28px so zone forms a clear, prominent rectangular box
          const boxHeight = Math.max(28, rawHeight);
          const boxWidth = '84%';

          const priceRangeText = `₹${plan.overlap_min_price.toFixed(1)} – ₹${plan.overlap_max_price.toFixed(1)}`;
          const badgeBorder = isDemand ? '#38bdf8' : '#ef4444';

          return (
            <g key={`svg-zone-${idx}`}>
              {/* Discrete Rectangular Bounding Box: Sky Blue for Demand / Crimson Red for Supply */}
              <rect
                x="8%"
                y={boxTop}
                width={boxWidth}
                height={boxHeight}
                fill={isDemand ? 'url(#demandGradient)' : 'url(#supplyGradient)'}
                stroke={isDemand ? '#38bdf8' : '#ef4444'}
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

              {/* High-Contrast Solid Background Pill for the Label */}
              <rect
                x="8.5%"
                y={boxTop + 4}
                width={215}
                height={20}
                rx="4"
                fill="#0b0f19"
                stroke={badgeBorder}
                strokeWidth="1.2"
                className="select-none pointer-events-none"
              />

              {/* Clear, Bold, Readable Text inside Pill */}
              <text
                x="9.2%"
                y={boxTop + 18}
                fill="#ffffff"
                fontSize="11.5"
                fontWeight="700"
                fontFamily="Inter, system-ui, sans-serif"
                className="select-none pointer-events-none"
              >
                <tspan fill={isDemand ? '#38bdf8' : '#f87171'} fontWeight="800">
                  {isDemand ? '● DEMAND' : '● SUPPLY'}
                </tspan>
                <tspan fill="#94a3b8" fontSize="10.5"> ({plan.achievements}-ACH)</tspan>
                <tspan fill="#e2e8f0" fontWeight="600"> [{priceRangeText}]</tspan>
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Base Lightweight Charts Container */}
      <div ref={chartContainerRef} className="w-full h-full" />

      {/* Dynamic Price/Time-Bound Arrow Canvas */}
      <canvas
        ref={arrowCanvasRef}
        className="absolute inset-0 pointer-events-none z-10"
      />
    </div>
  );
};
