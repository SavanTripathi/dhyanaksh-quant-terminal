from datetime import datetime, date, timedelta, time
from typing import Optional
import pytz

IST = pytz.timezone("Asia/Kolkata")
MARKET_SETTLEMENT_TIME = time(16, 0)

NSE_HOLIDAYS_2026 = {
    date(2026, 1, 26),  # Republic Day
    date(2026, 3, 10),  # Maha Shivratri
    date(2026, 3, 25),  # Holi
    date(2026, 4, 2),   # Good Friday
    date(2026, 4, 14),  # Dr. Ambedkar Jayanti
    date(2026, 5, 1),   # Maharashtra Day
    date(2026, 8, 15),  # Independence Day
    date(2026, 10, 2),  # Mahatma Gandhi Jayanti
    date(2026, 10, 20), # Dussehra
    date(2026, 11, 10), # Diwali
    date(2026, 12, 25), # Christmas
}

def is_trading_day(dt: Optional[datetime] = None) -> bool:
    tz = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(tz) if dt is None else (dt if dt.tzinfo else tz.localize(dt)).astimezone(tz)
    
    # Check Weekend (Saturday = 5, Sunday = 6)
    if now_ist.weekday() >= 5:
        return False
        
    # Check NSE Official Holidays
    if now_ist.date() in NSE_HOLIDAYS_2026:
        return False
        
    return True

def get_last_completed_trading_day(ref_dt: Optional[datetime] = None) -> date:
    """
    Returns the date of the most recent finalized NSE trading day.
    - If called after 16:00 IST on a trading day (Mon-Fri, non-holiday), today's EOD is completed.
    - If called before 16:00 IST on a trading day, or on a weekend/holiday, steps back day-by-day
      until the latest completed trading session is reached.
    """
    if ref_dt is None:
        now_ist = datetime.now(IST)
    elif ref_dt.tzinfo is None:
        now_ist = IST.localize(ref_dt)
    else:
        now_ist = ref_dt.astimezone(IST)
        
    candidate_dt = now_ist
    # If today is a trading day but market has not finalized EOD close (before 16:00 IST),
    # today's candle is still in progress / incomplete.
    if candidate_dt.time() < MARKET_SETTLEMENT_TIME:
        candidate_dt = candidate_dt - timedelta(days=1)
        
    while True:
        if candidate_dt.weekday() < 5 and candidate_dt.date() not in NSE_HOLIDAYS_2026:
            return candidate_dt.date()
        candidate_dt = candidate_dt - timedelta(days=1)

