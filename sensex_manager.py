# sensex_manager.py
import threading
import time
import os
import json
import random
import requests
from datetime import datetime, timezone, timedelta

import config
import market_schedule
import sensex_core_logic

import telegram_utils
import whatsapp_utils
import dhan_auth
import dhan_order_router

IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now():
    return datetime.now(IST)

def get_logs_dir(asset_name: str) -> str:
    custom_path = os.environ.get("PERSISTENT_LOG_DIR") or os.environ.get("RENDER_DISK_PATH")
    if custom_path:
        base = os.path.join(custom_path, "logs", asset_name)
    else:
        base = os.path.join("logs", asset_name)
    os.makedirs(base, exist_ok=True)
    return base

def load_todays_metrics(asset_name: str) -> dict:
    today_str = get_ist_now().strftime("%Y-%m-%d")
    log_dir = get_logs_dir(asset_name)
    file_path = os.path.join(log_dir, f"metrics_{today_str}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"date": today_str, "wins": 0, "losses": 0, "net_points": 0.0}

def save_todays_metrics(asset_name: str, metrics: dict):
    try:
        log_dir = get_logs_dir(asset_name)
        date_str = metrics.get("date") or get_ist_now().strftime("%Y-%m-%d")
        file_path = os.path.join(log_dir, f"metrics_{date_str}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
    except Exception as e:
        print(f"[{asset_name}] Metrics save error: {e}")

# Global tracking state dictionary initialization
asset_states = {
    name: {
        "current_trend": "NEUTRAL",
        "trend_age": 0,
        "metrics": load_todays_metrics(name),
        "active_trade": {
            "direction": None,
            "entry_price": 0.0,
            "max_expansion": 0.0,
            "targets_achieved": []
        }
    } for name in config.ASSETS
}

# Direct in-memory RAM log buffer for 100% reliable cloud streaming
latest_logs = {name: "" for name in config.ASSETS}

# Simulated benchmark price baseline for Sensex (around 80,450)
_simulated_base_price = 80450.0

def fetch_sensex_candles(symbol: str, timeframe: str) -> list:
    """
    Fetches 250 1-minute OHLCV candles for BSE Sensex.
    - Uses Dhan API if DHAN_ACCESS_TOKEN is configured.
    - Uses public Yahoo Finance (^BSESN) or high-precision simulation if token is missing.
    """
    global _simulated_base_price
    
    # Provider 1: Dhan API Live Feed (If Access Token Configured)
    if not config.MOCK_FEED_ENABLED:
        try:
            dhan = dhan_auth.get_dhan_client()
            if dhan:
                # Dhan API Historical/Intraday Candles call
                res = dhan.historical_daily_data(
                    symbol=config.ASSETS["SENSEX"]["dhan_security_id"],
                    exchange_segment="BSE_INDEX",
                    instrument_type="INDEX"
                )
                if res and res.get("status") == "success" and len(res.get("data", [])) >= 201:
                    candles = res["data"]
                    return [[int(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])] for c in candles[-250:]]
        except Exception as e:
            print(f"[DHAN FEED NOTICE] Falling back to public feed: {e}")

    # Provider 2: Public Yahoo Finance API (^BSESN - BSE Sensex)
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EBSESN?interval=1m&range=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=6)
        if res.status_code == 200:
            json_data = res.json()
            result = json_data.get("chart", {}).get("result", [])[0]
            timestamps = result.get("timestamp", [])
            indicators = result.get("indicators", {}).get("quote", [])[0]
            opens = indicators.get("open", [])
            highs = indicators.get("high", [])
            lows = indicators.get("low", [])
            closes = indicators.get("close", [])
            volumes = indicators.get("volume", [])

            formatted = []
            for i in range(len(timestamps)):
                if closes[i] is not None:
                    formatted.append([
                        timestamps[i] * 1000,
                        float(opens[i] or closes[i]),
                        float(highs[i] or closes[i]),
                        float(lows[i] or closes[i]),
                        float(closes[i]),
                        float(volumes[i] or 100)
                    ])
            if len(formatted) >= 201:
                return formatted[-250:]
    except Exception as e:
        print(f"[YAHOO FEED NOTICE] Market feed notice: {e}")

    # Provider 3: Realistic SENSEX Market Candle Simulation (For off-market hours & testing)
    candles = []
    curr_t = int(time.time()) - (250 * 60)
    p = _simulated_base_price
    
    for i in range(250):
        t_stamp = (curr_t + (i * 60)) * 1000
        change = random.uniform(-15.0, 15.5)
        p = max(70000.0, p + change)
        high = p + random.uniform(2.0, 12.0)
        low = p - random.uniform(2.0, 12.0)
        open_p = p - random.uniform(-5.0, 5.0)
        vol = random.uniform(150.0, 1200.0)
        candles.append([t_stamp, open_p, high, low, p, vol])

    _simulated_base_price = p
    return candles

