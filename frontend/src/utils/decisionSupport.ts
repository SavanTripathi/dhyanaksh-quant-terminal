import { TradePlan } from '../services/types';

/**
 * Returns the count of aligned timeframes (out of 4) matching the plan's direction.
 */
export function getConfluenceCount(plan: TradePlan): number {
  const isDemand = plan.direction === 'DEMAND';
  if (isDemand) {
    return [plan.has_qdz, plan.has_mdz, plan.has_wdz, plan.has_ddz].filter(Boolean).length;
  } else {
    return [plan.has_qsz, plan.has_msz, plan.has_wsz, plan.has_dsz].filter(Boolean).length;
  }
}

/**
 * Checks if a trade plan qualifies as a Tier A Actionable candidate.
 * - Distance to proximal <= 1.50% (shallow test or proximal approach)
 * - Multi-timeframe confluence >= 3 of 4 timeframes
 */
export function isTierACandidate(plan: TradePlan): boolean {
  const dist = Math.abs(plan.distance_pct ?? 99);
  const confluence = getConfluenceCount(plan);
  return dist <= 1.50 && confluence >= 3;
}

export interface ZonePenetrationInfo {
  type: 'SHALLOW' | 'MEDIUM' | 'DEEP' | 'APPROACHING';
  label: string;
  badgeText: string;
  colorClass: string;
  depthPct: number;
}

/**
 * Computes zone penetration depth and assigns institutional execution rating:
 * - Shallow (<2%): Optimal Set & Forget entry (fresh institutional orders)
 * - Medium (2-5%): Moderate penetration, caution warranted
 * - Deep (>5%): Depleted base, heightened risk of distal breach
 * - Approaching: Outside proximal boundary
 */
export function getZonePenetration(plan: TradePlan): ZonePenetrationInfo {
  const dist = plan.distance_pct ?? 0;
  const isInside = plan.proximity_state === 'IN_ZONE' || dist < 0;
  const absDist = Math.abs(dist);

  if (isInside) {
    if (absDist <= 2.0) {
      return {
        type: 'SHALLOW',
        label: 'Shallow Test (Optimal)',
        badgeText: `🟢 Shallow (${absDist.toFixed(1)}%)`,
        colorClass: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
        depthPct: absDist,
      };
    } else if (absDist <= 5.0) {
      return {
        type: 'MEDIUM',
        label: 'Medium Test (Moderate)',
        badgeText: `🟡 Mid-Base (${absDist.toFixed(1)}%)`,
        colorClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
        depthPct: absDist,
      };
    } else {
      return {
        type: 'DEEP',
        label: 'Deep / Depleted (High Risk)',
        badgeText: `🔴 Deep (${absDist.toFixed(1)}%)`,
        colorClass: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
        depthPct: absDist,
      };
    }
  } else {
    // Approaching
    if (absDist <= 0.5) {
      return {
        type: 'SHALLOW',
        label: 'At Proximal Line',
        badgeText: `⚡ At Proximal (+${absDist.toFixed(1)}%)`,
        colorClass: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
        depthPct: absDist,
      };
    } else {
      return {
        type: 'APPROACHING',
        label: 'Approaching Zone',
        badgeText: `🎯 Approaching (+${absDist.toFixed(1)}%)`,
        colorClass: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
        depthPct: absDist,
      };
    }
  }
}

export interface OpposingClearanceInfo {
  hasOpposing: boolean;
  opposingTf: string | null;
  opposingProximal: number | null;
  rClearance: number | null;
  isClear: boolean;
  badgeText: string;
  colorClass: string;
}

/**
 * Calculates distance to nearest opposing HTF zone (3M, 1M, 1W) in R multiples.
 */
export function getOpposingClearance(plan: TradePlan): OpposingClearanceInfo {
  const isDemand = plan.direction === 'DEMAND';
  const oppDir = isDemand ? 'SUPPLY' : 'DEMAND';
  const entry = plan.entry_price || plan.current_price || 0;
  const sl = plan.stop_loss || 0;
  const r = plan.risk_per_share || Math.abs(entry - sl) || 1;

  const atz = plan.all_timeframe_zones || {};
  let nearestOppProx: number | null = null;
  let nearestOppTf: string | null = null;
  let minDiff = Infinity;

  for (const tf of ['3M', '1M', '1W'] as const) {
    const zone = atz[tf];
    if (zone && zone.direction === oppDir && zone.proximal !== undefined) {
      const prox = zone.proximal;
      if (isDemand && prox > entry) {
        const diff = prox - entry;
        if (diff < minDiff) {
          minDiff = diff;
          nearestOppProx = prox;
          nearestOppTf = tf;
        }
      } else if (!isDemand && prox < entry) {
        const diff = entry - prox;
        if (diff < minDiff) {
          minDiff = diff;
          nearestOppProx = prox;
          nearestOppTf = tf;
        }
      }
    }
  }

  if (nearestOppProx !== null && minDiff !== Infinity) {
    const rClearance = minDiff / r;
    const isClear = rClearance >= 2.0;
    return {
      hasOpposing: true,
      opposingTf: nearestOppTf,
      opposingProximal: nearestOppProx,
      rClearance: Number(rClearance.toFixed(1)),
      isClear,
      badgeText: isClear
        ? `⚡ Runway: ${rClearance.toFixed(1)}R (${nearestOppTf})`
        : `⚠️ Opposing: ${rClearance.toFixed(1)}R (${nearestOppTf})`,
      colorClass: isClear
        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
        : 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    };
  }

  return {
    hasOpposing: false,
    opposingTf: null,
    opposingProximal: null,
    rClearance: null,
    isClear: true,
    badgeText: '🚀 HTF Unobstructed (>3R)',
    colorClass: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  };
}

/**
 * Sorts and filters Tier A Actionable candidates.
 */
export function rankTierAPlans(plans: TradePlan[]): TradePlan[] {
  const tierA = plans.filter(isTierACandidate);

  return tierA.sort((a, b) => {
    const confA = getConfluenceCount(a);
    const confB = getConfluenceCount(b);
    if (confB !== confA) return confB - confA; // 4/4 before 3/4

    const distA = Math.abs(a.distance_pct ?? 99);
    const distB = Math.abs(b.distance_pct ?? 99);
    if (distA !== distB) return distA - distB; // closer to proximal first

    const convA = a.conviction_score || a.gtf_odds_score || 0;
    const convB = b.conviction_score || b.gtf_odds_score || 0;
    return convB - convA;
  });
}
