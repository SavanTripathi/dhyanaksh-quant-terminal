import { TradePlan, Candle } from '../services/types';
import universeSetupsJson from './nifty500_universe_setups.json';

// Complete NIFTY 500 scanned universe seed for 100% immediate full-tab hydration
export const DEFAULT_INITIAL_SETUPS: TradePlan[] = (universeSetupsJson as any[]).map((s, idx) => ({
  id: idx + 100,
  symbol: s.symbol,
  name: s.name || s.symbol,
  direction: s.direction || 'DEMAND',
  current_price: s.current_price || s.cmp || 1000.0,
  overlap_min_price: s.overlap_min_price || s.distal_price || 950.0,
  overlap_max_price: s.overlap_max_price || s.proximal_price || 1000.0,
  entry_price: s.entry_price || s.proximal_price || 1000.0,
  stop_loss: s.stop_loss || s.distal_price || 950.0,
  risk_per_share: s.risk_per_share || Math.abs((s.proximal_price || 1000) - (s.distal_price || 950)),
  target_1: s.target_1 || (s.proximal_price ? s.proximal_price * 1.02 : 1020.0),
  target_2: s.target_2 || (s.proximal_price ? s.proximal_price * 1.035 : 1035.0),
  target_3: s.target_3 || (s.proximal_price ? s.proximal_price * 1.05 : 1050.0),
  atr_1d_14: s.atr_1d_14 || 15.0,
  atr_buffer: s.atr_buffer || 3.0,
  distance_pct: s.distance_pct !== undefined ? s.distance_pct : 0.2,
  is_approaching: s.is_approaching !== undefined ? s.is_approaching : true,
  has_ma_confluence: s.has_ma_confluence !== undefined ? s.has_ma_confluence : true,
  conviction_score: s.conviction_score || s.score || 85,
  conviction_grade: s.conviction_grade || 'TIER_1_HIGH',
  catalyst_summary: s.catalyst_summary || `${s.zone_timeframe || '1W'} ${s.direction || 'DEMAND'} origin setup`,
  gtf_odds_score: s.gtf_odds_score || 11.5,
  gtf_entry_type: s.gtf_entry_type || 'TYPE_1_LIMIT_ENTRY',
  gtf_curve_location: s.gtf_curve_location || (s.direction === 'DEMAND' ? 'VERY_LOW_ON_CURVE' : 'VERY_HIGH_ON_CURVE'),
  gtf_curve_percent: s.gtf_curve_percent || 20.0,
  is_sector_synchronized: true,
  achievements: s.achievements || 2,
  participating_timeframes: (s.participating_timeframes || [s.zone_timeframe || '1W']) as any,
  status: s.status || 'ACTIVE',
  cmp: s.cmp || s.current_price || 1000.0,
  change_pct: s.change_pct || 0.0,
  zone_timeframe: s.zone_timeframe || '1W',
  proximity_state: s.proximity_state || 'IN_ZONE',
  proximity_badge: s.proximity_badge,
  proximity_pct: s.proximity_pct || s.distance_pct || 0.2,
  broken_supply_level: s.broken_supply_level,
  has_opposing_violation: s.has_opposing_violation || false,
  has_wdz: s.has_wdz,
  has_mdz: s.has_mdz,
  has_qdz: s.has_qdz,
  has_ddz: s.has_ddz,
  has_wsz: s.has_wsz,
  has_msz: s.has_msz,
  has_qsz: s.has_qsz,
  has_dsz: s.has_dsz,
  all_timeframe_zones: s.all_timeframe_zones,
  is_fresh: true,
  created_at: s.created_at || new Date().toISOString(),
}));

// Helper to generate synthetic high-fidelity fallback candles for instant chart mount
export const generateFallbackCandles = (symbol: string, tf: string = '1W', baseCmp?: number): Candle[] => {
  const map: Record<string, number> = {
    TMPV: 318.45,
    ABBOTINDIA: 26175.0,
    SBIN: 1045.0,
    COFORGE: 1981.0,
    BAJFINANCE: 1056.0,
  };

  const price = baseCmp || map[symbol.toUpperCase()] || 1000.0;
  const isIntraday = tf === '75M' || tf === '125M';
  const count = 60;
  const candles: Candle[] = [];
  const now = Date.now();
  const stepMs = tf === '1W' ? 7 * 86400 * 1000 : tf === '1M' ? 30 * 86400 * 1000 : tf === '3M' ? 90 * 86400 * 1000 : 86400 * 1000;

  let curr = price * 0.92;
  for (let i = count; i >= 0; i--) {
    const timeVal = new Date(now - i * stepMs);
    const dateStr = isIntraday ? Math.floor(timeVal.getTime() / 1000) : timeVal.toISOString().split('T')[0];
    const isLast = i === 0;
    
    let open = isLast ? price * 0.995 : curr;
    let close = isLast ? price : curr * (1 + (Math.sin(i) * 0.02 + 0.005));
    let high = Math.max(open, close) * (1 + 0.012);
    let low = Math.min(open, close) * (1 - 0.012);

    candles.push({
      timestamp: timeVal.toISOString(),
      time: dateStr as any,
      open: Math.round(open * 100) / 100,
      high: Math.round(high * 100) / 100,
      low: Math.round(low * 100) / 100,
      close: Math.round(close * 100) / 100,
      volume: 1500000 + Math.floor(Math.sin(i) * 500000),
    });

    curr = close;
  }

  return candles;
};
