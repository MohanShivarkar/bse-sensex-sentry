# whatsapp_utils.py
import requests
import config

def send_whatsapp_message(message_text: str) -> bool:
    if not config.WHATSAPP_ENABLED:
        print("[WHATSAPP NOTICE] WhatsApp notifications disabled in config.")
        return False

    if not config.GREENAPI_INSTANCE_ID or not config.GREENAPI_API_TOKEN or not config.GREENAPI_GROUP_ID:
        print("[WHATSAPP NOTICE] Green-API configuration parameters missing. Skipping dispatch.")
        return False

    url = f"{config.GREENAPI_HOST}/waInstance{config.GREENAPI_INSTANCE_ID}/sendMessage/{config.GREENAPI_API_TOKEN}"
    
    payload = {
        "chatId": config.GREENAPI_GROUP_ID,
        "message": message_text
    }

    try:
        response = requests.post(url, json=payload, timeout=8)
        if response.status_code == 200:
            return True
        else:
            print(f"[WHATSAPP ERROR] Dispatch failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[WHATSAPP ERROR] Exception during dispatch: {e}")
        return False

def send_initialization_alert(asset_name: str = "SENSEX", timeframe: str = "1m"):
    chart_url = "https://www.tradingview.com/chart/?symbol=BSE:SENSEX"
    msg = (
        f"⚡ *MOHAN'S RESEARCH: BSE SENSEX SENTRY ONLINE*\n\n"
        f"🚀 *Asset:* {asset_name} ({timeframe} Scalp)\n"
        f"📈 *Live Chart:* {chart_url}\n"
        f"📌 *Engine Status:* Active & Armed ({config.SYSTEM_VERSION})\n\n"
        f"🎯 *SETUP CONFINES*\n"
        f"* Build Version: {config.SYSTEM_VERSION}\n"
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
        f"{header}\n\n"
        f"📌 *Market Asset:* {asset_name}\n"
        f"📊 *Trade Action:* {emoji}\n"
        f"💰 *Entry Trigger:* {price:.2f}\n"
        f"📈 *Live Chart:* {chart_url}\n\n"
        f"📋 *CONFIRMED SETUP MATRICES*\n"
        f"* Signal Lock: Age 0 Confirmation\n"
        f"* Macro Guard: Trend Clearance Verified\n"
        f"* Candle Profile: {pattern} ({breakout})\n"
        f"* Volume Fuel: {vol_ratio}x Institutional Volume\n\n"
        f"⚡ Option strikes active. Fast 8-10s micro-trailing tracking active..."
    )
    return send_whatsapp_message(msg)

def send_trailing_update_alert(asset_name, trail_level, sl_price, current_gain):
    if trail_level == 1:
        header = "🛡️ *MOHAN'S SCALPER: BREAKEVEN LOCK SECURED*"
        desc = f"Gain reached +{current_gain:.2f} pts! Stop Loss moved to Entry + 2 pts ({sl_price:.2f}). Trade is 100% Risk-Free!"
    else:
        header = "🚀 *MOHAN'S SCALPER: DYNAMIC PROFIT TRAIL LEVEL 2*"
        desc = f"Gain reached +{current_gain:.2f} pts! Trailing SL adjusted to {sl_price:.2f} (20 pts behind peak). Profit locked!"

    msg = (
        f"{header}\n\n"
        f"📌 *Asset:* {asset_name}\n"
        f"💡 *Trailing Status:* {desc}\n\n"
        f"⚡ Riding trend expansion... Micro-trailing active."
    )
    return send_whatsapp_message(msg)

def send_exit_breakdown_alert(asset_name, result_tag, gross_pnl, fee_pnl, net_pnl, exit_price, wins, losses, total_net):
    outcome_emoji = "🟢 SUCCESS WIN" if result_tag == "WIN" else "🔴 STOP LOSS FAIL"
    
    msg = (
        f"🚨 *MOHAN'S SCALPER: TRADE EXIT SCORECARD* 🚨\n\n"
        f"🚨 *HARD EXIT: {asset_name}* 🚨\n\n"
        f"* Trade Result: {outcome_emoji}\n"
        f"* Exit Price: {exit_price:.2f}\n\n"
        f"📊 *DETAILED PnL BREAKDOWN:*\n"
        f"* Gross Price Movement: {gross_pnl:+.2f} Pts\n"
        f"* Net Realized Output: {net_pnl:+.2f} Pts\n\n"
        f"📊 *Running Scorecard Today:*\n"
        f"🏆 Wins: {wins} | ❌ Losses: {losses}\n"
        f"💰 Net Performance: {total_net:+.2f} points"
    )
    return send_whatsapp_message(msg)

def send_hard_exit_alert(exit_msg_text: str):
    return send_whatsapp_message(exit_msg_text)

def send_eod_report(asset_name: str, date_str: str, wins: int, losses: int, net_points: float):
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100.0) if total_trades > 0 else 0.0
    
    msg = (
        f"📊 *MOHAN'S RESEARCH: EOD PERFORMANCE REPORT* 🏆\n\n"
        f"📅 *Date:* {date_str}\n"
        f"📌 *Asset:* {asset_name} (1m Scalp Engine)\n\n"
        f"📈 *DAILY TRADING SUMMARY*\n"
        f"* Total Trades Executed: {total_trades}\n"
        f"* Successful Trades (Wins): {wins} 🟢\n"
        f"* Stopped Trades (Losses): {losses} 🔴\n"
        f"🎯 *Win Rate:* {win_rate:.1f}%\n\n"
        f"💰 *NET PERFORMANCE*\n"
        f"🚀 *Total Net Points:* {net_points:+.2f} Points\n\n"
        f"🛡️ Day {date_str} concluded. All positions settled."
    )
    return send_whatsapp_message(msg)
