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
  showBrokenOpposing?: boolean;
  showVolume: boolean;
  isMultiGrid?: boolean;
  cmp?: number;
}

interface CustomDrawing {
  id: string;
  price: number;
  type: 'DEMAND_LINE' | 'SUPPLY_LINE' | 'CUSTOM_NOTE';
  label: string;
  color: string;
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
  showBrokenOpposing = false,
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
  const customDrawingLinesRef = useRef<IPriceLine[]>([]);
  const areaBandsRef = useRef<ISeriesApi<'Area'>[]>([]);
  const [containerWidth, setContainerWidth] = React.useState<number>(800);

  // Manual User Drawings (Persistent across sessions in localStorage)
  const currentSymbol = activeTradePlan?.symbol || (candles.length > 0 ? 'DEFAULT' : '');
  const [customDrawings, setCustomDrawings] = React.useState<CustomDrawing[]>(() => {
    try {
      const saved = localStorage.getItem(`custom_drawings_${currentSymbol}`);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [isDrawingMode, setIsDrawingMode] = React.useState<boolean>(false);
  const [drawToolType, setDrawToolType] = React.useState<'DEMAND' | 'SUPPLY'>('DEMAND');

  // Sync custom drawings with localStorage
  useEffect(() => {
    if (!currentSymbol) return;
    try {
      const saved = localStorage.getItem(`custom_drawings_${currentSymbol}`);
      if (saved) {
        setCustomDrawings(JSON.parse(saved));
      } else {
        setCustomDrawings([]);
      }
    } catch {}
  }, [currentSymbol]);

  const saveCustomDrawings = (drawings: CustomDrawing[]) => {
    setCustomDrawings(drawings);
    if (currentSymbol) {
      localStorage.setItem(`custom_drawings_${currentSymbol}`, JSON.stringify(drawings));
    }
  };

  const addManualZoneLine = (type: 'DEMAND' | 'SUPPLY') => {
    if (!candlestickSeriesRef.current || candles.length === 0) return;
    const latestCandle = candles[candles.length - 1];
    const basePrice = (cmp && cmp > 0) ? cmp : (activeTradePlan?.current_price || latestCandle.close);
    const targetPrice = type === 'DEMAND' ? Number((basePrice * 0.985).toFixed(2)) : Number((basePrice * 1.015).toFixed(2));
    
    const newDrawing: CustomDrawing = {
      id: `mark_${Date.now()}`,
      price: targetPrice,
      type: type === 'DEMAND' ? 'DEMAND_LINE' : 'SUPPLY_LINE',
      label: type === 'DEMAND' ? 'Manual Demand Zone' : 'Manual Supply Zone',
      color: type === 'DEMAND' ? '#3B82F6' : '#EF4444',
    };

    saveCustomDrawings([...customDrawings, newDrawing]);
  };

  const clearManualDrawings = () => {
    saveCustomDrawings([]);
  };

  const isDark = theme === 'dark';

  // Initialize Chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const bgColor = isDark ? '#131722' : '#ffffff';
    const textColor = isDark ? '#d1d4dc' : '#1e293b';
    const gridColor = isDark ? '#1e222d' : '#f1f5f9';
    const borderColor = isDark ? '#2a2e39' : '#e2e8f0';

    const container = chartContainerRef.current;
    const initialWidth = container.clientWidth || 800;
    const initialHeight = container.clientHeight || 500;
    setContainerWidth(initialWidth);

    const chart = createChart(container, {
      width: initialWidth,
      height: initialHeight,
      layout: {
        background: { type: ColorType.Solid, color: bgColor },
        textColor: textColor,
        fontFamily: "'JetBrains Mono', 'Plus Jakarta Sans', system-ui, sans-serif",
      },
      grid: {
        vertLines: {
          color: gridColor,
          style: LineStyle.Dotted,
        },
        horzLines: {
          color: gridColor,
          style: LineStyle.Dotted,
        },
      },
      crosshair: {
        mode: 1, // Magnet crosshair
        vertLine: {
          color: '#2962ff',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#2962ff',
        },
        horzLine: {
          color: '#2962ff',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#2962ff',
        },
      },
      rightPriceScale: {
        borderColor: borderColor,
        visible: true,
        scaleMargins: {
          top: isMultiGrid ? 0.12 : 0.15,
          bottom: showVolume ? 0.22 : 0.1,
        },
        autoScale: true,
      },
      timeScale: {
        borderColor: borderColor,
        timeVisible: true,
        secondsVisible: false,
        fixLeftEdge: false,
        fixRightEdge: false,
      },
    });
    chartRef.current = chart;

    // Add Primary Candlestick Series (TradingView Standard Crisp Colors)
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.05,
      },
      lastValueVisible: true,
      priceLineVisible: false, // Strict: CMP Right-Axis Badge only, no line cutting across chart
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
        top: 0.75, // Volume occupies bottom 25% of the viewport for crisp visibility
        bottom: 0.0,
      },
      visible: false,
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

    // Robust dynamic screen fitting using ResizeObserver
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

    const resizeObserver = new ResizeObserver((entries) => {
      if (!entries || entries.length === 0 || !chartRef.current) return;
      const { width, height } = entries[0].contentRect;
      if (width > 0 && height > 0) {
        setContainerWidth(width);
        chartRef.current.applyOptions({ width, height });
      }
    });

    resizeObserver.observe(container);
    window.addEventListener('resize', handleResize);
    const timeoutId = setTimeout(handleResize, 50);

    return () => {
      clearTimeout(timeoutId);
      resizeObserver.disconnect();
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
      candlestickSeriesRef.current = null;
      volumeSeriesRef.current = null;
      ema20SeriesRef.current = null;
      ema50SeriesRef.current = null;
      sma200SeriesRef.current = null;
    };
  }, [theme, isMultiGrid, showVolume]);

  // Update Data, Indicators, and Extended Canvas Zone Shading
  useEffect(() => {
    if (!candlestickSeriesRef.current || !volumeSeriesRef.current || candles.length === 0) return;

    const isIntraday = timeframe === '75M' || timeframe === '125M';
    const seenTimes = new Set<string | number>();
    const formattedCandles: CandlestickData[] = [];
    const formattedVolume: HistogramData[] = [];
    const closes: number[] = [];

    // Sort chronologically ascending
    const sorted = [...candles].sort((a, b) => {
      const timeA = new Date((a as any).time || (a as any).date || a.timestamp).getTime();
      const timeB = new Date((b as any).time || (b as any).date || b.timestamp).getTime();
      return timeA - timeB;
    });

    sorted.forEach((c) => {
      const rawTime = (c as any).time || (c as any).date || c.timestamp;
      if (!rawTime) return;

      let formattedTime: any;
      if (isIntraday) {
        // Unix timestamp in seconds (integer)
        const d = new Date(rawTime);
        formattedTime = Math.floor(d.getTime() / 1000) as any;
      } else {
        // YYYY-MM-DD string
        if (typeof rawTime === 'string' && rawTime.includes('T')) {
          formattedTime = rawTime.split('T')[0];
        } else if (typeof rawTime === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(rawTime)) {
          formattedTime = rawTime;
        } else {
          const d = new Date(rawTime);
          formattedTime = d.toISOString().split('T')[0];
        }
      }

      if (!formattedTime || seenTimes.has(formattedTime)) return;
      seenTimes.add(formattedTime);

      const open = parseFloat(c.open as any);
      const high = parseFloat(c.high as any);
      const low = parseFloat(c.low as any);
      const close = parseFloat(c.close as any);

      if (isNaN(open) || isNaN(high) || isNaN(low) || isNaN(close)) return;

      formattedCandles.push({
        time: formattedTime,
        open,
        high,
        low,
        close,
      });

      formattedVolume.push({
        time: formattedTime,
        value: c.volume || 100000,
        color: close >= open ? 'rgba(34, 197, 94, 0.65)' : 'rgba(239, 68, 68, 0.65)',
      });

      closes.push(close);
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

    if (formattedCandles.length > 0) {
      candlestickSeriesRef.current.setData(formattedCandles);
    }

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

      // Continuous Settlement CMP Tag (Right price scale tag only, no line cutting across candles)
      if (candlestickSeriesRef.current && (activeTradePlan || formattedCandles.length > 0)) {
        candlestickSeriesRef.current.applyOptions({
          lastValueVisible: true,
          priceLineVisible: false,
        });
      }

      // ==========================================
      // DEFAULT: ALWAYS RENDER STRICTLY 2 ROYAL BLUE ZONE LINES
      // ==========================================
      if (showZones && activeTradePlan) {
        const plan = activeTradePlan;
        const isDemand = plan.direction === 'DEMAND';
        const royalBlue = '#2563EB'; // Solid Royal Blue

        // 1. Proximal Entry Line (Solid Royal Blue)
        if (plan.entry_price) {
          const lEntry = candlestickSeriesRef.current.createPriceLine({
            price: plan.entry_price,
            color: royalBlue,
            lineWidth: 2,
            lineStyle: LineStyle.Solid,
            axisLabelVisible: true,
            title: '',
          });
          activePriceLinesRef.current.push(lEntry);
        }

        // 2. Distal Base Line (Zone Floor / Ceiling) (Solid Royal Blue)
        const distalPrice = isDemand ? plan.overlap_min_price : plan.overlap_max_price;
        if (distalPrice) {
          const lDistal = candlestickSeriesRef.current.createPriceLine({
            price: distalPrice,
            color: royalBlue,
            lineWidth: 2,
            lineStyle: LineStyle.Solid,
            axisLabelVisible: true,
            title: '',
          });
          activePriceLinesRef.current.push(lDistal);
        }

        // 3. Optional: Broken Opposing Zone Line (ONLY when toggled on)
        if (showBrokenOpposing) {
          const brokenLevel = plan.broken_supply_level || (plan as any).broken_supply_level;
          if (brokenLevel && brokenLevel > 0) {
            const lBroken = candlestickSeriesRef.current.createPriceLine({
              price: brokenLevel,
              color: '#38BDF8', // Sky Blue
              lineWidth: 1,
              lineStyle: LineStyle.Solid,
              axisLabelVisible: true,
              title: 'BROKEN',
            });
            activePriceLinesRef.current.push(lBroken);
          }
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

      // Render Custom User Manual Drawings (Saved in LocalStorage)
      customDrawingLinesRef.current.forEach((line) => {
        try {
          candlestickSeriesRef.current?.removePriceLine(line);
        } catch (e) {}
      });
      customDrawingLinesRef.current = [];

      customDrawings.forEach((drawing) => {
        if (!candlestickSeriesRef.current) return;
        const line = candlestickSeriesRef.current.createPriceLine({
          price: drawing.price,
          color: drawing.color,
          lineWidth: 2,
          lineStyle: LineStyle.Dotted,
          axisLabelVisible: true,
          title: drawing.type === 'DEMAND_LINE' ? 'MANUAL DZ' : 'MANUAL SZ',
        });
        customDrawingLinesRef.current.push(line);
      });

      // Clear any previous area band series
      areaBandsRef.current.forEach((s) => {
        try {
          chartRef.current?.removeSeries(s);
        } catch (e) {}
      });
      areaBandsRef.current = [];

      // Draw Institutional Price Line Boundaries
      if (showZones && clusters.length > 0 && formattedCandles.length > 0) {
        const refPrice = activeTradePlan?.current_price || activeTradePlan?.cmp || cmp || formattedCandles[formattedCandles.length - 1].close || clusters[0].overlap_min_price;
        
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
    <div className="relative w-full h-full overflow-hidden group">
      {/* Base Lightweight Charts Container */}
      <div ref={chartContainerRef} className="w-full h-full" />

      {/* Dynamic Price/Time-Bound Arrow Canvas */}
      <canvas
        ref={arrowCanvasRef}
        className="absolute inset-0 pointer-events-none z-10"
      />

      {/* Floating Manual Zone Drawing Toolbar (TradingView Style) */}
      <div className="absolute top-2 right-16 z-30 flex items-center gap-1 bg-[#131722]/90 backdrop-blur-md border border-[#2a2e39] px-2 py-1 rounded-lg shadow-lg">
        <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mr-1 hidden sm:inline">
          Mark:
        </span>
        <button
          onClick={() => addManualZoneLine('DEMAND')}
          title="Mark manual Demand Zone line at current level"
          className="px-2 py-0.5 bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 border border-blue-500/40 rounded text-[10px] font-bold flex items-center gap-1 active:scale-95 transition-all"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
          + DZ Mark
        </button>

        <button
          onClick={() => addManualZoneLine('SUPPLY')}
          title="Mark manual Supply Zone line at current level"
          className="px-2 py-0.5 bg-rose-600/20 hover:bg-rose-600/40 text-rose-400 border border-rose-500/40 rounded text-[10px] font-bold flex items-center gap-1 active:scale-95 transition-all"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
          + SZ Mark
        </button>

        {customDrawings.length > 0 && (
          <button
            onClick={clearManualDrawings}
            title="Clear all saved manual markings for this stock"
            className="px-1.5 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[10px] font-semibold active:scale-95 transition-all"
          >
            Clear ({customDrawings.length})
          </button>
        )}
      </div>
    </div>
  );
};
