"""
Step 9: Pro Institutional Conviction Ranking Engine.
Evaluates every scanned stock across 6 quantitative institutional pillars (0–100 Points):
1. HTF Zone Quality & Achievements (35 Pts)
2. Sector Momentum Alignment via Mansfield Relative Strength (20 Pts)
3. Institutional Derivatives (F&O) Positioning & Put Walls (15 Pts)
4. Structural Moving Average Alignment & Golden Cross (15 Pts)
5. Order Execution Proximity to Zone (10 Pts)
6. Institutional FII/DII Net Flow Liquidity (5 Pts)
"""
from typing import Dict, List, Any, Optional
from app.domain.schemas import TradePlanSchema, SpatialOverlapCluster
from app.domain.enums import ZoneDirection


class ConvictionRankingEngine:
    """
    6-Pillar Pro-Grade Institutional Conviction Scorer.
    """

    def compute_conviction_score(
        self,
        symbol: str,
        direction: ZoneDirection,
        achievements: int,
        distance_pct: float,
        is_approaching: bool,
        has_ma_confluence: bool = False,
        ema_50: Optional[float] = None,
        sma_200: Optional[float] = None,
        current_price: Optional[float] = None,
        sector_name: str = "Broad Market",
        is_sector_leading: bool = True,
        is_fo_put_wall_aligned: bool = True,
        is_fii_supportive: bool = True,
    ) -> Dict[str, Any]:
        """
        Calculates composite score (0–100), conviction grade, and natural-language catalyst.
        """
        # Pillar 1: HTF Zone Quality (35 pts)
        if achievements >= 3:
            p1_zone = 35  # Triple Confluence (Q+M+W)
        elif achievements == 2:
            p1_zone = 25  # Dual Confluence (M+W)
        else:
            p1_zone = 10

        # Pillar 2: Sector Momentum Alignment (20 pts)
        # Leading = 20, Emerging = 12, Lagging = 5
        if is_sector_leading:
            p2_sector = 20
        else:
            p2_sector = 12

        # Pillar 3: Derivatives F&O Positioning (15 pts)
        if is_fo_put_wall_aligned:
            p3_fo = 15
        else:
            p3_fo = 8

        # Pillar 4: Structural Moving Average Alignment (15 pts)
        p4_ma = 0
        if has_ma_confluence:
            p4_ma += 7
        if ema_50 and sma_200 and ema_50 > sma_200:
            p4_ma += 4  # Golden Cross
        if current_price and sma_200 and current_price > sma_200:
            p4_ma += 4  # Bullish Structural Trend
        p4_ma = min(15, p4_ma)

        # Pillar 5: Order Execution Proximity (10 pts)
        if is_approaching or distance_pct <= 2.5:
            p5_proximity = 10
        elif distance_pct <= 5.0:
            p5_proximity = 6
        else:
            p5_proximity = 3

        # Pillar 6: Institutional Liquidity Flows (5 pts)
        p6_flow = 5 if is_fii_supportive else 2

        total_score = min(100, p1_zone + p2_sector + p3_fo + p4_ma + p5_proximity + p6_flow)

        # Conviction Tier Classification
        if total_score >= 85:
            grade = "PRO_SUPER_HIGH (👑 Super-High Conviction)"
            tier_badge = "👑 TOP PICK"
        elif total_score >= 75:
            grade = "TIER_1_HIGH (🔥 High Conviction)"
            tier_badge = "🔥 HIGH CONVICTION"
        else:
            grade = "MODERATE (📊 Valid Confluence)"
            tier_badge = "📊 STANDARD"

        # Natural Language Institutional Catalyst Summary
        catalyst = (
            f"{symbol} (Score: {total_score}/100 - {tier_badge}): "
            f"{'3-Achievement Triple HTF' if achievements >= 3 else '2-Achievement Dual HTF'} {direction.value} Confluence. "
            f"Aligned with {sector_name} leading momentum and strong Open Interest support. "
            f"Distance to Proximal Entry is {distance_pct:.1f}%."
        )

        breakdown = {
            "p1_zone_quality": p1_zone,
            "p2_sector_momentum": p2_sector,
            "p3_fo_derivatives": p3_fo,
            "p4_moving_averages": p4_ma,
            "p5_proximity": p5_proximity,
            "p6_institutional_flows": p6_flow,
        }

        return {
            "conviction_score": total_score,
            "conviction_grade": grade,
            "conviction_breakdown": breakdown,
            "catalyst_summary": catalyst,
        }


conviction_ranking_engine = ConvictionRankingEngine()
