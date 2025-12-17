from pathlib import Path
import os
import logging
import json
from dotenv import load_dotenv

FRONTEND_URL = os.environ.get(
    "FRONTEND_URL",
    "http://localhost:3000",
)

# --- 1. Setup Environment ---
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

# --- 2. Database Config ---
MONGO_URL = os.environ.get("MONGO_URL")
if not MONGO_URL:
    raise RuntimeError("MONGO_URL environment variable is required")

DB_NAME = os.environ.get("DB_NAME", "mediconnect_db")

# --- 3. Email Config ---
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "MediConnect <onboarding@resend.dev>",
)

# --- 4. Helper Parsers ---
def parse_list(value):
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    s = str(value).strip()
    if s.startswith("["):
        return json.loads(s)
    return [v.strip() for v in s.split(",") if v.strip()]

def parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "yes", "y")

# --- 5. CORS Configuration (PRODUCTION SAFE) ---

# CORS ORIGINS (REQUIRED)
CORS_ORIGINS = parse_list(os.environ.get("CORS_ORIGINS"))
if not CORS_ORIGINS:
    raise RuntimeError("CORS_ORIGINS must be explicitly set")

# Credentials
CORS_ALLOW_CREDENTIALS = parse_bool(
    os.environ.get("CORS_ALLOW_CREDENTIALS", "true"),
    True,
)

# Methods (explicit)
CORS_ALLOW_METHODS = parse_list(
    os.environ.get("CORS_ALLOW_METHODS")
) or [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

# Headers (explicit)
CORS_ALLOW_HEADERS = parse_list(
    os.environ.get("CORS_ALLOW_HEADERS")
) or [
    "Authorization",
    "Content-Type",
    "Accept",
    "Origin",
    "X-Requested-With",
]

# 🚨 Hard safety rule
if CORS_ALLOW_CREDENTIALS and "*" in CORS_ORIGINS:
    raise RuntimeError(
        "CORS_ORIGINS cannot contain '*' when credentials are enabled"
    )

# --- 6. Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mediconnect")
