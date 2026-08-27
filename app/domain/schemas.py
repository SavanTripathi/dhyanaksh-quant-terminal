"""
Pydantic Schemas for Candles, Zones, Spatial Overlaps, Trade Plans, Screener, Charts, and Alerts.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.domain.enums import (
    Timeframe, ZoneDirection, FreshnessStatus, ZoneStructure, CandleType, AlertType, AlertChannel, AlertState
)


class CandleBase(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    timeframe: Timeframe
    symbol: str


class CandleSchema(CandleBase):
    candle_type: Optional[CandleType] = CandleType.NORMAL
    body_range: Optional[float] = None
    total_range: Optional[float] = None
    body_ratio: Optional[float] = None


class ZoneBase(BaseModel):
    symbol: str
    timeframe: Timeframe
    direction: ZoneDirection
    structure: ZoneStructure
    proximal_price: float
    distal_price: float
    freshness: FreshnessStatus = FreshnessStatus.FRESH
    creation_timestamp: datetime
    base_candle_count: int
    penetration_timestamp: Optional[datetime] = None


class ZoneSchema(ZoneBase):
    id: Optional[int] = None
    leg_in_time: Optional[datetime] = None
    leg_out_time: Optional[datetime] = None
    departure_strength: Optional[float] = None
    has_opposing_violation: bool = False
    broken_supply_level: Optional[float] = None


class SpatialOverlapCluster(BaseModel):
    symbol: str
    direction: ZoneDirection
    overlap_min_price: float
    overlap_max_price: float
    achievements: int = Field(
        ...,
        description="Number of overlapping timeframe zones in this spatial cluster. Must be > 1 for Tier 2/3."
    )
    participating_timeframes: List[Timeframe]
    zones: List[ZoneSchema]
    is_fresh: bool = True
    cluster_score: float = 0.0
    has_opposing_violation: bool = False
    broken_supply_level: Optional[float] = None


class TradePlanSchema(BaseModel):
    id: Optional[int] = None
    symbol: str
    direction: ZoneDirection
    current_price: float
    overlap_min_price: float
    overlap_max_price: float
    
    # Deterministic Trade Formula Levels
    entry_price: float
    stop_loss: float
    risk_per_share: float  # R
    target_1: float        # 2.0R
    target_2: float        # 3.5R
    target_3: float        # 5.0R
    
    atr_1d_14: float
    atr_buffer: float      # 0.20 * ATR_1D(14)
    
    # Distance and Proximity
    distance_pct: float
    is_approaching: bool
    lifecycle_state: AlertState = AlertState.MONITORING
    
    # Moving Average Confluences
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    sma_200: Optional[float] = None
    has_ma_confluence: bool = False
    ma_confluence_details: Optional[Dict[str, Any]] = None
    
    # Step 9: Pro Institutional Conviction Metrics (0 - 100)
    conviction_score: int = 75
    conviction_grade: str = "TIER_1_HIGH (🔥 High Conviction)"
    conviction_breakdown: Optional[Dict[str, int]] = None
    catalyst_summary: Optional[str] = None
    
    # Step 10: GTF Theory & Indicator Suite Metrics
    gtf_odds_score: float = 11.5
    gtf_entry_type: str = "TYPE_1_LIMIT_ENTRY"
    gtf_curve_location: str = "VERY_LOW_ON_CURVE"
    gtf_curve_percent: float = 18.5
    gtf_trend_alignment: Optional[Dict[str, str]] = None
    is_sector_synchronized: bool = True
    gtf_odds_breakdown: Optional[Dict[str, float]] = None
    
    # Achievements
    achievements: int
    participating_timeframes: List[Timeframe]
    status: str = "ACTIVE"
    cmp: Optional[float] = None
    change_pct: Optional[float] = 0.0
    proximity_pct: Optional[float] = None
    broken_supply_level: Optional[float] = None
    has_opposing_violation: bool = False
    is_fresh: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ScanRequest(BaseModel):
    symbol: str
    lookback_days: int = 365
    min_achievements: int = 2


class ScanResponse(BaseModel):
    symbol: str
    total_zones_detected: int
    fresh_zones_count: int
    clusters_count: int
    clusters: List[SpatialOverlapCluster]


class BatchScanRunSchema(BaseModel):
    id: Optional[int] = None
    scan_date: datetime
    universe_count: int
    scanned_count: int
    clusters_found: int
    trade_plans_generated: int
    run_duration_seconds: float
    status: str
    summary_metrics: Optional[Dict[str, Any]] = None


class ScreenerShortlistResponse(BaseModel):
    total_plans: int
    approaching_plans_count: int
    plans: List[TradePlanSchema]


class ChartCandlesResponse(BaseModel):
    symbol: str
    timeframe: Timeframe
    count: int
    candles: List[CandleSchema]


class ChartZonesResponse(BaseModel):
    symbol: str
    fresh_zones_count: int
    clusters_count: int
    zones: List[ZoneSchema]
    clusters: List[SpatialOverlapCluster]


# Step 3 Notification & Alert Schemas
class AlertPayload(BaseModel):
    symbol: str
    exchange: str = "NSE"
    alert_type: AlertType
    direction: ZoneDirection
    achievement_tier: str       # 🥇 3-ACHIEVEMENT TRIPLE CONFLUENCE / 🥈 2-ACHIEVEMENT DUAL CONFLUENCE
    achievements: int
    participating_timeframes: List[str]
    current_price: float
    distance_pct: float
    proximal_entry: float
    distal_boundary: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    risk_per_share: float
    atr_buffer: float
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    sma_200: Optional[float] = None
    has_ma_confluence: bool = False
    notes: Optional[str] = None


class AlertNotificationSchema(BaseModel):
    id: Optional[int] = None
    trade_plan_id: Optional[int] = None
    symbol: str
    alert_type: AlertType
    channel: AlertChannel
    payload: Dict[str, Any]
    rendered_message: Optional[str] = None
    is_dispatched: bool = False
    dispatch_status: str = "PENDING"
    error_message: Optional[str] = None
    date_iso: str
    created_at: Optional[datetime] = None
    dispatched_at: Optional[datetime] = None


class AlertConfigurationSchema(BaseModel):
    id: Optional[int] = None
    channel: AlertChannel
    is_enabled: bool = True
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    enabled_triggers: List[str] = ["APPROACHING", "ZONE_HIT", "TARGET_1_HIT", "INVALIDATED"]


class AlertTestRequest(BaseModel):
    channel: AlertChannel
    symbol: str = "RELIANCE"
    alert_type: AlertType = AlertType.SYSTEM_TEST
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None


class AlertTestResponse(BaseModel):
    status: str
    channel: AlertChannel
    delivered: bool
    rendered_message: str
    detail: Optional[str] = None


class AlertHistoryResponse(BaseModel):
    total_alerts: int
    alerts: List[AlertNotificationSchema]


class DispatchBatchResponse(BaseModel):
    evaluated_plans_count: int
    triggered_alerts_count: int
    dispatched_alerts_count: int
    throttled_alerts_count: int
    details: List[Dict[str, Any]]


# ==========================================
# STEP 6: BACKTEST SCHEMAS
# ==========================================

class BacktestRunRequest(BaseModel):
    symbol: str = "RELIANCE"
    lookback_days: int = Field(730, ge=90, le=2520)
    min_achievements: int = Field(2, ge=2, le=6)
    account_size: float = Field(500000.0, ge=10000.0)
    risk_per_trade_pct: float = Field(1.0, ge=0.1, le=10.0)


class BacktestTradeRecordSchema(BaseModel):
    id: Optional[int] = None
    symbol: str
    direction: ZoneDirection
    achievements: int
    participating_timeframes: List[Timeframe]
    entry_date: str
    exit_date: Optional[str] = None
    entry_price: float
    sl_price: float
    target_1: float
    target_2: float
    target_3: float
    exit_price: Optional[float] = None
    exit_reason: str  # WIN_T1, WIN_T2, WIN_T3, LOSS_SL, OPEN
    pnl_r: float
    pnl_amount: float
    holding_days: int
    mae_pct: float
    has_ma_confluence: bool = False


class EquityCurvePoint(BaseModel):
    date: str
    cumulative_pnl_r: float
    equity_value: float
    drawdown_pct: float


class TierComparisonStats(BaseModel):
    tier_name: str
    total_setups: int
    win_rate_t1: float
    win_rate_t2: float
    win_rate_t3: float
    profit_factor: float
    expectancy_r: float
    avg_mae_pct: float


class BacktestResultsResponse(BaseModel):
    run_id: int
    run_name: str
    symbol: str
    lookback_days: int
    min_achievements: int
    total_trades: int
    winning_trades_t1: int
    winning_trades_t2: int
    winning_trades_t3: int
    loss_trades_sl: int
    open_trades: int
    win_rate_t1: float
    win_rate_t2: float
    win_rate_t3: float
    profit_factor: float
    expectancy_r: float
    max_drawdown_pct: float
    avg_holding_days: float
    avg_mae_pct: float
    equity_curve: List[EquityCurvePoint]
    tier_comparison: List[TierComparisonStats]
    trades: List[BacktestTradeRecordSchema]
    created_at: datetime


# ==========================================
# STEP 7: INSTITUTIONAL REGIME & F&O SCHEMAS
# ==========================================

class MarketRegimeResponse(BaseModel):
    date_iso: str
    nifty_50_price: float
    nifty_50_trend: str
    fii_net_cash_cr: float
    dii_net_cash_cr: float
    fii_long_contracts: int
    fii_short_contracts: int
    long_short_ratio: float
    regime: str  # HEAVILY_OVERSOLD, BEARISH_DOMINANCE, NEUTRAL_RANGEBOUND, OVERBOUGHT_EXTENDED
    regime_description: str
    rolling_z_score_120d: float
    market_breadth_adv_dec_ratio: float
    updated_at: datetime


class SectorRankingSchema(BaseModel):
    sector_name: str
    symbol: str
    relative_ratio: float
    mrs_score: float
    mrs_velocity: float
    quadrant: str  # OUTPERFORMING_STRENGTHENING, OUTPERFORMING_WEAKENING, UNDERPERFORMING_IMPROVING, UNDERPERFORMING_DETERIORATING
    rank: int


class SectorRotationResponse(BaseModel):
    date_iso: str
    benchmark_symbol: str = "NIFTY50"
    total_sectors: int
    leading_sectors: List[str]
    emerging_sectors: List[str]
    sectors: List[SectorRankingSchema]
    updated_at: datetime


class FOStrikeOIData(BaseModel):
    strike_price: float
    call_oi: int
    put_oi: int
    call_volume: int
    put_volume: int
    call_change_oi: int
    put_change_oi: int


class FOIntelligenceResponse(BaseModel):
    symbol: str
    spot_price: float
    max_pain_strike: float
    pcr_oi: float
    pcr_volume: float
    call_resistance_wall: float
    put_support_floor: float
    buildup_type: str  # LONG_BUILDUP, SHORT_BUILDUP, LONG_UNWINDING, SHORT_COVERING
    buildup_bias: str  # BULLISH, BEARISH, NEUTRAL
    strikes: List[FOStrikeOIData]
    updated_at: datetime


class InstitutionalScoreBreakdown(BaseModel):
    total_score: int  # 0 - 100
    zone_base_score: int
    sector_mrs_score: int
    fii_flow_score: int
    fo_oi_alignment_score: int
    ma_confluence_score: int
    conviction_grade: str  # INSTITUTIONAL_A_PLUS, INSTITUTIONAL_A, STANDARD_B, NEUTRAL


