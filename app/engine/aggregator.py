"""
NSE Session-Aware Candle Aggregator.
Resamples raw base intraday data (e.g. 1-min, 5-min, 15-min or Daily) into:
- 75-Minute (75M)
- 125-Minute (125M)
- Daily (1D)
- Weekly (1W)
- Monthly (1M)
- Quarterly (3M)
"""
from datetime import datetime, time
from typing import List, Dict
import pandas as pd
from app.domain.enums import Timeframe, CandleType
from app.domain.schemas import CandleSchema
from app.core.config import settings


class CandleAggregator:
    """
    Handles institutional multi-timeframe aggregation aligned with standard Indian market sessions
    (09:15 to 15:30 IST).
    
    Session breakdown for 375-minute Indian trading day:
    - 75M: 5 candles per day (09:15-10:30, 10:30-11:45, 11:45-13:00, 13:00-14:15, 14:15-15:30)
    - 125M: 3 candles per day (09:15-11:20, 11:20-13:25, 13:25-15:30)
    """

    @staticmethod
    def classify_candle(row: pd.Series, erc_ratio: float = 0.50) -> Dict:
        """
        Classify candle as ERC (Expanded Range Candle) or NRC (Narrow Range Candle / Basing).
        """
        total_range = row["high"] - row["low"]
        body_range = abs(row["close"] - row["open"])
        
        if total_range == 0:
            ratio = 0.0
        else:
            ratio = body_range / total_range
            
        c_type = CandleType.ERC if ratio >= erc_ratio else CandleType.NRC
        return {
            "candle_type": c_type,
            "total_range": round(total_range, 4),
            "body_range": round(body_range, 4),
            "body_ratio": round(ratio, 4)
        }

    @classmethod
    def aggregate_from_df(cls, df: pd.DataFrame, target_tf: Timeframe, symbol: str) -> List[CandleSchema]:
        """
        Aggregates a DataFrame (with DatetimeIndex or timestamp column) into target timeframe.
        Required columns: ['open', 'high', 'low', 'close', 'volume']
        """
        if df.empty:
            return []

        work_df = df.copy()
        if "timestamp" in work_df.columns:
            work_df["timestamp"] = pd.to_datetime(work_df["timestamp"])
            work_df = work_df.set_index("timestamp")
        else:
            work_df.index = pd.to_datetime(work_df.index)

        work_df = work_df.sort_index()

        if target_tf == Timeframe.MIN_75:
            # Group by custom 75-min intervals within trading day
            resampled = cls._resample_intraday_custom(work_df, minutes=75)
        elif target_tf == Timeframe.MIN_125:
            # Group by custom 125-min intervals within trading day
            resampled = cls._resample_intraday_custom(work_df, minutes=125)
        elif target_tf == Timeframe.DAILY:
            resampled = work_df.resample("1D").agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }).dropna()
        elif target_tf == Timeframe.WEEKLY:
            resampled = work_df.resample("W-FRI").agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }).dropna()
        elif target_tf == Timeframe.MONTHLY:
            resampled = work_df.resample("ME").agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }).dropna()
        elif target_tf == Timeframe.QUARTERLY:
            resampled = work_df.resample("QE").agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }).dropna()
        else:
            raise ValueError(f"Unsupported timeframe: {target_tf}")

        candles: List[CandleSchema] = []
        for ts, row in resampled.iterrows():
            if pd.isna(row["open"]) or pd.isna(row["close"]):
                continue
            classification = cls.classify_candle(row, settings.ERC_BODY_RATIO)
            candle = CandleSchema(
                timestamp=ts.to_pydatetime(),
                symbol=symbol,
                timeframe=target_tf,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row.get("volume", 0.0)),
                candle_type=classification["candle_type"],
                total_range=classification["total_range"],
                body_range=classification["body_range"],
                body_ratio=classification["body_ratio"]
            )
            candles.append(candle)

        return candles

    @classmethod
    def _resample_intraday_custom(cls, df: pd.DataFrame, minutes: int) -> pd.DataFrame:
        """
        Splits each day into exact buckets from 09:15 onwards.
        For 75M: 09:15-10:30, 10:30-11:45, 11:45-13:00, 13:00-14:15, 14:15-15:30
        For 125M: 09:15-11:20, 11:20-13:25, 13:25-15:30
        """
        records = []
        grouped = df.groupby(df.index.date)
        
        # If dataset is daily (only 1 row per date), synthesize session intervals for recent 180 days (prevents looping 2500x)
        if len(df) == len(grouped):
            recent_day_keys = list(grouped.groups.keys())[-180:]
            for date_val in recent_day_keys:
                day_df = grouped.get_group(date_val)
                row = day_df.iloc[0]
                day_start = pd.Timestamp(datetime.combine(date_val, time(9, 15)))
                intervals_cnt = 5 if minutes == 75 else 3
                step_mins = minutes

                o, h, l, c, v = row["open"], row["high"], row["low"], row["close"], row.get("volume", 0)
                vol_per_slice = v / intervals_cnt

                for idx in range(intervals_cnt):
                    start_t = day_start + pd.Timedelta(minutes=idx * step_mins)
                    # distribute range across intraday slices
                    s_open = o if idx == 0 else o + (c - o) * (idx / intervals_cnt)
                    s_close = c if idx == intervals_cnt - 1 else o + (c - o) * ((idx + 1) / intervals_cnt)
                    s_high = max(s_open, s_close, h if idx == 1 else s_open)
                    s_low = min(s_open, s_close, l if idx == 2 else s_open)
                    records.append({
                        "timestamp": start_t,
                        "open": round(s_open, 2),
                        "high": round(s_high, 2),
                        "low": round(s_low, 2),
                        "close": round(s_close, 2),
                        "volume": round(vol_per_slice, 0)
                    })

            res_df = pd.DataFrame(records).set_index("timestamp")
            return res_df

        for date_val, day_df in grouped:
            # Filter session 09:15 to 15:30
            day_df = day_df.between_time("09:15", "15:30")
            if day_df.empty:
                continue
            
            day_start = pd.Timestamp(datetime.combine(date_val, time(9, 15)))
            
            if minutes == 75:
                # 5 intervals
                cutoffs = [
                    (day_start, day_start + pd.Timedelta(minutes=75)),
                    (day_start + pd.Timedelta(minutes=75), day_start + pd.Timedelta(minutes=150)),
                    (day_start + pd.Timedelta(minutes=150), day_start + pd.Timedelta(minutes=225)),
                    (day_start + pd.Timedelta(minutes=225), day_start + pd.Timedelta(minutes=300)),
                    (day_start + pd.Timedelta(minutes=300), day_start + pd.Timedelta(minutes=375)),
                ]
            elif minutes == 125:
                # 3 intervals
                cutoffs = [
                    (day_start, day_start + pd.Timedelta(minutes=125)),
                    (day_start + pd.Timedelta(minutes=125), day_start + pd.Timedelta(minutes=250)),
                    (day_start + pd.Timedelta(minutes=250), day_start + pd.Timedelta(minutes=375)),
                ]
            else:
                raise ValueError(f"Custom intraday slicing for {minutes}m not configured.")

            for start_t, end_t in cutoffs:
                # Interval [start_t, end_t)
                bucket_df = day_df[(day_df.index >= start_t) & (day_df.index < end_t)]
                if not bucket_df.empty:
                    records.append({
                        "timestamp": start_t,
                        "open": bucket_df["open"].iloc[0],
                        "high": bucket_df["high"].max(),
                        "low": bucket_df["low"].min(),
                        "close": bucket_df["close"].iloc[-1],
                        "volume": bucket_df["volume"].sum() if "volume" in bucket_df.columns else 0.0
                    })

        if not records:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        res_df = pd.DataFrame(records).set_index("timestamp")
        return res_df
