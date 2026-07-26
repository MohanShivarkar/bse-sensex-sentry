# =======================================================================================
# SENSEX SENTRY BOT: INDIAN MARKET CONFIGURATION LAYER
# =======================================================================================
import os

# Dhan API Credentials (Get access token from https://dhanhq.co)
DHAN_CLIENT_ID = os.environ.get("DHAN_CLIENT_ID", "YOUR_DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.environ.get("DHAN_ACCESS_TOKEN", "YOUR_DHAN_ACCESS_TOKEN")

# Execution Mode Toggles
# Phase 1: Signal Monitoring & Multi-Channel Alerts (ACTIVE)
# Phase 2: Automated Dhan Options Trading (Set AUTO_TRADE_ENABLED = True when ready)
AUTO_TRADE_ENABLED = False 

# If Dhan Access Token is not provided, enable Fallback Feed Mode automatically
MOCK_FEED_ENABLED = (DHAN_ACCESS_TOKEN == "YOUR_DHAN_ACCESS_TOKEN" or not DHAN_ACCESS_TOKEN)

# Telegram Gateway Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8829418844:AAGU1BD2ASTdw4KTdYhbeyi94JJX5ImxjxE")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5447820186")

# Green-API WhatsApp Gateway Configuration
WHATSAPP_ENABLED = True
GREENAPI_HOST = os.environ.get("GREENAPI_HOST", "https://7107.api.greenapi.com")
GREENAPI_INSTANCE_ID = os.environ.get("GREENAPI_INSTANCE_ID", "710722692952")
GREENAPI_API_TOKEN = os.environ.get("GREENAPI_API_TOKEN", "6f68c32589c64b72ae2d460755cc454339484bc650f241c7bb")
GREENAPI_GROUP_ID = os.environ.get("GREENAPI_GROUP_ID", "120363409565136267@g.us")

# Indian Market Assets Definition
ASSETS = {
    "SENSEX": {
        "symbol": "BSE:SENSEX",
        "dhan_security_id": "51", # SENSEX Index Security ID on Dhan
        "timeframe": "1m",
        "description": "BSE Sensex Benchmark Momentum Node"
    }
}
