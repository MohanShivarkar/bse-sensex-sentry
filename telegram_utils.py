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
        f"• *Build Version:* {config.SYSTEM_VERSION}\n"
        f"• *Trend Filter:* High-Velocity Momentum Edge\n"
        f"• *Volume Fuel:* Institutional Volume Confirmed\n"
        f"• *Macro Guard:* 200 EMA Clearance Active\n\n"
        f"🛡️ *MECHANICAL RISK RULE*\n"
        f"• Candle close breaching 15 EMA = STRUCTURE BREACHED.\n"
        f"• Hard Exit. No Hesitation. No Exceptions.\n\n"
        f"🔍 Scanning SENSEX market blocks... Sentry protocols locked."
    )
    send_telegram(msg)

def send_signal_alert(asset_name, trend, price, pattern, breakout, vol_ratio, dist_sign, dist_val):
    chart_url = "https://www.tradingview.com/chart/?symbol=BSE:SENSEX"
    header = "🟢 *MOHAN'S RESEARCH: BREAKOUT ALERT* 🚀" if trend == "BULLISH" else "🔴 *MOHAN'S RESEARCH: BREAKDOWN ALERT* 📉"
    side_marker = "📈 *BULLISH RUN*" if trend == "BULLISH" else "📉 *BEARISH RUN*"
    
    msg = (f"{header}\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"🎯 *SENTRY SIGNAL ACTIVATED*\n"
           f"• *Market Asset* : `{asset_name}`\n"
           f"• *Trade Action* : {side_marker}\n"
           f"• *Entry Trigger* : `{price:.2f}`\n"
           f"• *Live Chart* : [View Live Chart]({chart_url})\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"📋 *CONFIRMED SETUP MATRICES*\n"
           f" ✅ *Signal Lock* : Age 0 Confirmation\n"
           f" ✅ *Macro Guard* : 200 EMA Dist ({dist_sign}{dist_val:.2f})\n"
           f" ✅ *Candle Profile* : {pattern} ({breakout})\n"
           f" ✅ *Volume Fuel* : {vol_ratio}x Institutional Volume\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"⚡ *Option strikes active. Fast 8-10s micro-trailing tracking active...*")
    return send_telegram(msg)

def send_trailing_update_alert(asset_name, trail_level, sl_price, current_gain):
    if trail_level == 1:
        header = "🛡️ *MOHAN'S SCALPER: BREAKEVEN LOCK SECURED*"
        desc = f"Gain reached `+{current_gain:.2f} pts`! Stop Loss moved to **Entry + 2 pts** (`{sl_price:.2f}`). Trade is 100% Risk-Free!"
    else:
        header = "🚀 *MOHAN'S SCALPER: DYNAMIC PROFIT TRAIL LEVEL 2*"
        desc = f"Gain reached `+{current_gain:.2f} pts`! Trailing SL adjusted to **`{sl_price:.2f}`** (20 pts behind peak). Profit locked!"

    msg = (f"{header}\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"📌 **Asset:** `{asset_name}`\n"
           f"💡 **Trailing Status:** {desc}\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"⚡ *Riding trend expansion... Micro-trailing active.*")
    return send_telegram(msg)

def send_exit_breakdown_alert(asset_name, result_tag, gross_pnl, fee_pnl, net_pnl, exit_price, wins, losses, total_net):
    outcome_emoji = "🟢 SUCCESS WIN" if result_tag == "WIN" else "🔴 STOP LOSS FAIL"
    
    msg = (f"🚨 *MOHAN'S SCALPER: TRADE EXIT SCORECARD* 🚨\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"🚨 **HARD EXIT: {asset_name}** 🚨\n\n"
           f"• **Trade Result:** {outcome_emoji}\n"
           f"• **Exit Price:** `{exit_price:.2f}`\n\n"
           f"📊 **DETAILED PnL BREAKDOWN:**\n"
           f"• **Gross Price Movement:** `{gross_pnl:+.2f} Pts`\n"
           f"• **Net Realized Output:** `{net_pnl:+.2f} Pts`\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"📊 **Running Scorecard Today:**\n"
           f"🏆 Wins: `{wins}` | ❌ Losses: `{losses}`\n"
           f"💰 Net Performance: `{total_net:+.2f} points`")
    return send_telegram(msg)

def send_eod_report(asset_name, date_str, wins, losses, net_points):
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100.0) if total_trades > 0 else 0.0
    
    msg = (f"📊 *MOHAN'S RESEARCH: EOD PERFORMANCE REPORT* 🏆\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"📅 *Date:* `{date_str}`\n"
           f"📌 *Asset:* `{asset_name}` (1m Scalp Engine)\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"📈 *DAILY TRADING SUMMARY*\n"
           f"• *Total Trades Executed:* `{total_trades}`\n"
           f"• *Successful Trades (Wins):* `{wins}` 🟢\n"
           f"• *Stopped Trades (Losses):* `{losses}` 🔴\n"
           f"🎯 *Win Rate:* `{win_rate:.1f}%`\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"💰 *NET PERFORMANCE*\n"
           f"🚀 *Total Net Points:* `{net_points:+.2f} Points`\n"
           f"━━━━━━━━━━━━━━━━━━━━━\n"
           f"🛡️ *Day {date_str} concluded. All positions settled.*")
    send_telegram(msg)
