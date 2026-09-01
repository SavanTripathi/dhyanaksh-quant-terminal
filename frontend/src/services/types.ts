export type Timeframe = '3M' | '1M' | '1W' | '1D' | '125M' | '75M';
export type ZoneDirection = 'DEMAND' | 'SUPPLY';
export type FreshnessStatus = 'FRESH' | 'INVALIDATED';
export type AlertType = 'APPROACHING' | 'ZONE_HIT' | 'TARGET_1_HIT' | 'TARGET_2_HIT' | 'TARGET_3_HIT' | 'INVALIDATED' | 'SYSTEM_TEST';
export type AlertChannel = 'TELEGRAM' | 'WEBHOOK' | 'IN_APP';

export interface Candle {
  timestamp: string;
  time?: string | number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  timeframe?: Timeframe;
  symbol?: string;
}


export interface Zone {
  id?: number;
  symbol: string;
  timeframe: Timeframe;
  direction: ZoneDirection;
  structure: string;
  proximal_price: number;
  distal_price: number;
  freshness: FreshnessStatus;
  creation_timestamp: string;
  base_candle_count: number;
  departure_strength?: number;
  is_fresh?: boolean;
  has_opposing_violation?: boolean;
  broken_supply_level?: number;
}

export interface SpatialOverlapCluster {
  symbol: string;
  direction: ZoneDirection;
  overlap_min_price: number;
  overlap_max_price: number;
  achievements: number;
  participating_timeframes: Timeframe[];
  zones: Zone[];
  is_fresh: boolean;
  cluster_score: number;
  has_opposing_violation?: boolean;
  broken_supply_level?: number;
}

export interface TradePlan {
  id?: number;
  symbol: string;
  direction: ZoneDirection;
  current_price: number;
  overlap_min_price: number;
  overlap_max_price: number;
  entry_price: number;
  stop_loss: number;
  risk_per_share: number;
  target_1: number;
  target_2: number;
  target_3: number;
  atr_1d_14: number;
  atr_buffer: number;
  distance_pct: number;
  is_approaching: boolean;
  lifecycle_state?: string;
  ema_20?: number;
  ema_50?: number;
  sma_200?: number;
  has_ma_confluence: boolean;
  ma_confluence_details?: Record<string, any>;
  conviction_score?: number;
  conviction_grade?: string;
  conviction_breakdown?: Record<string, number>;
  catalyst_summary?: string;
  gtf_odds_score?: number;
  gtf_score_7?: number;
  gtf_entry_type?: string;
  gtf_curve_location?: string;
  gtf_curve_percent?: number;
  gtf_trend_alignment?: Record<string, string>;
  gtf_clock_position?: string;
  is_lotl_merged?: boolean;
  opposing_broken_count?: number;
  is_sector_synchronized?: boolean;
  gtf_odds_breakdown?: Record<string, number>;
  achievements: number;
  participating_timeframes: Timeframe[];
  status: string;
  cmp?: number;
  change_pct?: number;
  zone_timeframe?: '3M' | '1M' | '1W' | '1D' | string;
  proximity_state?: 'IN_ZONE' | 'APPROACHING' | 'FAR' | string;
  proximity_badge?: string;
  proximity_pct?: number;
  broken_supply_level?: number;
  has_opposing_violation?: boolean;
  is_fresh?: boolean;
  has_wdz?: boolean;
  has_mdz?: boolean;
  has_qdz?: boolean;
  has_ddz?: boolean;
  has_wsz?: boolean;
  has_msz?: boolean;
  has_qsz?: boolean;
  has_dsz?: boolean;
  all_timeframe_zones?: Record<string, { direction: string; proximal: number; distal: number; timeframe: string; proximity_badge?: string }>;
  created_at?: string;
  updated_at?: string;
}


export interface ScreenerShortlistResponse {
  total_plans: number;
  approaching_plans_count: number;
  plans: TradePlan[];
}

export interface ChartCandlesResponse {
  symbol: string;
  timeframe: Timeframe;
  count: number;
  candles: Candle[];
}

export interface ChartZonesResponse {
  symbol: string;
  fresh_zones_count: number;
  clusters_count: number;
  zones: Zone[];
  clusters: SpatialOverlapCluster[];
}

export interface AlertNotification {
  id?: number;
  trade_plan_id?: number;
  symbol: string;
  alert_type: AlertType;
  channel: AlertChannel;
  payload: Record<string, any>;
  rendered_message?: string;
  is_dispatched: boolean;
  dispatch_status: string;
  error_message?: string;
  date_iso: string;
  created_at?: string;
  dispatched_at?: string;
}

export interface AlertHistoryResponse {
  total_alerts: number;
  alerts: AlertNotification[];
}
