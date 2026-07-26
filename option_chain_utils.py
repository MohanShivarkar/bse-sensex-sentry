# option_chain_utils.py
"""
Option Chain Selection Utility for BSE SENSEX Weekly Options (Phase 2 Ready).
Calculates nearest At-The-Money (ATM) / In-The-Money (ITM) Strike prices for SENSEX Options.
SENSEX Option strike interval = 100 points.
"""

def get_sensex_option_strike(spot_price: float, option_type: str = "CE", offset_strikes: int = 0) -> int:
    """
    Calculates the target SENSEX Option strike price.
    - spot_price: Current SENSEX Index spot price (e.g. 80450.50)
    - option_type: 'CE' (Call Option) or 'PE' (Put Option)
    - offset_strikes: 0 for ATM, +1 for 1-strike ITM/OTM
    """
    # Round to nearest 100 points (SENSEX Strike step size = 100)
    atm_strike = int(round(spot_price / 100.0) * 100)
    
    if option_type.upper() == "CE":
        target_strike = atm_strike - (offset_strikes * 100) # Slightly ITM Call for higher delta
    else:
        target_strike = atm_strike + (offset_strikes * 100) # Slightly ITM Put for higher delta
        
    return target_strike

def format_sensex_option_symbol(strike_price: int, option_type: str = "CE") -> str:
    """
    Formats standard SENSEX option string for Dhan API lookup.
    Example: SENSEX 80500 CE
    """
    return f"SENSEX {strike_price} {option_type.upper()}"
