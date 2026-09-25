import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = BASE_DIR

# IPRoyal Residential Proxy
PROXY_HOST = "geo.iproyal.com"
PROXY_PORT = 12321
PROXY_USER = "QpM15E2X6SKxs5Jn"
PROXY_PASS = "FaUi7YQJVChJeDuU"

PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

REQUESTS_PROXIES = {
    'http': PROXY_URL,
    'https': PROXY_URL
}

PLAYWRIGHT_PROXY = {
    "server": f"http://{PROXY_HOST}:{PROXY_PORT}",
    "username": PROXY_USER,
    "password": PROXY_PASS
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# LinkedIn Configuration
# Method 3 (Session Cookie): Paste your li_at session cookie here or set LINKEDIN_LI_AT env var
LINKEDIN_LI_AT = os.environ.get("LINKEDIN_LI_AT", "")
