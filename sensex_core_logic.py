# sensex_core_logic.py
"""
Phase 3.0 (Sensex) Execution Engine.
Features:
- Micro-Trailing Engine (Level 1 Breakeven Lock at +15-20 pts, Level 2 Dynamic 20-pt Trail at +40 pts).
- Mandatory 3-Minute Post-Exit Cooldown (180s).
- Opposing Wick Rejection Filter (>40% Wick Height).
- 3 Consecutive Loss Circuit Breaker (30-min pause).
- Ghost SL Purge & Complete State Hygiene.
"""
import time
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

def calculate_ema(prices, period):
    if len(prices) < period:
        return [prices[-1]] * len(prices)
    k = 2 / (period + 1)
    ema = [prices[0]]
    for price in prices[1:]:
        ema.append(price * k + ema[-1] * (1 - k))
    return ema

def calculate_adx_wilder(highs, lows, closes, period=14):
    if len(closes) < period * 2:
        return 25.0
    tr = []
    dm_plus = []
    dm_minus = []
    for i in range(1, len(closes)):
        h_diff = highs[i] - highs[i-1]
        l_diff = lows[i-1] - lows[i]
        up = h_diff if (h_diff > l_diff and h_diff > 0) else 0.0
        down = l_diff if (l_diff > h_diff and l_diff > 0) else 0.0
        tr_val = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        tr.append(tr_val)
        dm_plus.append(up)
        dm_minus.append(down)
    
    atr_smooth = sum(tr[:period])
    plus_smooth = sum(dm_plus[:period])
    minus_smooth = sum(dm_minus[:period])
    
    dx_list = []
    for i in range(period, len(tr)):
        atr_smooth = atr_smooth - (atr_smooth / period) + tr[i]
        plus_smooth = plus_smooth - (plus_smooth / period) + dm_plus[i]
        minus_smooth = minus_smooth - (minus_smooth / period) + dm_minus[i]
        
        di_p = 100 * (plus_smooth / atr_smooth) if atr_smooth > 0 else 0
        di_m = 100 * (minus_smooth / atr_smooth) if atr_smooth > 0 else 0
        di_sum = di_p + di_m
        dx = 100 * (abs(di_p - di_m) / di_sum) if di_sum > 0 else 0
        dx_list.append(dx)
        
    if not dx_list:
        return 25.0
    adx = sum(dx_list[-period:]) / min(len(dx_list), period)
    return round(adx, 1)

def is_wick_rejection(c_open, c_high, c_low, c_close, trend):
    c_range = c_high - c_low
    if c_range <= 0:
        return False
        
    if trend == "BULLISH":
        upper_wick = c_high - max(c_open, c_close)
        return (upper_wick / c_range) > 0.40
    elif trend == "BEARISH":
        lower_wick = min(c_open, c_close) - c_low
        return (lower_wick / c_range) > 0.40
    return False

