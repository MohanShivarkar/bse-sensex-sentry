# whatsapp_utils.py
import requests
import config

def send_whatsapp_message(message_text: str) -> bool:
    if not config.WHATSAPP_ENABLED:
        return False
        
    url = f"{config.GREENAPI_HOST}/waInstance{config.GREENAPI_INSTANCE_ID}/sendMessage/{config.GREENAPI_API_TOKEN}"
    payload = {
        "chatId": config.GREENAPI_GROUP_ID,
        "message": message_text
    }
    
    try:
        response = requests.post(url, json=payload, timeout=8)
        return response.status_code == 200
    except Exception as e:
        print(f"[WHATSAPP ERROR] Dispatch failed: {e}")
        return False

def send_initialization_alert(asset_name: str = "SENSEX", timeframe: str = "1m"):
    chart_url = "https://www.tradingview.com/chart/?symbol=BSE:SENSEX"
    msg = (
        f"⚡ *MOHAN'S RESEARCH: BSE SENSEX SENTRY ONLINE*\n\n"
        f"🚀 *Asset:* {asset_name} ({timeframe} Scalp)\n"
        f"📈 *Live Chart:* {chart_url}\n"
        f"📌 *Engine Status:* Active & Armed (Indian Market Hours)\n\n"
        f"🎯 *SETUP CONFINES*\n"
        f"* Trend Filter: High-Velocity Momentum Edge\n"
        f"* Volume Fuel: Institutional Volume Confirmed\n"
        f"* Macro Guard: Trend Clearance Active\n\n"
        f"🛡️ *MECHANICAL RISK RULE*\n"
        f"* Any candle close breaching structural anchor = STRUCTURE BREACHED.\n"
        f"* Hard Exit. No Hesitation. No Exceptions.\n\n"
        f"🔍 Scanning live market blocks... Sentry protocols locked."
    )
    return send_whatsapp_message(msg)

def send_signal_alert(asset_name: str, trend: str, price: float, pattern: str, breakout: str, vol_ratio: float, dist_sign: str, dist_val: float):
    header = "🟢 *MOHAN'S RESEARCH: BREAKOUT ALERT* 🚀" if trend == "BULLISH" else "🔴 *MOHAN'S RESEARCH: BREAKDOWN ALERT* 📉"
    emoji = "📈 BULLISH RUN" if trend == "BULLISH" else "📉 BEARISH RUN"
    chart_url = "https://www.tradingview.com/chart/?symbol=BSE:SENSEX"
    
    msg = (
        f"{header}\n"
        f"───────────────────\n"
        f"🎯 *SENTRY SIGNAL ACTIVATED*\n"
        f"📌 *Asset:* {asset_name}\n"
        f"📊 *Trade Action:* {emoji}\n"
        f"💰 *Entry Trigger:* ₹{price:,.2f}\n"
        f"📈 *Live Chart:* {chart_url}\n"
        f"───────────────────\n"
        f"📋 *STRATEGY CONFIRMATIONS*\n"
        f"✅ *EMA Cross:* Signal Lock (Age 0)\n"
        f"✅ *Macro Guard:* 200 EMA ({dist_sign}₹{dist_val:,.2f})\n"
        f"✅ *Candle:* {pattern} ({breakout})\n"
        f"✅ *Volume Fuel:* {vol_ratio}x Relative Velocity\n"
        f"───────────────────\n"
        f"⚡ Scalp targets initializing... Tracking momentum!"
    )
    return send_whatsapp_message(msg)

def send_milestone_alert(asset_name: str, target: float, entry: float, current: float, trend_age: int, points_moved: float):
    chart_url = "https://www.tradingview.com/chart/?symbol=BSE:SENSEX"
    msg = (
        f"🎯 *MOHAN'S SCALPER: TARGET SECURED*\n"
        f"───────────────────\n"
        f"💰 *SCALP MILESTONE ACHIEVED*\n"
        f"📌 *Asset:* {asset_name}\n"
        f"💵 *Initial Entry:* ₹{entry:,.2f}\n"
        f"📈 *Current Price:* ₹{current:,.2f}\n"
        f"⏱️ *Trend Duration:* {trend_age} mins\n"
        f"📈 *Live Chart:* {chart_url}\n"
        f"───────────────────\n"
        f"🎉 *PROFIT RUN-UP*\n"
        f"✅ *+{target:.0f} Points Target Achieved!*\n"
        f"🚀 *Total Expansion:* +{points_moved:,.2f} Points\n"
        f"───────────────────\n"
        f"💡 Lock in partials & trail stops tight to 15 EMA!"
    )
    return send_whatsapp_message(msg)

def send_hard_exit_alert(msg_text: str):
    return send_whatsapp_message(msg_text)

def send_eod_report(asset_name: str, date_str: str, wins: int, losses: int, net_points: float):
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0.0
    msg = (
        f"📊 *MOHAN'S SENSEX DAILY PERFORMANCE REPORT*\n"
        f"───────────────────\n"
        f"📅 *Date:* {date_str}\n"
        f"📌 *Asset:* {asset_name}\n"
        f"🏆 *Wins:* {wins} | ❌ *Losses:* {losses}\n"
        f"📈 *Win Rate:* {win_rate:.1f}%\n"
        f"💰 *Net Expansion PnL:* {net_points:+.2f} Points\n"
        f"───────────────────\n"
        f"🏁 Daily market session closed."
    )
    return send_whatsapp_message(msg)
