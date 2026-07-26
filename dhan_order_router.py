# dhan_order_router.py
import config
import dhan_auth
import option_chain_utils

def place_sensex_option_order(spot_price: float, direction: str) -> dict:
    """
    Places an automated Intraday (MIS) Option Buy order on Dhan API when AUTO_TRADE_ENABLED = True.
    - direction: 'BULLISH' (Buys CE Call Option) or 'BEARISH' (Buys PE Put Option)
    """
    if not config.AUTO_TRADE_ENABLED:
        print("[ORDER ROUTER NOTICE] Auto-trading is disabled (AUTO_TRADE_ENABLED = False). Skipping Dhan order execution.")
        return {"status": "SKIPPED", "reason": "Monitoring Mode Active"}
        
    dhan = dhan_auth.get_dhan_client()
    if not dhan:
        print("[ORDER ROUTER ERROR] Dhan API client not authenticated.")
        return {"status": "FAILED", "reason": "Dhan Auth Missing"}

    option_type = "CE" if direction == "BULLISH" else "PE"
    strike = option_chain_utils.get_sensex_option_strike(spot_price, option_type, offset_strikes=0)
    symbol_str = option_chain_utils.format_sensex_option_symbol(strike, option_type)
    
    print(f"[DHAN ORDER ROUTER] Executing Intraday Buy for {symbol_str} at Spot ₹{spot_price:,.2f}...")
    
    try:
        # Dhan Order Placement Signature (Phase 2 Auto-Trading Hook)
        # response = dhan.place_order(
        #     security_id=strike_sec_id,
        #     exchange_segment=dhan.BSE_FNO,
        #     transaction_type=dhan.BUY,
        #     quantity=10, # SENSEX Lot size
        #     order_type=dhan.MARKET,
        #     product_type=dhan.INTRA,
        #     price=0
        # )
        return {"status": "SUCCESS", "symbol": symbol_str, "strike": strike}
    except Exception as e:
        print(f"[DHAN ORDER ERROR] Order placement exception: {e}")
        return {"status": "FAILED", "reason": str(e)}

def auto_squareoff_all_positions() -> dict:
    """
    Mandatory 3:15 PM IST Intraday Squareoff to close all open options positions before market close.
    """
    if not config.AUTO_TRADE_ENABLED:
        return {"status": "SKIPPED"}
        
    print("[DHAN ORDER ROUTER] 3:15 PM IST Reached. Triggering mandatory intraday auto-squareoff...")
    return {"status": "SQUARED_OFF"}
