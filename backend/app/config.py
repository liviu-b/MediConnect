from pathlib import Path
import os
import logging
import json
from dotenv import load_dotenv

# --- 1. Setup Environment ---
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / '.env'
load_dotenv(ENV_PATH)

# --- 2. Database Config ---
MONGO_URL = os.environ.get('MONGO_URL', '')
if not MONGO_URL:
    raise ValueError("MONGO_URL environment variable is required")

DB_NAME = os.environ.get('DB_NAME', 'mediconnect_db')

# --- 3. Email Config ---
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'MediConnect <onboarding@resend.dev>')

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# --- 4. Helper Functions for Parsing ---
def _parse_list(value, default_list):
    """Safely parses a string list from env vars (e.g. '["http://a.com"]')"""
    if value is None:
        return list(default_list)
    if isinstance(value, (list, tuple)):
        return list(value)
    s = str(value).strip()
    if s.startswith("[") and s.endswith("]"):
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
    return [item.strip() for item in s.split(",") if item.strip()]

def _parse_bool(value, default):
    """Safely parses boolean values from env vars"""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    low = str(value).strip().lower()
    if low in ("true", "1", "yes", "y"):
        return True
    if low in ("false", "0", "no", "n"):
        return False
    return default

# --- 5. CORS Configuration (The Fix) ---

# Specific defaults for local development
_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Load origins from .env, or use the safe defaults above
_raw_origins = os.environ.get('CORS_ORIGINS')
CORS_ORIGINS = _parse_list(_raw_origins, _default_origins)

# Handle Credentials
_raw_allow_credentials = os.environ.get('CORS_ALLOW_CREDENTIALS', 'true')
CORS_ALLOW_CREDENTIALS = _parse_bool(_raw_allow_credentials, True)

# Handle Methods and Headers
_raw_methods = os.environ.get('CORS_ALLOW_METHODS', '["*"]')
_raw_headers = os.environ.get('CORS_ALLOW_HEADERS', '["*"]')
CORS_ALLOW_METHODS = _parse_list(_raw_methods, ["*"])
CORS_ALLOW_HEADERS = _parse_list(_raw_headers, ["*"])

# SAFETY CHECK: If credentials are on, forbid wildcard '*' origins
if CORS_ALLOW_CREDENTIALS and any(o == "*" for o in CORS_ORIGINS):
    # Fallback to localhost if misconfigured
    CORS_ORIGINS = _default_origins 

# --- 6. Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mediconnect")