import yfinance as yf
import pandas as pd
import numpy as np
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def fetch_clean_equity_candles(symbol: str, timeframe: str = "1W") -> List[Dict]:
    """
    Dynamically fetches split/bonus-adjusted OHLCV candles from NSE.
    Zero hardcoded price maps. Works across entire NIFTY 500 universe.
    """
    clean_sym = symbol.strip().upper().replace(".NS", "")
    ticker_sym = f"{clean_sym}.NS"

    tf_map = {
        "1D": ("2y", "1d"),
        "1W": ("3y", "1wk"),
        "1M": ("5y", "1mo"),
        "3M": ("10y", "3mo"),
        "125M": ("60d", "60m"),
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
