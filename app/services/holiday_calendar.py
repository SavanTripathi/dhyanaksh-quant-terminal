from datetime import datetime, date
from typing import Optional
import pytz

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
    now_ist = datetime.now(tz) if dt is None else dt.astimezone(tz)
    
    # Check Weekend (Saturday = 5, Sunday = 6)
    if now_ist.weekday() >= 5:
        return False
        
    # Check NSE Official Holidays
    if now_ist.date() in NSE_HOLIDAYS_2026:
        return False
        
    return True