def evaluate_micro_trailing(state, current_price, curr_15):
    trade = state.get("active_trade", {})
    direction = trade.get("direction")
    if not direction:
        return None, state

    entry_price = trade.get("entry_price", 0.0)
    now_ts = time.time()
    signal = None

    if direction == "BULLISH":
        if current_price > trade.get("max_expansion", 0.0):
            trade["max_expansion"] = current_price
        
        peak_gain = trade["max_expansion"] - entry_price
        current_gain = current_price - entry_price

        if peak_gain >= 15.0 and trade.get("sl_price", 0.0) < (entry_price + 2.0):
            trade["sl_price"] = entry_price + 2.0
            trade["trail_level"] = 1

        if peak_gain >= 40.0:
            new_sl = trade["max_expansion"] - 20.0
            if new_sl > trade.get("sl_price", 0.0):
                trade["sl_price"] = new_sl
                trade["trail_level"] = 2

        effective_sl = max(trade.get("sl_price", 0.0), curr_15)
        if current_price <= effective_sl:
            retained_points = round(current_gain, 2)
            is_win = (retained_points > 0)
            result_tag = "WIN" if is_win else "LOSS"

            if is_win:
                state["metrics"]["wins"] += 1
                state["consecutive_losses"] = 0
            else:
                state["metrics"]["losses"] += 1
                state["consecutive_losses"] = state.get("consecutive_losses", 0) + 1

            state["metrics"]["net_points"] += retained_points
            state["last_exit_timestamp"] = now_ts
            
            if state.get("consecutive_losses", 0) >= 3:
                state["circuit_breaker_until"] = now_ts + 1800

            signal = {
                "type": "HARD_EXIT", "price": current_price, "direction": "BULLISH",
                "result": result_tag, "points": retained_points, "trail_level": trade.get("trail_level", 0)
            }
            state["active_trade"] = {"direction": None, "entry_price": 0.0, "max_expansion": 0.0, "sl_price": 0.0, "trail_level": 0}
            state["current_trend"] = "NEUTRAL"

    elif direction == "BEARISH":
        if current_price < trade.get("max_expansion", 99999999.0) or trade.get("max_expansion") == 0.0:
            trade["max_expansion"] = current_price
        
        peak_gain = entry_price - trade["max_expansion"]
        current_gain = entry_price - current_price

        if peak_gain >= 15.0 and (trade.get("sl_price", 99999999.0) > (entry_price - 2.0)):
            trade["sl_price"] = entry_price - 2.0
            trade["trail_level"] = 1

        if peak_gain >= 40.0:
            new_sl = trade["max_expansion"] + 20.0
            if trade.get("sl_price", 99999999.0) == 0.0 or new_sl < trade["sl_price"]:
                trade["sl_price"] = new_sl
                trade["trail_level"] = 2

        effective_sl = min(trade["sl_price"], curr_15) if trade.get("sl_price", 0.0) > 0 else curr_15
        if current_price >= effective_sl:
            retained_points = round(current_gain, 2)
            is_win = (retained_points > 0)
            result_tag = "WIN" if is_win else "LOSS"

            if is_win:
                state["metrics"]["wins"] += 1
                state["consecutive_losses"] = 0
            else:
                state["metrics"]["losses"] += 1
                state["consecutive_losses"] = state.get("consecutive_losses", 0) + 1

            state["metrics"]["net_points"] += retained_points
            state["last_exit_timestamp"] = now_ts
            
            if state.get("consecutive_losses", 0) >= 3:
                state["circuit_breaker_until"] = now_ts + 1800

            signal = {
                "type": "HARD_EXIT", "price": current_price, "direction": "BEARISH",
                "result": result_tag, "points": retained_points, "trail_level": trade.get("trail_level", 0)
            }
            state["active_trade"] = {"direction": None, "entry_price": 0.0, "max_expansion": 0.0, "sl_price": 0.0, "trail_level": 0}
            state["current_trend"] = "NEUTRAL"

    return signal, state

