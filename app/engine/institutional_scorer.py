"""
Step 7: Institutional Confluence Scorer (0–100 Multi-Factor Scale).
Combines Zone Achievements, Sector Relative Strength (MRS), Institutional Cash/Derivatives Flows,
and F&O Option Walls into a unified institutional conviction score.
"""
from typing import Dict, Any
from app.domain.schemas import InstitutionalScoreBreakdown


class InstitutionalScorer:
    def score_setup(
        self,
        achievements: int,
        is_sector_leading_or_emerging: bool = True,
        is_fii_supportive: bool = True,
        is_fo_wall_aligned: bool = True,
        has_ma_confluence: bool = False,
    ) -> InstitutionalScoreBreakdown:
        """
        Calculates composite 0-100 institutional conviction score.
        """
        # 1. Base HTF Zone Score: 50 pts (3-Ach = 50 pts, 2-Ach = 35 pts)
        zone_score = 50 if achievements >= 3 else 35

        # 2. Sector MRS Alignment: +15 pts (Leading or Emerging Quadrant)
        sector_score = 15 if is_sector_leading_or_emerging else 5

        # 3. FII/DII Flow Regime: +15 pts (Net buying cash flow or L/S oversold squeeze setup)
        flow_score = 15 if is_fii_supportive else 5

        # 4. F&O OI Support / PCR: +10 pts (Zone aligns with Put Floor / Call Wall)
        fo_score = 10 if is_fo_wall_aligned else 4

        # 5. Moving Average Confluence: +10 pts (50 EMA / 200 SMA nesting)
        ma_score = 10 if has_ma_confluence else 0

        total_score = min(100, zone_score + sector_score + flow_score + fo_score + ma_score)

        if total_score >= 85:
            grade = "INSTITUTIONAL_A_PLUS (Macro Prime)"
        elif total_score >= 70:
            grade = "INSTITUTIONAL_A (High Conviction)"
        elif total_score >= 55:
            grade = "STANDARD_B (Valid Confluence)"
        else:
            grade = "NEUTRAL (Low Macro Confirmation)"

        return InstitutionalScoreBreakdown(
            total_score=total_score,
            zone_base_score=zone_score,
            sector_mrs_score=sector_score,
            fii_flow_score=flow_score,
            fo_oi_alignment_score=fo_score,
            ma_confluence_score=ma_score,
            conviction_grade=grade,
        )


institutional_scorer = InstitutionalScorer()
