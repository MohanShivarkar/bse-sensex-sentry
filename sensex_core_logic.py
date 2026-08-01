# sensex_core_logic.py
"""
Phase 2.1 BSE Sensex Core Engine with Trend Entry Window & Wilder ADX Smoothing.
"""
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

def analyze_market(closes, highs, lows, volumes, state):
    if len(closes) < 201:
        last_price = closes[-1] if len(closes) > 0 else 80000.0
        fallback_telemetry = {
            "last_price": last_price,
            "curr_9": last_price, "curr_15": last_price, "curr_200": last_price,
            "spread": 0.0, "spread_pct": 0.0, "pattern": "Good Candle",
            "vol_ratio": 1.0, "breakout": "Inside Bar Consolidation",
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

    is_green_candle = closes[-2] > closes[-3]
    candle_body = abs(closes[-2] - closes[-3])
    candle_range = highs[-2] - lows[-2]
    body_ratio = (candle_body / candle_range) if candle_range > 0 else 0.0
    body_ratio_rounded = round(body_ratio, 2)
    color_label = "Green" if is_green_candle else "Red"

    if body_ratio >= 0.75:
        pattern = f"Strong {color_label} Candle"
    elif 0.40 <= body_ratio < 0.75:
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

    tick_cross = "✅" if (is_bullish_cross or is_bearish_cross or state["trend_age"] <= 5) else "❌"
    has_macro_clearance = False
    if state["current_trend"] == "BULLISH" and last_price > curr_200: 
        has_macro_clearance = True
    elif state["current_trend"] == "BEARISH" and last_price < curr_200: 
        has_macro_clearance = True
    tick_macro = "✅" if has_macro_clearance else "❌"
    
    is_solid_candle = (body_ratio >= 0.40)
    tick_adx = "✅" if adx_val >= 15.0 else "❌"
    tick_body = "✅" if is_solid_candle else "❌"

    checklist_file_str = f"Cross: {tick_cross} | 200EMA: {tick_macro} | ADX({adx_val}): {tick_adx} | Body({body_ratio_rounded}): {tick_body}"
    sys_action = f"Monitoring {state['current_trend']} SENSEX trend... Holding state (Age {state['trend_age']}m)"
    signal = None

    # Early Trend Entry Window (Age 0m - 5m)
    if state["active_trade"]["direction"] is None and state["current_trend"] in ("BULLISH", "BEARISH") and state["trend_age"] <= 5:
        if state["current_trend"] == "BULLISH":
            if last_price > curr_200 and is_solid_candle:
                sys_action = f"Bullish breakout verified (Age {state['trend_age']}m)! Transmitting entry..."
                state["active_trade"] = {"direction": "BULLISH", "entry_price": last_price, "max_expansion": last_price, "targets_achieved": []}
                signal = {
                    "type": "ENTRY_BULLISH", "price": last_price, "pattern": pattern,
                    "breakout": breakout, "vol_ratio": vol_ratio, "dist_sign": dist_sign, "distance_200": abs(distance_200)
                }
            else:
                reason = "under 200 EMA" if last_price <= curr_200 else "weak candle body"
                sys_action = f"Entry window open (Age {state['trend_age']}m) | Pending: {reason}"
                
        elif state["current_trend"] == "BEARISH":
            if last_price < curr_200 and is_solid_candle:
                sys_action = f"Bearish breakdown verified (Age {state['trend_age']}m)! Transmitting entry..."
                state["active_trade"] = {"direction": "BEARISH", "entry_price": last_price, "max_expansion": last_price, "targets_achieved": []}
                signal = {
                    "type": "ENTRY_BEARISH", "price": last_price, "pattern": pattern,
                    "breakout": breakout, "vol_ratio": vol_ratio, "dist_sign": dist_sign, "distance_200": abs(distance_200)
                }
            else:
                reason = "over 200 EMA" if last_price >= curr_200 else "weak candle body"
                sys_action = f"Entry window open (Age {state['trend_age']}m) | Pending: {reason}"

    elif state["current_trend"] == "NEUTRAL":
        state["active_trade"] = {"direction": None, "entry_price": 0.0, "targets_achieved": []}

    if state["active_trade"]["direction"] == "BULLISH":
        if last_price > state["active_trade"].get("max_expansion", 0.0):
            state["active_trade"]["max_expansion"] = last_price
    elif state["active_trade"]["direction"] == "BEARISH":
        if last_price < state["active_trade"].get("max_expansion", 99999999.0) or state["active_trade"].get("max_expansion") == 0.0:
            state["active_trade"]["max_expansion"] = last_price

    if state["active_trade"]["direction"] == "BULLISH" and last_price < curr_15:
        peak_points = state["active_trade"]["max_expansion"] - state["active_trade"]["entry_price"]
        raw_stop_loss_points = last_price - state["active_trade"]["entry_price"]

        if peak_points >= 50.0:
            state["metrics"]["wins"] += 1
            result_tag = "WIN"
            retained_points = max(state["active_trade"]["targets_achieved"]) if state["active_trade"]["targets_achieved"] else 50.0
        else:
            state["metrics"]["losses"] += 1
            result_tag = "LOSS"
            retained_points = raw_stop_loss_points

        state["metrics"]["net_points"] += retained_points
        sys_action = f"STRUCTURE BREACHED. Hard Exit. Result: {result_tag} ({retained_points:+.2f} pts)"
        signal = {"type": "HARD_EXIT", "price": last_price, "direction": "BULLISH", "result": result_tag, "points": retained_points}
        state["active_trade"] = {"direction": None, "entry_price": 0.0, "targets_achieved": []}
        state["current_trend"] = "NEUTRAL"

    elif state["active_trade"]["direction"] == "BEARISH" and last_price > curr_15:
        peak_points = state["active_trade"]["entry_price"] - state["active_trade"]["max_expansion"]
        raw_stop_loss_points = state["active_trade"]["entry_price"] - last_price

        if peak_points >= 50.0:
            state["metrics"]["wins"] += 1
            result_tag = "WIN"
            retained_points = max(state["active_trade"]["targets_achieved"]) if state["active_trade"]["targets_achieved"] else 50.0
        else:
            state["metrics"]["losses"] += 1
            result_tag = "LOSS"
            retained_points = raw_stop_loss_points

        state["metrics"]["net_points"] += retained_points
        sys_action = f"STRUCTURE BREACHED. Hard Exit. Result: {result_tag} ({retained_points:+.2f} pts)"
        signal = {"type": "HARD_EXIT", "price": last_price, "direction": "BEARISH", "result": result_tag, "points": retained_points}
        state["active_trade"] = {"direction": None, "entry_price": 0.0, "targets_achieved": []}
        state["current_trend"] = "NEUTRAL"

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
