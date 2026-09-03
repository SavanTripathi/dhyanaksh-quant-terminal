import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime, time
from typing import List, Dict

logger = logging.getLogger(__name__)

def fetch_clean_equity_candles(
    symbol: str, 
    timeframe: str = "1W", 
    analysis_mode: str = "EOD", 
    as_of_date: str = "2026-09-02"
) -> List[Dict]:
    """
    Dynamically fetches split/bonus-adjusted OHLCV candles from NSE.
    Exact session slicing:
      - 75M: 5 exact session buckets per day (09:15-10:30, 10:30-11:45, 11:45-13:00, 13:00-14:15, 14:15-15:30) resampled from 15m bars.
      - 125M: 3 exact session buckets per day (09:15-11:20, 11:20-13:25, 13:25-15:30) resampled from 5m granular bars.
      - 1D, 1W, 1M, 3M: Clean historical daily/higher timeframe bars.
    Mode-aware:
      - In EOD mode, enforces strict cutoff <= as_of_date 23:59:59 IST across all timeframes.
      - In LIVE mode, supplies latest available intraday and current session candles.
    Zero hardcoded price maps. Works across entire NIFTY 500 universe.
    """
    clean_sym = symbol.strip().upper().replace(".NS", "")
    ticker_sym = f"{clean_sym}.NS"

    tf_map = {
        "1D": ("2y", "1d"),
        "1W": ("3y", "1wk"),
        "1M": ("5y", "1mo"),
        "3M": ("10y", "3mo"),
        "125M": ("60d", "5m"),
        "75M": ("60d", "15m")
    }
    period, interval = tf_map.get(timeframe, ("3y", "1wk"))

    try:
        ticker = yf.Ticker(ticker_sym)
        # auto_adjust=True guarantees proper split/demerger/bonus price scaling
        df = ticker.history(period=period, interval=interval, auto_adjust=True, timeout=10)

        if df is None or df.empty or len(df) < 5:
            logger.warning(f"No price history returned for {ticker_sym}")
            return []

        df = df.dropna()

        # Sanity check: eliminate bad single-bar anomaly spikes
        df['prev_close'] = df['Close'].shift(1)
        valid_mask = (df['prev_close'].isna()) | (
            (df['Close'] / df['prev_close'] < 2.5) & (df['Close'] / df['prev_close'] > 0.4)
        )
        df = df[valid_mask].drop(columns=['prev_close'])

        # Enforce strict EOD snapshot boundary across all timeframes (1D, 75M, 125M, 1W, etc.)
        if analysis_mode.upper() == "EOD" and as_of_date:
            cutoff_dt = pd.to_datetime(f"{as_of_date} 23:59:59+05:30")
            if df.index.tz is None:
                df.index = df.index.tz_localize("Asia/Kolkata")
            df = df[df.index <= cutoff_dt]

        # Exact Session Slicing for 75M and 125M
        if timeframe in ("75M", "125M"):
            if df.index.tz is None:
                df.index = df.index.tz_localize("Asia/Kolkata")
            
            resampled_records = []
            grouped_by_day = df.groupby(df.index.date)
            for date_val, day_df in grouped_by_day:
                day_start = pd.Timestamp(datetime.combine(date_val, time(9, 15))).tz_localize("Asia/Kolkata")
                
                if timeframe == "75M":
                    cutoffs = [
                        (day_start, day_start + pd.Timedelta(minutes=75)),
                        (day_start + pd.Timedelta(minutes=75), day_start + pd.Timedelta(minutes=150)),
                        (day_start + pd.Timedelta(minutes=150), day_start + pd.Timedelta(minutes=225)),
                        (day_start + pd.Timedelta(minutes=225), day_start + pd.Timedelta(minutes=300)),
                        (day_start + pd.Timedelta(minutes=300), day_start + pd.Timedelta(minutes=375)),
                    ]
                else:  # 125M
                    cutoffs = [
                        (day_start, day_start + pd.Timedelta(minutes=125)),
                        (day_start + pd.Timedelta(minutes=125), day_start + pd.Timedelta(minutes=250)),
                        (day_start + pd.Timedelta(minutes=250), day_start + pd.Timedelta(minutes=375)),
                    ]

                for st, et in cutoffs:
                    bucket = day_df[(day_df.index >= st) & (day_df.index < et)]
                    if not bucket.empty:
                        ts = int(st.timestamp())
                        resampled_records.append({
                            "time": ts,
                            "open": round(float(bucket.iloc[0]["Open"]), 2),
                            "high": round(float(bucket["High"].max()), 2),
                            "low": round(float(bucket["Low"].min()), 2),
                            "close": round(float(bucket.iloc[-1]["Close"]), 2),
                            "volume": int(bucket["Volume"].sum()) if "Volume" in bucket else 0
                        })
            return resampled_records

        candles = []
        for idx, row in df.iterrows():
            ts = int(idx.timestamp()) if hasattr(idx, 'timestamp') else int(pd.to_datetime(idx).timestamp())
            candles.append({
                "time": ts,
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume']) if 'Volume' in row else 0
            })
        return candles

    except Exception as e:
        logger.error(f"Failed to fetch market data for {ticker_sym}: {e}")
        return []


def get_canonical_weekly_candles(df_daily: pd.DataFrame) -> List[Dict]:
    """
    Aggregates standard daily candles into clean Monday-Friday weekly bars matching TradingView.
    """
    df = df_daily.copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df['time'], unit='s', utc=True)
    
    weekly = df.resample('W-FRI').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

    candles = []
    for idx, row in weekly.iterrows():
        candles.append({
            "time": int(idx.timestamp()),
            "open": round(float(row['open']), 2),
            "high": round(float(row['high']), 2),
            "low": round(float(row['low']), 2),
            "close": round(float(row['close']), 2),
            "volume": int(row['volume'])
        })
    return candles
