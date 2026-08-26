"""
Technical Indicator Suite.
Provides vectorized calculations for:
- ATR (Average True Range, default period 14)
- EMA (Exponential Moving Average, default 20 & 50)
- SMA (Simple Moving Average, default 200)
- ATR Buffer (0.20 * ATR_1D(14))
"""
from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np


class IndicatorEngine:
    """
    Vectorized technical indicators for Daily (1D) series.
    """

    @staticmethod
    def calculate_true_range(df: pd.DataFrame) -> pd.Series:
        """
        True Range = max(High - Low, |High - PrevClose|, |Low - PrevClose|)
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr

    @classmethod
    def calculate_atr(cls, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculates ATR using standard Wilder's smoothing / EMA approach.
        """
        if len(df) < period:
            # Fallback for short series
            return (df["high"] - df["low"]).rolling(window=min(len(df), period), min_periods=1).mean()

        tr = cls.calculate_true_range(df)
        atr = tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        # Fill leading NaNs with simple rolling mean
        atr = atr.fillna(tr.rolling(period, min_periods=1).mean())
        return atr

    @staticmethod
    def calculate_ema(series: pd.Series, span: int) -> pd.Series:
        """
        Calculates Exponential Moving Average.
        """
        return series.ewm(span=span, adjust=False).mean()

    @staticmethod
    def calculate_sma(series: pd.Series, window: int) -> pd.Series:
        """
        Calculates Simple Moving Average.
        """
        return series.rolling(window=window, min_periods=1).mean()

    @classmethod
    def compute_daily_indicators(cls, daily_df: pd.DataFrame) -> Dict[str, float]:
        """
        Computes the latest ATR(14), 0.20*ATR buffer, 20 EMA, 50 EMA, and 200 SMA
        for a given daily DataFrame.
        """
        if daily_df.empty:
            return {
                "atr_14": 0.0,
                "atr_buffer": 0.0,
                "ema_20": 0.0,
                "ema_50": 0.0,
                "sma_200": 0.0,
                "current_price": 0.0
            }

        df = daily_df.copy()
        if "close" not in df.columns:
            raise ValueError("DataFrame must contain 'close' column")

        atr_series = cls.calculate_atr(df, period=14)
        ema_20_series = cls.calculate_ema(df["close"], span=20)
        ema_50_series = cls.calculate_ema(df["close"], span=50)
        sma_200_series = cls.calculate_sma(df["close"], window=200)

        latest_idx = df.index[-1]
        latest_close = float(df["close"].iloc[-1])
        latest_atr = float(atr_series.iloc[-1]) if not pd.isna(atr_series.iloc[-1]) else 0.0
        latest_atr_buffer = round(0.20 * latest_atr, 2)

        return {
            "atr_14": round(latest_atr, 2),
            "atr_buffer": latest_atr_buffer,
            "ema_20": round(float(ema_20_series.iloc[-1]), 2),
            "ema_50": round(float(ema_50_series.iloc[-1]), 2),
            "sma_200": round(float(sma_200_series.iloc[-1]), 2),
            "current_price": round(latest_close, 2)
        }