def format_terminal_log(label: str, content: str) -> str:
    timestamp = get_ist_now().strftime("[%Y-%m-%d %H:%M:%S]")
    padded_label = label.ljust(17)
    return f"{timestamp} {padded_label}: {content}"

def write_to_daily_file(asset_name: str, log_text: str):
    try:
        log_dir = get_logs_dir(asset_name)
        date_str = get_ist_now().strftime("%Y-%m-%d")
        file_path = os.path.join(log_dir, f"sentry_log_{date_str}.txt")
        
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(log_text + "\n")
    except Exception as e:
        print(format_terminal_log("LOGGING ERROR", f"[{asset_name}] Failed writing telemetry to disk: {str(e)}"))

def should_send_init_alert(asset_name: str) -> bool:
    try:
        log_dir = get_logs_dir(asset_name)
        lock_file = os.path.join(log_dir, "startup.lock")
        now = time.time()
        if os.path.exists(lock_file):
            with open(lock_file, "r", encoding="utf-8") as f:
                prev_time = float(f.read().strip() or "0")
                if (now - prev_time) < 300:
                    return False
        with open(lock_file, "w", encoding="utf-8") as f:
            f.write(str(now))
        return True
    except Exception:
        return True

def is_duplicate_signal(asset_name: str, signal: dict) -> bool:
    if not signal:
        return False
        
    sig_type = signal.get("type", "")
    sig_price = round(float(signal.get("price", 0.0)), 2)
    sig_key = f"{sig_type}_{sig_price}"
    now = time.time()
    
    try:
        log_dir = get_logs_dir(asset_name)
        lock_file = os.path.join(log_dir, "last_signal.json")
        
        if os.path.exists(lock_file):
            with open(lock_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                prev_key = data.get("key")
                prev_time = data.get("time", 0)
                if prev_key == sig_key and (now - prev_time) < 120:
                    return True
                    
        with open(lock_file, "w", encoding="utf-8") as f:
            json.dump({"key": sig_key, "time": now}, f)
            
    except Exception as e:
        print(f"[{asset_name}] Signal lock file notice: {e}")
        
    return False

def run_asset_production_loop(name, details):
    global asset_states
    if should_send_init_alert(name):
        try:
            telegram_utils.send_initialization_alert(name, details['timeframe'])
        except Exception as e:
            print(f"[{name}] Telegram alert warning: {e}")

        try:
            whatsapp_utils.send_initialization_alert(name, details['timeframe'])
        except Exception as e:
            print(f"[{name}] WhatsApp alert warning: {e}")

    first_run = True
    while True:
        try:
            if not first_run:
                now = time.time()
                time_to_next_candle = 60 - (now % 60)
                time.sleep(time_to_next_candle + 1.5)
            first_run = False
            
            # Check Indian Market Hours Status
            is_open = market_schedule.is_market_open()
            status_text = market_schedule.get_market_status_text()

            # Optional: Automatic Intraday 3:15 PM Squareoff Trigger
            if market_schedule.is_auto_squareoff_time():
                dhan_order_router.auto_squareoff_all_positions()

            ohlcv = fetch_sensex_candles(details['symbol'], details['timeframe'])
            if len(ohlcv) < 201:
                notice_log = f"""-----------------------------------------------------------------------------------------
{format_terminal_log('GLOBAL MARKET SCAN', f"{name} ({details['symbol']}) {details['timeframe']}")}
{format_terminal_log(name, f"Connecting to BSE Sensex market data feed... (Got {len(ohlcv)} candles)")}
{format_terminal_log('Strategy Core', f"{asset_states[name]['current_trend']} | Age {asset_states[name]['trend_age']}m | Retrying Feed")}
{format_terminal_log('Setup Checklist', 'Cross: ❌ | 200EMA: ❌ | Candle: ❌ | Volume Fuel: ❌')}
{format_terminal_log('System Action', status_text)}
-----------------------------------------------------------------------------------------"""
                write_to_daily_file(name, notice_log)
                latest_logs[name] += notice_log + "\n\n"
                if len(latest_logs[name]) > 10000:
                    latest_logs[name] = latest_logs[name][-10000:]
                time.sleep(5)
                continue

            opens = [candle[1] for candle in ohlcv]
            highs = [candle[2] for candle in ohlcv]
            lows = [candle[3] for candle in ohlcv]
            closes = [candle[4] for candle in ohlcv]
            volumes = [candle[5] for candle in ohlcv]

            state, signal, telemetry = sensex_core_logic.analyze_market(
                closes, highs, lows, volumes, asset_states[name], opens=opens
            )

            asset_states[name] = state
            save_todays_metrics(name, state["metrics"])

            p_cross = "[Y]" if (signal and signal.get("type", "").startswith("ENTRY")) else "[N]"
            p_macro = "[Y]" if (state["current_trend"] == "BULLISH" and closes[-2] > telemetry.get("curr_200", 0)) or \
                               (state["current_trend"] == "BEARISH" and closes[-2] < telemetry.get("curr_200", 0)) else "[N]"
            p_candle = "[N]" if "Weak" in telemetry.get("pattern", "") else "[Y]"
            p_volume = "[Y]" if telemetry.get("vol_ratio", 0) >= 1.5 else "[N]"
            checklist_console_str = f"Cross: {p_cross} | 200EMA: {p_macro} | Candle: {p_candle} | Volume Fuel: {p_volume}"

            file_log_block = f"""-----------------------------------------------------------------------------------------
{format_terminal_log('GLOBAL MARKET SCAN', f"{name} ({details['symbol']}) {details['timeframe']}")}
{format_terminal_log(name, f"Last ₹{telemetry['last_price']:,.2f} | 9 EMA {telemetry['curr_9']:,.2f} | 15 EMA {telemetry['curr_15']:,.2f} | 200 EMA {telemetry['curr_200']:,.2f}")}
{format_terminal_log('Strategy Core', f"{state['current_trend']} | Age {state['trend_age']}m | Spread ₹{telemetry['spread']:,.2f} ({telemetry['spread_pct']:.3f}%)")}
{format_terminal_log('Price Action', f"{telemetry['pattern']} | Vol Ratio {telemetry['vol_ratio']}x | {telemetry['breakout']}")}
{format_terminal_log('Setup Checklist', telemetry['checklist_file_str'])}
{format_terminal_log('System Action', f"{telemetry['sys_action']} [{status_text}]")}
-----------------------------------------------------------------------------------------"""
            write_to_daily_file(name, file_log_block)
            latest_logs[name] += file_log_block + "\n\n"
            if len(latest_logs[name]) > 10000:
                latest_logs[name] = latest_logs[name][-10000:]

            print("-----------------------------------------------------------------------------------------")
            print(format_terminal_log("GLOBAL MARKET SCAN", f"{name} ({details['symbol']}) {details['timeframe']}"))
            print(format_terminal_log(name, f"Last ₹{telemetry['last_price']:,.2f} | 9 EMA {telemetry['curr_9']:,.2f} | 15 EMA {telemetry['curr_15']:,.2f} | 200 EMA {telemetry['curr_200']:,.2f}"))
            print(format_terminal_log("Strategy Core", f"{state['current_trend']} | Age {state['trend_age']}m | Spread ₹{telemetry['spread']:,.2f} ({telemetry['spread_pct']:.3f}%)"))
            print(format_terminal_log("Price Action", f"{telemetry['pattern']} | Vol Ratio {telemetry['vol_ratio']}x | {telemetry['breakout']}"))
            print(format_terminal_log("Setup Checklist", checklist_console_str))
            print(format_terminal_log("System Action", telemetry['sys_action']))
            print("-----------------------------------------------------------------------------------------")

            if signal and not is_duplicate_signal(name, signal):
                if signal["type"].startswith("ENTRY"):
                    # Dispatch Option 1 Alerts
                    telegram_utils.send_signal_alert(
                        asset_name=name, trend=state["current_trend"], price=signal["price"],
                        pattern=signal["pattern"], breakout=signal["breakout"], vol_ratio=signal["vol_ratio"],
                        dist_sign=signal["dist_sign"], dist_val=signal["distance_200"]
                    )
                    whatsapp_utils.send_signal_alert(
                        asset_name=name, trend=state["current_trend"], price=signal["price"],
                        pattern=signal["pattern"], breakout=signal["breakout"], vol_ratio=signal["vol_ratio"],
                        dist_sign=signal["dist_sign"], dist_val=signal["distance_200"]
                    )
                    # Phase 2 Hook: Automated Option Execution on Dhan if AUTO_TRADE_ENABLED = True
                    dhan_order_router.place_sensex_option_order(signal["price"], state["current_trend"])
                
                elif signal["type"] == "HARD_EXIT":
                    outcome_emoji = "🟢 SUCCESS WIN" if signal["result"] == "WIN" else "🔴 STOP LOSS FAIL"
                    exit_msg = (
                        f"🚨 *HARD EXIT: {name} (BSE SENSEX)* 🚨\n\n"
                        f"• *Trade Result:* {outcome_emoji}\n"
                        f"• *Points Output:* {signal['points']:+.2f} Pts\n"
                        f"• *Exit Realized Price:* ₹{signal['price']:,.2f}\n\n"
                        f"📊 *Running Scorecard Today:*\n"
                        f"🏆 Wins: {state['metrics']['wins']} | ❌ Losses: {state['metrics']['losses']}\n"
                        f"💰 Net Performance: {state['metrics']['net_points']:+.2f} points"
                    )
                    telegram_utils.send_telegram(exit_msg)
                    whatsapp_utils.send_hard_exit_alert(exit_msg)

                elif signal["type"] == "EOD_REPORT":
                    telegram_utils.send_eod_report(name, signal["date"], signal["wins"], signal["losses"], signal["net_points"])
                    whatsapp_utils.send_eod_report(name, signal["date"], signal["wins"], signal["losses"], signal["net_points"])

            active_trade = state["active_trade"]
            if active_trade["direction"] == state["current_trend"] and state["trend_age"] > 0:
                if active_trade["direction"] == "BULLISH":
                    points_moved = telemetry["last_price"] - active_trade["entry_price"]
                else:
                    points_moved = active_trade["entry_price"] - telemetry["last_price"]
                    
                milestones = [50.0, 100.0, 150.0, 300.0] # Sensex milestone points
                for target in milestones:
                    if points_moved >= target and target not in active_trade["targets_achieved"]:
                        active_trade["targets_achieved"].append(target)
                        telegram_utils.send_milestone_alert(
                            asset_name=name, target=target, entry=active_trade["entry_price"],
                            current=telemetry["last_price"], trend_age=state["trend_age"], points_moved=points_moved
                        )
                        whatsapp_utils.send_milestone_alert(
                            asset_name=name, target=target, entry=active_trade["entry_price"],
                            current=telemetry["last_price"], trend_age=state["trend_age"], points_moved=points_moved
                        )

        except Exception as e:
            print(format_terminal_log("CONNECTION ERROR", f"[{name}] Live feed dropped: {str(e)}"))
            time.sleep(10)

_nodes_started = False
_nodes_lock = threading.Lock()
_manager_pid = None

def start_manager_nodes():
    global _nodes_started, _manager_pid
    current_pid = os.getpid()
    with _nodes_lock:
        if _nodes_started and _manager_pid == current_pid:
            return
        _nodes_started = True
        _manager_pid = current_pid
        for name, details in config.ASSETS.items():
            t = threading.Thread(target=run_asset_production_loop, args=(name, details), daemon=True)
            t.start()

if __name__ == "__main__":
    start_manager_nodes()
    while True:
        time.sleep(1)
