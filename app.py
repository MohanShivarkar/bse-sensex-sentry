# app.py
from flask import Flask, render_template, jsonify, abort, request
import os
import threading
import time
import requests
import sensex_manager

app = Flask(__name__)

# Start the background BSE Sensex tracking daemon automatically on server boot
sensex_manager.start_manager_nodes()

def keep_alive_daemon():
    """
    Self-pinging background thread to prevent Render Free Tier from going to sleep.
    Pings local /status endpoint every 4 minutes to guarantee continuous Indian Market scanning.
    """
    time.sleep(15)
    port = int(os.environ.get("PORT", 5001))
    url = f"http://127.0.0.1:{port}/status"
    while True:
        try:
            requests.get(url, timeout=5)
        except Exception:
            pass
        time.sleep(240)

threading.Thread(target=keep_alive_daemon, daemon=True).start()

@app.before_request
def ensure_manager_nodes():
    sensex_manager.start_manager_nodes()

@app.route('/')
def index():
    """Renders the main BSE Sensex monitoring dashboard template."""
    return render_template('index.html')

@app.route('/status')
def status():
    """Exposes the live running tracker states for BSE Sensex."""
    return jsonify(sensex_manager.asset_states)

@app.route('/list_logs/<asset_name>')
def list_logs(asset_name):
    """Lists all available historical log files stored on disk for Sensex."""
    if asset_name not in sensex_manager.asset_states:
        return abort(404, description="Asset target not recognized.")
    log_dir = sensex_manager.get_logs_dir(asset_name)
    files = []
    if os.path.exists(log_dir):
        files = [f for f in os.listdir(log_dir) if f.startswith("sentry_log_") and f.endswith(".txt")]
        files.sort(reverse=True)
    return jsonify({"files": files})

@app.route('/get_log/<asset_name>')
def get_log(asset_name):
    """Dynamically serves active RAM logs or selected historical log files."""
    if asset_name not in sensex_manager.asset_states:
        return abort(404, description="Asset target not recognized.")
        
    requested_file = request.args.get("file")
    log_dir = sensex_manager.get_logs_dir(asset_name)
    
    if requested_file:
        safe_filename = os.path.basename(requested_file)
        file_path = os.path.join(log_dir, safe_filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    recent_logs = "".join(lines[-250:])
                    return jsonify({"log": recent_logs})
            except Exception as e:
                return jsonify({"log": f"Error loading historical log file: {str(e)}"})
        return jsonify({"log": "Selected historical log file not found."})

    # Priority 1: Serve directly from RAM memory buffer
    mem_log = sensex_manager.latest_logs.get(asset_name, "")
    if mem_log.strip():
        return jsonify({"log": mem_log})

    # Priority 2: Disk file fallback
    date_str = sensex_manager.get_ist_now().strftime("%Y-%m-%d")
    file_path = os.path.join(log_dir, f"sentry_log_{date_str}.txt")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_logs = "".join(lines[-150:])
                if recent_logs.strip():
                    return jsonify({"log": recent_logs})
        except Exception:
            pass

    return jsonify({"log": f"[{sensex_manager.get_ist_now().strftime('%H:%M:%S IST')}] SENSEX Core Engine: Synchronizing Indian Market candle closure data..."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
