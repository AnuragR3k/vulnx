import sqlite3
import os
import logging
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import time
from scanner import WebSecurityScanner  # Your custom scanner
from siem_integration import SIEMForwarder
from security_grade import analyze_security_posture


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

DB_PATH = os.environ.get('VULNX_DB_PATH', './vulnx.sqlite3')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY','changeme-please')


CORS(app, origins=[
    "https://vulnx.vercel.app",  # Your production URL
    "http://localhost:5173",      # For local testing
    "*"                           # Or allow all (less secure)
])
# --- Database helpers ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS scan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        url TEXT,
        mode TEXT,
        ts TEXT,
        result_json TEXT,
        FOREIGN KEY(user_id) REFERENCES user(id)
    );
    ''')
    db.commit()

app.before_request(init_db)

CORS(app)  # Enable CORS for React frontend

siem_forwarder = SIEMForwarder()

@app.route('/api/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()
        target_url = data.get('url')
        # Only basic mode, no mode param needed
        if not target_url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Add http:// if missing
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url

        logger.info("[BASIC SCAN] Starting scan on %s", target_url)
        scanner = WebSecurityScanner(target_url, max_depth=1)
        vulnerabilities = scanner.scan()
        logger.info("[BASIC SCAN] Found %d vulnerabilities", len(vulnerabilities))

        security_grade = analyze_security_posture(target_url)
        logger.info("[SECURITY GRADE] %s scored %s (%d/100)", target_url, security_grade["grade"], security_grade["score"])

        scan_id = SIEMForwarder.generate_scan_id()
        try:
            siem_forwarder.forward_scan_results(target_url, vulnerabilities, scan_id)
        except Exception as siem_error:
            # Never fail the scan response if SIEM forwarding raises unexpectedly.
            logger.error("[SIEM] Forwarding error (scan continues): %s", siem_error)

        return jsonify({'vulnerabilities': vulnerabilities, 'security_grade': security_grade}), 200

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[SCAN ERROR]\n{error_trace}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def api_register():
    # Your existing register code
    pass

@app.route('/api/login', methods=['POST'])
def api_login():
    # Your existing login code
    pass

@app.route('/api/logout', methods=['POST'])
def api_logout():
    # Your existing logout code
    pass

@app.route('/api/whoami', methods=['GET'])
def api_whoami():
    # Your existing whoami code
    pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ('1', 'true', 'yes')
    logger.info("[SERVER] Starting VulnX backend on port %s", port)
    if siem_forwarder.enabled:
        logger.info("[SERVER] SIEM integration active — endpoint=%s", siem_forwarder.endpoint)
    else:
        logger.info("[SERVER] SIEM integration inactive — set SIEM_ENDPOINT to enable")
    app.run(debug=debug, port=port, host='0.0.0.0')