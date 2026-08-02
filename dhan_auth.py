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
    Supports either Access Token or API Key + Secret authentication.
    If credentials are not provided or invalid, returns None (triggering Fallback Feed Mode).
    """
    if not DHANHQ_INSTALLED:
        return None
        
    try:
        if config.DHAN_ACCESS_TOKEN and config.DHAN_ACCESS_TOKEN != "YOUR_DHAN_ACCESS_TOKEN":
            dhan = dhanhq(config.DHAN_CLIENT_ID, config.DHAN_ACCESS_TOKEN)
            return dhan
        elif config.DHAN_API_KEY and config.DHAN_API_SECRET:
            # DhanHQ client initialized with Client ID & API Key / Secret token
            dhan = dhanhq(config.DHAN_CLIENT_ID, config.DHAN_API_KEY)
            return dhan
    except Exception as e:
        print(f"[DHAN AUTH WARNING] Failed establishing Dhan API session: {e}")
        return None

    return None
