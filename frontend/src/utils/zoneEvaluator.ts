import { TradePlan, Timeframe, ZoneDirection } from '../services/types';

export interface ZoneMatchResult {
  isMatch: boolean;
  relationship: 'INSIDE' | 'APPROACHING' | 'FAR' | 'NONE';
  proximal?: number;
  distal?: number;
  badge?: string;
}

/**
 * Deterministically evaluates if a stock's current price is actively interacting
 * with a valid zone on the specified timeframe and direction.
 * 
 * Criteria:
 * Match = (Zone Direction) AND (Exact Timeframe) AND (Zone Validity) AND (Active Proximity: IN_ZONE or APPROACHING <= 3.5%)
 */
export function evaluateZoneMatch(
  stock: TradePlan,
  targetTimeframe: '3M' | '1M' | '1W' | '1D',
  targetDirection: 'ALL' | ZoneDirection
): ZoneMatchResult {
  const isDemand = stock.direction === 'DEMAND';
  const isSupply = stock.direction === 'SUPPLY';

  // Check direction alignment
  if (targetDirection !== 'ALL' && stock.direction !== targetDirection) {
    return { isMatch: false, relationship: 'NONE' };
  }

  // Check timeframe presence
  const hasTargetDemand =
    targetTimeframe === '3M' ? Boolean(stock.has_qdz) :
    targetTimeframe === '1M' ? Boolean(stock.has_mdz) :
    targetTimeframe === '1W' ? Boolean(stock.has_wdz) :
    Boolean(stock.has_ddz);

  const hasTargetSupply =
    targetTimeframe === '3M' ? Boolean(stock.has_qsz) :
    targetTimeframe === '1M' ? Boolean(stock.has_msz) :
    targetTimeframe === '1W' ? Boolean(stock.has_wsz) :
    Boolean(stock.has_dsz);

  const hasZoneForDirection = isDemand ? hasTargetDemand : isSupply ? hasTargetSupply : (hasTargetDemand || hasTargetSupply);

  // Exact primary zone match
  const isExactPrimary = stock.zone_timeframe === targetTimeframe;

  // If this timeframe has an active zone or is the primary timeframe with valid proximity
  if (hasZoneForDirection || isExactPrimary) {
    const isInside = stock.proximity_state === 'IN_ZONE' || (stock.distance_pct !== undefined && stock.distance_pct <= 0.3);
    const isApproaching = stock.is_approaching || (stock.distance_pct !== undefined && stock.distance_pct <= 3.5);

    if (isInside || isApproaching) {
      const rel = isInside ? 'INSIDE' : 'APPROACHING';
      const tagPrefix = isDemand
        ? (targetTimeframe === '3M' ? 'QDZ' : targetTimeframe === '1M' ? 'MDZ' : targetTimeframe === '1W' ? 'WDZ' : 'DDZ')
        : (targetTimeframe === '3M' ? 'QSZ' : targetTimeframe === '1M' ? 'MSZ' : targetTimeframe === '1W' ? 'WSZ' : 'DSZ');

      const entryPrice = stock.entry_price || stock.current_price;
      const badge = isInside
        ? `${isDemand ? '🟢' : '🔴'} INSIDE ${tagPrefix} (₹${entryPrice.toFixed(1)})`
        : `${isDemand ? '🟡' : '🟠'} APP ${tagPrefix} (${(stock.distance_pct || 1.5).toFixed(1)}%)`;

      return {
        isMatch: true,
        relationship: rel,
        proximal: stock.entry_price,
        distal: stock.stop_loss,
        badge,
      };
    }
  }

  return { isMatch: false, relationship: 'NONE' };
}

/**
 * 👑 ATZ (All Timeframe Zones) Strict Intersection:
 * Match(QDZ) AND Match(MDZ) AND Match(WDZ) AND Match(DDZ) for DEMAND (or QSZ/MSZ/WSZ/DSZ for SUPPLY)
 */
export function evaluateATZMatch(stock: TradePlan, targetDirection: 'ALL' | ZoneDirection): boolean {
  if (targetDirection !== 'ALL' && stock.direction !== targetDirection) {
    return false;
  }

  if (stock.direction === 'DEMAND') {
    return Boolean(stock.has_qdz && stock.has_mdz && stock.has_wdz && stock.has_ddz);
  } else {
    return Boolean(stock.has_qsz && stock.has_msz && stock.has_wsz && stock.has_dsz);
  }
}
