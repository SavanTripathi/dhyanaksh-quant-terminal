"""
SQLAlchemy ORM Models for Instruments, Candles, Zones, Overlaps, Trade Plans, Batch Runs, and Alerts.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Enum as SQLEnum, ForeignKey, Table, JSON, Text
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.enums import (
    Timeframe, ZoneDirection, FreshnessStatus, ZoneStructure, AlertType, AlertChannel, AlertState
)


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, index=True, nullable=False)
    exchange = Column(String(20), default="NSE", nullable=False)
    market_cap_cr = Column(Float, nullable=True)  # Market Cap in Crore INR
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CandleModel(Base):
    __tablename__ = "candles"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    timeframe = Column(SQLEnum(Timeframe), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)


class ZoneModel(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    timeframe = Column(SQLEnum(Timeframe), index=True, nullable=False)
    direction = Column(SQLEnum(ZoneDirection), index=True, nullable=False)
    structure = Column(SQLEnum(ZoneStructure), nullable=False)
    proximal_price = Column(Float, nullable=False)
    distal_price = Column(Float, nullable=False)
    freshness = Column(SQLEnum(FreshnessStatus), default=FreshnessStatus.FRESH, index=True, nullable=False)
    
    creation_timestamp = Column(DateTime, index=True, nullable=False)
    penetration_timestamp = Column(DateTime, nullable=True)
    base_candle_count = Column(Integer, default=1)
    
    leg_in_time = Column(DateTime, nullable=True)
    leg_out_time = Column(DateTime, nullable=True)
    departure_strength = Column(Float, nullable=True)


class OverlapClusterModel(Base):
    __tablename__ = "overlap_clusters"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    direction = Column(SQLEnum(ZoneDirection), index=True, nullable=False)
    overlap_min_price = Column(Float, nullable=False)
    overlap_max_price = Column(Float, nullable=False)
    achievements = Column(Integer, index=True, nullable=False)  # Must be > 1
    participating_timeframes = Column(JSON, nullable=False)     # e.g. ["1M", "1W", "1D"]
    zone_ids = Column(JSON, nullable=True)                      # e.g. [12, 45, 88]
    is_fresh = Column(Boolean, default=True)
    cluster_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TradePlanModel(Base):
    __tablename__ = "trade_plans"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    direction = Column(SQLEnum(ZoneDirection), index=True, nullable=False)
    current_price = Column(Float, nullable=False)
    
    # Common zone overlap bounds
    overlap_min_price = Column(Float, nullable=False)
    overlap_max_price = Column(Float, nullable=False)
    
    # Deterministic Trade Formula Levels
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    risk_per_share = Column(Float, nullable=False)  # R
    target_1 = Column(Float, nullable=False)        # 2.0R
    target_2 = Column(Float, nullable=False)        # 3.5R
    target_3 = Column(Float, nullable=False)        # 5.0R
    
    atr_1d_14 = Column(Float, nullable=False)
    atr_buffer = Column(Float, nullable=False)      # 0.20 * ATR_1D(14)
    
    # Distance and Proximity
    distance_pct = Column(Float, nullable=False)
    is_approaching = Column(Boolean, index=True, default=False)
    lifecycle_state = Column(SQLEnum(AlertState), default=AlertState.MONITORING, index=True)
    
    # Moving Average Confluence Layer
    ema_20 = Column(Float, nullable=True)
    ema_50 = Column(Float, nullable=True)
    sma_200 = Column(Float, nullable=True)
    has_ma_confluence = Column(Boolean, default=False)
    ma_confluence_details = Column(JSON, nullable=True)
    
    # Confluence Achievements
    achievements = Column(Integer, index=True, nullable=False)
    participating_timeframes = Column(JSON, nullable=False)
    
    # Step 9: Pro Institutional Conviction Metrics (0 - 100)
    conviction_score = Column(Integer, default=75, index=True)
    conviction_grade = Column(String(50), default="TIER_1_HIGH")
    catalyst_summary = Column(Text, nullable=True)
    
    # Step 10: GTF Theory & Indicator Suite Metrics
    gtf_odds_score = Column(Float, default=11.5)
    gtf_entry_type = Column(String(50), default="TYPE_1_LIMIT_ENTRY")
    gtf_curve_location = Column(String(50), default="VERY_LOW_ON_CURVE")
    gtf_curve_percent = Column(Float, default=18.5)
    is_sector_synchronized = Column(Boolean, default=True)
    
    status = Column(String(30), default="ACTIVE", index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class BatchScanRunModel(Base):
    __tablename__ = "batch_scan_runs"

    id = Column(Integer, primary_key=True, index=True)
    scan_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    universe_count = Column(Integer, nullable=False)
    scanned_count = Column(Integer, nullable=False)
    clusters_found = Column(Integer, nullable=False)
    trade_plans_generated = Column(Integer, nullable=False)
    run_duration_seconds = Column(Float, nullable=False)
    status = Column(String(30), default="COMPLETED")
    summary_metrics = Column(JSON, nullable=True)


class AlertNotificationModel(Base):
    __tablename__ = "alert_notifications"

    id = Column(Integer, primary_key=True, index=True)
    trade_plan_id = Column(Integer, ForeignKey("trade_plans.id"), nullable=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    alert_type = Column(SQLEnum(AlertType), index=True, nullable=False)
    channel = Column(SQLEnum(AlertChannel), index=True, nullable=False)
    
    payload_json = Column(JSON, nullable=False)
    rendered_message = Column(Text, nullable=True)
    
    is_dispatched = Column(Boolean, default=False, index=True)
    dispatch_status = Column(String(30), default="PENDING")  # PENDING, SENT, FAILED, THROTTLED
    error_message = Column(Text, nullable=True)
    
    date_iso = Column(String(10), index=True, nullable=False)  # YYYY-MM-DD for deduplication
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    dispatched_at = Column(DateTime, nullable=True)


class AlertConfigurationModel(Base):
    __tablename__ = "alert_configurations"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(SQLEnum(AlertChannel), unique=True, index=True, nullable=False)
    is_enabled = Column(Boolean, default=True)
    
    # Telegram config
    telegram_bot_token = Column(String(255), nullable=True)
    telegram_chat_id = Column(String(100), nullable=True)
    
    # Webhook config
    webhook_url = Column(String(500), nullable=True)
    webhook_secret = Column(String(255), nullable=True)
    
    # Enabled triggers: ["APPROACHING", "ZONE_HIT", "TARGET_1_HIT", "INVALIDATED"]
    enabled_triggers = Column(JSON, default=lambda: ["APPROACHING", "ZONE_HIT", "TARGET_1_HIT", "INVALIDATED"])
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class BacktestRunModel(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_name = Column(String(100), nullable=False)
    symbol = Column(String(50), index=True, nullable=False)
    lookback_days = Column(Integer, default=730)
    min_achievements = Column(Integer, default=2)

    total_trades = Column(Integer, default=0)
    winning_trades_t1 = Column(Integer, default=0)
    winning_trades_t2 = Column(Integer, default=0)
    winning_trades_t3 = Column(Integer, default=0)
    loss_trades_sl = Column(Integer, default=0)
    open_trades = Column(Integer, default=0)

    win_rate_t1 = Column(Float, default=0.0)
    win_rate_t2 = Column(Float, default=0.0)
    win_rate_t3 = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    expectancy_r = Column(Float, default=0.0)
    max_drawdown_pct = Column(Float, default=0.0)
    avg_holding_days = Column(Float, default=0.0)
    avg_mae_pct = Column(Float, default=0.0)

    summary_metrics = Column(JSON, nullable=True)
    equity_curve = Column(JSON, nullable=True)
    tier_stats = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class BacktestTradeRecordModel(Base):
    __tablename__ = "backtest_trade_records"

    id = Column(Integer, primary_key=True, index=True)
    backtest_run_id = Column(Integer, ForeignKey("backtest_runs.id"), index=True, nullable=False)
    symbol = Column(String(50), index=True, nullable=False)
    direction = Column(SQLEnum(ZoneDirection), index=True, nullable=False)
    achievements = Column(Integer, nullable=False)
    participating_timeframes = Column(JSON, nullable=False)

    entry_date = Column(String(30), nullable=False)
    exit_date = Column(String(30), nullable=True)

    entry_price = Column(Float, nullable=False)
    sl_price = Column(Float, nullable=False)
    target_1 = Column(Float, nullable=False)
    target_2 = Column(Float, nullable=False)
    target_3 = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)

    exit_reason = Column(String(30), nullable=False)  # WIN_T1, WIN_T2, WIN_T3, LOSS_SL, OPEN
    pnl_r = Column(Float, default=0.0)
    pnl_amount = Column(Float, default=0.0)
    holding_days = Column(Integer, default=0)
    mae_pct = Column(Float, default=0.0)
    has_ma_confluence = Column(Boolean, default=False)


# ==========================================
# STEP 7: INSTITUTIONAL CONTEXT & REGIME MODELS
# ==========================================

class InstitutionalFlowModel(Base):
    __tablename__ = "institutional_flows"

    id = Column(Integer, primary_key=True, index=True)
    date_iso = Column(String(10), unique=True, index=True, nullable=False)  # YYYY-MM-DD
    fii_net_cash_cr = Column(Float, nullable=False)                         # in ₹ Crores
    dii_net_cash_cr = Column(Float, nullable=False)                         # in ₹ Crores
    fii_index_long_contracts = Column(Integer, nullable=False)
    fii_index_short_contracts = Column(Integer, nullable=False)
    long_short_ratio = Column(Float, nullable=False)
    regime = Column(String(50), nullable=False)                             # HEAVILY_OVERSOLD, BEARISH_DOMINANCE, NEUTRAL_RANGEBOUND, OVERBOUGHT_EXTENDED
    rolling_z_score_120d = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SectorRankingModel(Base):
    __tablename__ = "sector_rankings"

    id = Column(Integer, primary_key=True, index=True)
    sector_name = Column(String(50), index=True, nullable=False)           # NIFTY BANK, NIFTY IT, etc.
    symbol = Column(String(50), nullable=False)
    relative_ratio = Column(Float, nullable=False)
    mrs_score = Column(Float, nullable=False)                               # Mansfield Relative Strength Score
    mrs_velocity = Column(Float, nullable=False)
    quadrant = Column(String(50), index=True, nullable=False)              # OUTPERFORMING_STRENGTHENING, OUTPERFORMING_WEAKENING, UNDERPERFORMING_IMPROVING, UNDERPERFORMING_DETERIORATING
    rank = Column(Integer, nullable=False)
    date_iso = Column(String(10), index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FOIntelligenceModel(Base):
    __tablename__ = "fo_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, index=True, nullable=False)
    spot_price = Column(Float, nullable=False)
    max_pain_strike = Column(Float, nullable=False)
    pcr_oi = Column(Float, nullable=False)
    pcr_volume = Column(Float, nullable=False)
    call_resistance_wall = Column(Float, nullable=False)                   # Strike with Max Call OI
    put_support_floor = Column(Float, nullable=False)                      # Strike with Max Put OI
    buildup_type = Column(String(50), nullable=False)                      # LONG_BUILDUP, SHORT_BUILDUP, LONG_UNWINDING, SHORT_COVERING
    open_interest_json = Column(JSON, nullable=False)                      # Detailed strikes data
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


