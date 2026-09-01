import pandas as pd
from typing import List, Dict

def build_higher_timeframes(daily_candles: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Resamples validated 1D candles into 1W (W-FRI), 1M (ME), and 3M (QE) higher timeframes.
    """
    if not daily_candles:
        return {"1D": [], "1W": [], "1M": [], "3M": []}

    df = pd.DataFrame(daily_candles)
    time_col = 'time' if 'time' in df.columns else ('candle_timestamp' if 'candle_timestamp' in df.columns else 'timestamp')
    df['datetime'] = pd.to_datetime(df[time_col], unit='s', utc=True)
    df = df.set_index('datetime').sort_index()

    aggregations = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }

    # Resample rules using standard calendar boundaries
    df_1w = df.resample('W-FRI').agg(aggregations).dropna()
    df_1m = df.resample('ME').agg(aggregations).dropna()
    df_3m = df.resample('QE').agg(aggregations).dropna()

    def serialize_resampled(resampled_df):
        out = []
        for idx, row in resampled_df.iterrows():
            out.append({
                "time": int(idx.timestamp()),
                "open": round(float(row['open']), 2),
                "high": round(float(row['high']), 2),
                "low": round(float(row['low']), 2),
                "close": round(float(row['close']), 2),
                "volume": int(row['volume'])
            })
        return out

    return {
        "1D": daily_candles,
        "1W": serialize_resampled(df_1w),
        "1M": serialize_resampled(df_1m),
        "3M": serialize_resampled(df_3m)
    }
