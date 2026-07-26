# market_schedule.py
from datetime import datetime, timezone, timedelta

# IST Timezone (+05:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now():
    return datetime.now(IST)

# Official NSE/BSE Stock Market Holidays for 2026 (Format: YYYY-MM-DD)
NSE_BSE_HOLIDAYS_2026 = {
    "2026-01-26", # Republic Day
    "2026-03-03", # Holi
    "2026-03-20", # Id-Ul-Fitr
    "2026-04-03", # Good Friday
    "2026-04-14", # Dr. Baba Saheb Ambedkar Jayanti
    "2026-05-01", # Maharashtra Day
    "2026-05-27", # Bakri Id
    "2026-08-15", # Independence Day
    "2026-10-02", # Mahatma Gandhi Jayanti
    "2026-11-09", # Diwali Laxmi Pujan
    "2026-11-10", # Diwali Balipratipada
    "2026-11-24", # Guru Nanak Jayanti
    "2026-12-25", # Christmas
}

def is_trading_day(dt=None) -> bool:
    """Checks if the given date (default today IST) is an Indian stock market trading day (Mon-Fri and not a holiday)."""
    if dt is None:
        dt = get_ist_now()
    # Monday = 0, Sunday = 6
    if dt.weekday() in (5, 6):
        return False
    date_str = dt.strftime("%Y-%m-%d")
    if date_str in NSE_BSE_HOLIDAYS_2026:
        return False
    return True

def is_market_open(dt=None) -> bool:
    """Checks if the Indian stock market is currently OPEN (9:15 AM to 3:30 PM IST on trading days)."""
    if dt is None:
        dt = get_ist_now()
    if not is_trading_day(dt):
        return False
    
    current_minutes = dt.hour * 60 + dt.minute
    open_minutes = 9 * 60 + 15    # 9:15 AM = 555 mins
    close_minutes = 15 * 60 + 30  # 3:30 PM = 930 mins
    
    return open_minutes <= current_minutes < close_minutes

def is_auto_squareoff_time(dt=None) -> bool:
    """Checks if it is 3:15 PM IST or later, triggering mandatory 3:15 PM intraday option squareoff."""
    if dt is None:
        dt = get_ist_now()
    current_minutes = dt.hour * 60 + dt.minute
    squareoff_minutes = 15 * 60 + 15 # 3:15 PM = 915 mins
    close_minutes = 15 * 60 + 30     # 3:30 PM = 930 mins
    return squareoff_minutes <= current_minutes < close_minutes

def get_market_status_text(dt=None) -> str:
    """Returns a formatted status string regarding current Indian Market status."""
    if dt is None:
        dt = get_ist_now()
    if not is_trading_day(dt):
        date_str = dt.strftime("%Y-%m-%d")
        if date_str in NSE_BSE_HOLIDAYS_2026:
            return "MARKET CLOSED (National Stock Market Holiday)"
        return "MARKET CLOSED (Weekend - Sat/Sun)"
        
    current_minutes = dt.hour * 60 + dt.minute
    open_minutes = 9 * 60 + 15
    close_minutes = 15 * 60 + 30
    
    if current_minutes < open_minutes:
        return "MARKET PRE-OPEN (Opens at 09:15 AM IST)"
    elif current_minutes >= close_minutes:
        return "MARKET CLOSED (Closed at 03:30 PM IST)"
    else:
        return "MARKET OPEN (Live Trading Hours 09:15 - 15:30 IST)"
