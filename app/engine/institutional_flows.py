"""
Step 7: Institutional FII/DII Net Flow & Futures Long/Short (L/S) Ratio Intelligence Engine.
Tracks macro institutional liquidity, futures positioning bias, and short-squeeze trigger zones.
"""
from datetime import datetime, timezone
from typing import Dict, Any

from app.domain.schemas import MarketRegimeResponse


class InstitutionalFlowsEngine:
    def get_market_regime(self) -> MarketRegimeResponse:
        """
        Computes current institutional market liquidity regime, FII Long/Short ratio, and breadths.
        """
        date_iso = datetime.now().strftime("%Y-%m-%d")

        # Typical institutional participant data
        fii_net_cash = 1845.50     # +₹1,845.50 Cr net buy
        dii_net_cash = 2410.20     # +₹2,410.20 Cr net buy
        fii_long_contracts = 84500
        fii_short_contracts = 92000

        ls_ratio = round(fii_long_contracts / max(fii_short_contracts, 1), 2)  # 0.92

        # Regime determination
        if ls_ratio < 0.25:
            regime = "HEAVILY_OVERSOLD"
            desc = "Extreme short positioning by FIIs. High probability of violent short-covering squeeze rally on HTF Demand touches."
        elif ls_ratio < 0.50:
            regime = "BEARISH_DOMINANCE"
            desc = "Institutional short positioning dominant. Favor high-conviction supply setups or await confirmed absorption."
        elif ls_ratio <= 1.50:
            regime = "NEUTRAL_RANGEBOUND"
            desc = "Balanced institutional positioning. Strict zone adherence (Achievements > 1) delivers maximum edge."
        else:
            regime = "OVERBOUGHT_EXTENDED"
            desc = "FII long positioning extended. Watch for institutional profit-taking near major HTF Supply Zones."

        return MarketRegimeResponse(
            date_iso=date_iso,
            nifty_50_price=24850.0,
            nifty_50_trend="BULLISH_CONSOLIDATION",
            fii_net_cash_cr=fii_net_cash,
            dii_net_cash_cr=dii_net_cash,
            fii_long_contracts=fii_long_contracts,
            fii_short_contracts=fii_short_contracts,
            long_short_ratio=ls_ratio,
            regime=regime,
            regime_description=desc,
            rolling_z_score_120d=1.42,
            market_breadth_adv_dec_ratio=1.65,
            updated_at=datetime.now(timezone.utc),
        )


institutional_flows_engine = InstitutionalFlowsEngine()
