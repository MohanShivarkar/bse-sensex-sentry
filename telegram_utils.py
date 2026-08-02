# telegram_utils.py
import requests
import config

TELEGRAM_API_URL = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"

def send_telegram(message_text: str) -> bool:
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("[TELEGRAM NOTICE] Bot Token or Chat ID missing. Skipping dispatch.")
        return False
        
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload, timeout=8)
        return response.status_code == 200
    except Exception as e:
        print(f"[TELEGRAM ERROR] Dispatch failed: {e}")
        return False

def send_initialization_alert(asset_name: str = "SENSEX", timeframe: str = "1m"):
    chart_url = "https://www.tradingview.com/chart/?symbol=BSE:SENSEX"
    msg = (
        f"⚡ *MOHAN'S RESEARCH: BSE SENSEX SENTRY ONLINE*\n\n"
        f"🚀 *Market Asset:* {asset_name} ({timeframe} Scalp Node)\n"
        f"📈 *Live Chart:* [BSE:SENSEX Chart]({chart_url})\n"
        f"📌 *Engine Status:* Active & Armed ({config.SYSTEM_VERSION})\n\n"

        f"🎯 *SETUP CONFINES*\n"
        f"• *Trend Filter:* High-Velocity Momentum Edge\n"
        f"• *Volume Fuel:* Institutional Volume Confirmed\n"
        f"• *Macro Guard:* 200 EMA Clearance Active\n\n"
        f"🛡️ *MECHANICAL RISK RULE*\n"
        f"• Candle close breaching 15 EMA = STRUCTURE BREACHED.\n"
        f"• Hard Exit. No Hesitation. No Exceptions.\n\n"
        f"🔍 Scanning SENSEX market blocks... Sentry protocols locked."
    )
    return send_telegram(msg)

def send_signal_alert(asset_name: str, trend: str, price: float, pattern: str, breakout: str, vol_ratio: float, dist_sign: str, dist_val: float):
    header = "🟢 *MOHAN'S RESEARCH: BREAKOUT ALERT*" if trend == "BULLISH" else "🔴 *MOHAN'S RESEARCH: BREAKDOWN ALERT*"
    emoji = "📈 *BULLISH RUN*" if trend == "BULLISH" else "📉 *BEARISH RUN*"
    chart_url = "https://www.tradingview.com/chart/?symbol=BSE:SENSEX"
    
    msg = (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *SENTRY SIGNAL ACTIVATED*\n"
        f"• *Market Asset* : `{asset_name}`\n"
        f"• *Trade Action* : {emoji}\n"
        f"• *Entry Trigger* : `₹{price:,.2f}`\n"
        f"• *Live Chart* : [View BSE:SENSEX Chart]({chart_url})\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 *STRATEGY CONFINES VERIFICATION*\n"
        f" ✅ *EMA Cross Engine* : Signal Lock (Age 0)\n"
        f" ✅ *Macro Guard* : 200 EMA Dist ({dist_sign}₹{dist_val:,.2f})\n"
        f" ✅ *Candle Profile* : {pattern} ({breakout})\n"
        f" ✅ *Volume Fuel* : {vol_ratio}x Relative Velocity\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Scalp targets initializing. Tracking SENSEX momentum blocks..."
    )
    return send_telegram(msg)

def send_milestone_alert(asset_name: str, target: float, entry: float, current: float, trend_age: int, points_moved: float):
    chart_url = "https://www.tradingview.com/chart/?symbol=BSE:SENSEX"
    msg = (
        f"🔥 *MOHAN'S SCALPER: TARGET ACHIEVEMENT*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 *SCALP MILESTONE SECURED*\n"
        f"• *Asset Target* : `{asset_name}`\n"
        f"• *Initial Entry* : `₹{entry:,.2f}`\n"
        f"• *Current Price* : `₹{current:,.2f}`\n"
        f"• *Trend Duration* : {trend_age} minutes\n"
        f"• *Live Chart* : [View BSE:SENSEX Chart]({chart_url})\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎉 *PROFIT RUN-UP PROGRESSION*\n"
        f"✅ *+{target:.0f} Points Target Achieved!*\n"
        f"🚀 *Total Expansion:* `+{points_moved:,.2f}` Points from Entry.\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Tip:* Favorable target window achieved. Lock in partials, trail stops tight to 15 EMA!"
    )
    return send_telegram(msg)

def send_eod_report(asset_name: str, date_str: str, wins: int, losses: int, net_points: float):
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0.0
    msg = (
        f"📊 *MOHAN'S SENSEX DAILY PERFORMANCE REPORT*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 *Trading Date:* `{date_str}`\n"
        f"📌 *Asset Node:* `{asset_name}`\n"
        f"🏆 *Scalp Wins:* {wins}\n"
        f"❌ *Stop-outs:* {losses}\n"
        f"📈 *Win Rate:* `{win_rate:.1f}%`\n"
        f"💰 *Net Expansion PnL:* `{net_points:+.2f}` Points\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏁 Daily market session closed. Systems resetting for next session."
    )
    return send_telegram(msg)
