# dhan_auth.py
import config

try:
    from dhanhq import dhanhq
    DHANHQ_INSTALLED = True
except ImportError:
    DHANHQ_INSTALLED = False

def get_dhan_client():
    """
    Initializes and returns the authenticated Dhan API client using dhanhq SDK.
    If Access Token is missing or invalid, returns None (triggering Fallback Feed Mode).
    """
    if config.MOCK_FEED_ENABLED or not DHANHQ_INSTALLED:
        return None
        
    try:
        dhan = dhanhq(config.DHAN_CLIENT_ID, config.DHAN_ACCESS_TOKEN)
        return dhan
    except Exception as e:
        print(f"[DHAN AUTH WARNING] Failed establishing Dhan API session: {e}")
        return None