def analyze_market(closes, highs, lows, volumes, state, opens=None):
    now_ts = time.time()

    if len(closes) < 201:
        last_price = closes[-1] if len(closes) > 0 else 80000.0
        fallback_telemetry = {
            "last_price": last_price,
            "curr_9": last_price, "curr_15": last_price, "curr_200": last_price,
            "spread": 0.0, "spread_pct": 0.0, "pattern": "Good Candle",
            "vol_ratio": 1.0, "breakout": "Inside Bar Consolidation", "body_ratio": 0.50,
            "checklist_file_str": "Cross: ❌ | 200EMA: ❌ | Candle: ❌ | Volume Fuel: ❌",
            "sys_action": "Gathering initial SENSEX market ticks..."
        }
        return state, None, fallback_telemetry

    today_str = datetime.now(IST).strftime("%Y-%m-%d")
    eod_signal = None

    if "metrics" in state and state["metrics"].get("date") and state["metrics"].get("date") != today_str:
        prev_date = state["metrics"].get("date")
        eod_signal = {
            "type": "EOD_REPORT",
            "date": prev_date,
            "wins": state["metrics"].get("wins", 0),
            "losses": state["metrics"].get("losses", 0),
            "net_points": state["metrics"].get("net_points", 0.0)
        }
        state["metrics"] = {"date": today_str, "wins": 0, "losses": 0, "net_points": 0.0}
        state["consecutive_losses"] = 0
    elif "metrics" not in state:
        state["metrics"] = {"date": today_str, "wins": 0, "losses": 0, "net_points": 0.0}

    if "active_trade" not in state or not isinstance(state["active_trade"], dict):
        state["active_trade"] = {"direction": None, "entry_price": 0.0, "max_expansion": 0.0, "sl_price": 0.0, "trail_level": 0}

    ema9_vector = calculate_ema(closes, 9)
    ema15_vector = calculate_ema(closes, 15)
    ema200_vector = calculate_ema(closes, 200)

    last_price = closes[-2]
    prev_9, curr_9 = ema9_vector[-3], ema9_vector[-2]
    prev_15, curr_15 = ema15_vector[-3], ema15_vector[-2]
    curr_200 = ema200_vector[-2]

    adx_val = calculate_adx_wilder(highs, lows, closes, 14)

    spread = abs(curr_9 - curr_15)
    spread_pct = (spread / curr_15) * 100 if curr_15 > 0 else 0.0
    distance_200 = last_price - curr_200
    dist_sign = "+" if distance_200 >= 0 else "-"

    historical_avg_vol = sum(volumes[-22:-2]) / 20 if len(volumes) >= 22 else 1.0
    current_vol = volumes[-2] if len(volumes) >= 2 else 1.0
    vol_ratio = round(current_vol / historical_avg_vol, 1) if historical_avg_vol > 0 else 1.0

    is_bullish_cross = (prev_9 <= prev_15) and (curr_9 > curr_15)
    is_bearish_cross = (prev_9 >= prev_15) and (curr_9 < curr_15)

    # TRUE CANDLE BODY DELTA
    candle_open = opens[-2] if (opens and len(opens) >= 2) else closes[-3]
    candle_high = highs[-2]
    candle_low = lows[-2]
    is_green_candle = closes[-2] >= candle_open
    candle_body = abs(closes[-2] - candle_open)
    candle_range = max(candle_high - candle_low, 0.00001)
    body_ratio = candle_body / candle_range
    body_ratio_rounded = round(body_ratio, 2)
    color_label = "Green" if is_green_candle else "Red"

    if body_ratio >= 0.70:
        pattern = f"Strong {color_label} Candle"
    elif 0.35 <= body_ratio < 0.70:
        pattern = f"Good {color_label} Candle"
    else:
        pattern = f"Weak {color_label} Candle"

    breakout = "Prev High Smashed" if last_price > highs[-3] else ("Prev Low Smashed" if last_price < lows[-3] else "Inside Bar Consolidation")

    if is_bullish_cross:
        state["current_trend"] = "BULLISH"
        state["trend_age"] = 0
    elif is_bearish_cross:
        state["current_trend"] = "BEARISH"
        state["trend_age"] = 0
    elif curr_9 > curr_15:
        if state["current_trend"] != "BULLISH":
            state["current_trend"] = "BULLISH"
            state["trend_age"] = 1
        else:
            state["trend_age"] += 1
    elif curr_9 < curr_15:
        if state["current_trend"] != "BEARISH":
            state["current_trend"] = "BEARISH"
            state["trend_age"] = 1
        else:
            state["trend_age"] += 1
    else:
        state["current_trend"] = "NEUTRAL"
        state["trend_age"] = 0

    last_exit_ts = state.get("last_exit_timestamp", 0)
    cooldown_remaining = max(0, int(180 - (now_ts - last_exit_ts)))
    is_cooldown_active = (cooldown_remaining > 0)

    cb_until = state.get("circuit_breaker_until", 0)
    cb_remaining = max(0, int(cb_until - now_ts))
    is_cb_active = (cb_remaining > 0)

    is_wick_rejected = is_wick_rejection(candle_open, candle_high, candle_low, closes[-2], state["current_trend"])

    tick_cross = "✅" if (is_bullish_cross or is_bearish_cross or state["trend_age"] <= 5) else "❌"
    has_macro_clearance = False
    if state["current_trend"] == "BULLISH" and last_price > curr_200: 
        has_macro_clearance = True
    elif state["current_trend"] == "BEARISH" and last_price < curr_200: 
        has_macro_clearance = True
    tick_macro = "✅" if has_macro_clearance else "❌"
    
    is_solid_candle = (body_ratio >= 0.35) and (not is_wick_rejected)
    tick_adx = "✅" if adx_val >= 15.0 else "❌"
    tick_body = "✅" if is_solid_candle else "❌"

    checklist_file_str = f"Cross: {tick_cross} | 200EMA: {tick_macro} | ADX({adx_val}): {tick_adx} | Body({body_ratio_rounded}): {tick_body}"
    sys_action = f"Monitoring {state['current_trend']} SENSEX trend... Holding state (Age {state['trend_age']}m)"
    signal = None

    if state["active_trade"]["direction"] is None and state["current_trend"] in ("BULLISH", "BEARISH") and state["trend_age"] <= 5:
        if is_cb_active:
            sys_action = f"CIRCUIT BREAKER ACTIVE (3 consecutive losses). Trading paused for {cb_remaining}s."
        elif is_cooldown_active:
            sys_action = f"POST-EXIT COOLDOWN ACTIVE. Re-entry locked for {cooldown_remaining}s."
        elif is_wick_rejected:
            sys_action = f"ENTRY REJECTED: Preceding candle opposing wick >40% of range."
        else:
            if state["current_trend"] == "BULLISH":
                if last_price > curr_200 and is_solid_candle:
                    sys_action = f"Bullish breakout verified (Age {state['trend_age']}m)! Transmitting entry..."
                    state["active_trade"] = {"direction": "BULLISH", "entry_price": last_price, "max_expansion": last_price, "sl_price": 0.0, "trail_level": 0}
                    signal = {
                        "type": "ENTRY_BULLISH", "price": last_price, "pattern": pattern,
                        "breakout": breakout, "vol_ratio": vol_ratio, "dist_sign": dist_sign, "distance_200": abs(distance_200)
                    }
                else:
                    reason = "under 200 EMA" if last_price <= curr_200 else "weak candle / wick rejection"
                    sys_action = f"Entry window open (Age {state['trend_age']}m) | Pending: {reason}"
                    
            elif state["current_trend"] == "BEARISH":
                if last_price < curr_200 and is_solid_candle:
                    sys_action = f"Bearish breakdown verified (Age {state['trend_age']}m)! Transmitting entry..."
                    state["active_trade"] = {"direction": "BEARISH", "entry_price": last_price, "max_expansion": last_price, "sl_price": 0.0, "trail_level": 0}
                    signal = {
                        "type": "ENTRY_BEARISH", "price": last_price, "pattern": pattern,
                        "breakout": breakout, "vol_ratio": vol_ratio, "dist_sign": dist_sign, "distance_200": abs(distance_200)
                    }
                else:
                    reason = "over 200 EMA" if last_price >= curr_200 else "weak candle / wick rejection"
                    sys_action = f"Entry window open (Age {state['trend_age']}m) | Pending: {reason}"

    elif state["current_trend"] == "NEUTRAL" and state["active_trade"]["direction"] is None:
        state["active_trade"] = {"direction": None, "entry_price": 0.0, "max_expansion": 0.0, "sl_price": 0.0, "trail_level": 0}

    if state["active_trade"]["direction"] is not None:
        micro_sig, state = evaluate_micro_trailing(state, last_price, curr_15)
        if micro_sig:
            signal = micro_sig

    if signal is None and eod_signal is not None:
        signal = eod_signal

    telemetry = {
        "last_price": last_price,
        "curr_9": curr_9, "curr_15": curr_15, "curr_200": curr_200,
        "spread": spread, "spread_pct": spread_pct,
        "pattern": pattern, "vol_ratio": vol_ratio, "breakout": breakout,
        "adx": adx_val, "body_ratio": body_ratio_rounded,
        "checklist_file_str": checklist_file_str,
        "sys_action": sys_action
    }

    return state, signal, telemetry
