# BSE Sensex Scalper Engine (`bse-sensex-sentry`)

An institutional-grade quantitative trading and monitoring engine for the **BSE Sensex Index & Options**, operating strictly during Indian Stock Market hours (**9:15 AM to 3:30 PM IST**).

---

## 🌟 Key Features

* **🇮🇳 Indian Market Hours Controller (`market_schedule.py`)**: Operates strictly between 9:15 AM and 3:30 PM IST on Indian stock market trading days (excluding NSE/BSE holidays).
* **⚡ Dhan API Integration (`dhanhq`)**: Free live feeds and index market ticks powered by Dhan API.
* **📈 Sensex Scalper Logic (`sensex_core_logic.py`)**: EMA 9/15 crossover strategy, 200 EMA macro filter, 20-period volume velocity ratio, candle body strength profiling, and 15 EMA close hard exit rules.
* **🛡️ 3:15 PM IST Mandatory Intraday Squareoff**: Auto-squares off intraday options positions to avoid broker penalty fees.
* **📢 Multi-Channel Signal Alerts**: Telegram Bot API and Green-API WhatsApp group alerts with direct TradingView Sensex chart links.
* **🖥️ Executive Console UI (`templates/index.html`)**: Styled for Indian Market (INR ₹ formatting, Market Status Badges, Auto-Scroll ON/OFF Lock, and Save Log .txt export).
* **🔁 Phase 2 Ready (`AUTO_TRADE_ENABLED`)**: Flip `AUTO_TRADE_ENABLED = True` in `config.py` anytime to enable automated Dhan SENSEX Options (`CE` / `PE`) trading!

---

## 🚀 How to Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional) Set your Dhan API Credentials in Environment Variables or `config.py`:
   ```bash
   export DHAN_CLIENT_ID="1000XXXXXX"
   export DHAN_ACCESS_TOKEN="your_access_token_from_dhanhq.co"
   ```
   *Note: If no Dhan token is set, the application automatically runs in Fallback Market Feed Mode.*

3. Start the Flask application:
   ```bash
   python app.py
   ```

4. Open your browser at **[http://localhost:5001](http://localhost:5001)**.
