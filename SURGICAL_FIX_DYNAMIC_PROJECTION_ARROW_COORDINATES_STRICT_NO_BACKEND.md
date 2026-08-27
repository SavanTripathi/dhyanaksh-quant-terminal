# STRICT FRONTEND SURGICAL DIRECTIVE — DYNAMIC CHART COORDINATE PROJECTION ARROW (ZERO BACKEND TOUCH)

## Project Name
**Dhyanaksh — HTF Supply & Demand Quant Terminal**

---

### STRICT GUARDRAILS (DO NOT TOUCH THE BACKEND)
> 1. **DO NOT MODIFY ANY BACKEND FILES:** Zero changes permitted to `app/`, python scripts, SQLite databases, schemas, endpoints, or cron schedulers.
> 2. **DO NOT ALTER PRICING OR GTF ZONE MODELS:** Keep all continuous CMP logic, 1-click alert handlers, and confluence scoring 100% frozen.
> 3. **FRONTEND UI/CHART WORKSPACE ONLY:** Focus strictly on `frontend/src/components/chart/TradingViewChart.tsx` (and `MultiChartGrid.tsx` if applicable).

---

### 1. Root Cause Analysis
The blue "Bullish Take-off" projection arrow pointing toward Target 3 is currently rendered as a fixed DOM/SVG overlay. When panning or zooming the chart, the Lightweight Charts canvas updates its internal price/time scale, but the static overlay remains fixed in screen pixels, causing the arrow to drift and disconnect from the actual price levels.

---

### 2. Frontend Surgical Implementation (`frontend/src/components/chart/TradingViewChart.tsx`)

Replace the static HTML/SVG overlay with a transparent dynamic canvas bound directly to the Lightweight Charts Coordinate API (`timeToCoordinate` and `priceToCoordinate`), recalculating on every zoom/pan event.

```tsx
// Inside TradingViewChart.tsx

// 1. Add Canvas Ref
const arrowCanvasRef = useRef<HTMLCanvasElement | null>(null);

// 2. Dynamic Arrow Draw Function
const drawDynamicProjectionArrow = () => {
  if (
    !chartRef.current ||
    !candlestickSeriesRef.current ||
    !activeTradePlan ||
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
  canvas.width = width;
  canvas.height = height;
  ctx.clearRect(0, 0, width, height);

  const isDemand = activeTradePlan.zone_type?.toUpperCase().includes('DEMAND') ?? (activeTradePlan.direction === 'DEMAND');
  const startPrice = activeTradePlan.entry_price;
  const endPrice = activeTradePlan.target_3 || activeTradePlan.target_1 || activeTradePlan.stop_loss;

  if (!startPrice || !endPrice || !candleData || candleData.length === 0) return;

  // Convert Logical/Price Coordinates to Exact Canvas (X, Y) Pixels
  const lastCandle = candleData[candleData.length - 1];
  const startX = timeScale.timeToCoordinate(lastCandle.time);
  const startY = series.priceToCoordinate(startPrice);
  const endY = series.priceToCoordinate(endPrice);

  if (startX === null || startY === null || endY === null) {
    return; // Price or time coordinate is currently off-screen
  }

  // Project forward ~120px in time
  const endX = Math.min(width - 60, startX + 130);

  // Render Dynamic Arrow & Trajectory
  ctx.save();
  const accentColor = isDemand ? '#06B6D4' : '#F43F5E'; // Cyan for Demand, Rose for Supply
  ctx.strokeStyle = accentColor;
  ctx.fillStyle = accentColor;
  ctx.lineWidth = 2;
  ctx.setLineDash([5, 4]);

  // Path line
  ctx.beginPath();
  ctx.moveTo(startX, startY);
  ctx.lineTo(endX, endY);
  ctx.stroke();

  // Arrow Head
  ctx.setLineDash([]);
  const headLength = 9;
  const angle = Math.atan2(endY - startY, endX - startX);
  ctx.beginPath();
  ctx.moveTo(endX, endY);
  ctx.lineTo(endX - headLength * Math.cos(angle - Math.PI / 6), endY - headLength * Math.sin(angle - Math.PI / 6));
  ctx.lineTo(endX - headLength * Math.cos(angle + Math.PI / 6), endY - headLength * Math.sin(angle + Math.PI / 6));
  ctx.closePath();
  ctx.fill();

  // Target Label
  ctx.font = 'bold 10px Inter, sans-serif';
  ctx.fillText(
    `${isDemand ? '🚀 Target' : '🔻 SL/Target'} ₹${endPrice.toFixed(2)}`,
    endX + 6,
    endY + 3
  );

  ctx.restore();
};

// 3. Subscribe to Pan, Zoom & Viewport Resize Events
useEffect(() => {
  if (!chartRef.current) return;

  const timeScale = chartRef.current.timeScale();

  const handleViewportUpdate = () => {
    requestAnimationFrame(drawDynamicProjectionArrow);
  };

  timeScale.subscribeVisibleTimeRangeChange(handleViewportUpdate);
  timeScale.subscribeVisibleLogicalRangeChange(handleViewportUpdate);
  window.addEventListener('resize', handleViewportUpdate);

  // Initial call
  drawDynamicProjectionArrow();

  return () => {
    timeScale.unsubscribeVisibleTimeRangeChange(handleViewportUpdate);
    timeScale.unsubscribeVisibleLogicalRangeChange(handleViewportUpdate);
    window.removeEventListener('resize', handleViewportUpdate);
  };
}, [candleData, activeTradePlan]);
```

### 3. Layering in Chart JSX Structure
Ensure the canvas overlay sits directly on top of the chart container with pointer-events-none so mouse dragging and wheel zooming are never blocked:

```tsx
<div className="relative w-full h-full overflow-hidden">
  {/* Base Lightweight Charts Container */}
  <div ref={chartContainerRef} className="w-full h-full" />

  {/* Dynamic Price/Time-Bound Arrow Canvas */}
  <canvas
    ref={arrowCanvasRef}
    className="absolute inset-0 pointer-events-none z-10"
  />
</div>
```

---

### 4. Verification & Acceptance Criteria
- [ ] Backend is completely untouched (`git status` shows zero modifications in `app/`).
- [ ] When zooming in, zooming out, or panning horizontally, the projection arrow stays pinned to the exact entry price and target price levels.
- [ ] No drifting, floating, or static disconnect occurs.
- [ ] `npm run build` completes with 0 errors.
- [ ] Deliver a Dynamic Chart Coordinate Arrow Audit Report.
