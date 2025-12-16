import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Helper Functions ---
def _parse_list(value, default=None):
    if value is None:
        return default or []
    if isinstance(value, list):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return [x.strip() for x in value.split(",") if x.strip()]

def _parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).lower() in ("true", "1", "t", "y", "yes")

# --- Environment Configuration ---
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# CORS Configuration
CORS_ORIGINS = _parse_list(
    os.getenv("CORS_ORIGINS"), 
    default=["http://localhost:3000", "http://127.0.0.1:3000"]
)
CORS_ALLOW_CREDENTIALS = _parse_bool(os.getenv("CORS_ALLOW_CREDENTIALS"), default=True)
CORS_ALLOW_METHODS = _parse_list(os.getenv("CORS_ALLOW_METHODS"), default=["*"])
CORS_ALLOW_HEADERS = _parse_list(os.getenv("CORS_ALLOW_HEADERS"), default=["*"])

# Safety Guard: Ensure wildcard origin is not used with credentials
if CORS_ALLOW_CREDENTIALS and "*" in CORS_ORIGINS:
    # Remove '*' and fallback to localhost if it was the only entry
    CORS_ORIGINS = [origin for origin in CORS_ORIGINS if origin != "*"]
    if not CORS_ORIGINS:
        CORS_ORIGINS = ["http://localhost:3000"]

# ... (Retain your existing Database, Secret Key, and Email configurations below)