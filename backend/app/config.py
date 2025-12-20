from pathlib import Path
import os
import logging
import json
from dotenv import load_dotenv

FRONTEND_URL = os.environ.get(
    "FRONTEND_URL",
    "http://localhost:3000",
)

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

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

MONGO_URL = os.environ.get("MONGO_URL")
if not MONGO_URL:
    raise RuntimeError("MONGO_URL environment variable is required")

# Redis Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
REDIS_ENABLED = parse_bool(os.environ.get("REDIS_ENABLED", "true"), True)
REDIS_CACHE_TTL = int(os.environ.get("REDIS_CACHE_TTL", "300"))  # 5 minutes default
REDIS_MAX_CONNECTIONS = int(os.environ.get("REDIS_MAX_CONNECTIONS", "50"))

DB_NAME = os.environ.get("DB_NAME")
if not DB_NAME:
    try:
        from urllib.parse import urlparse
        parsed = urlparse(MONGO_URL)
        path = (parsed.path or "").lstrip("/")
        if path:
            DB_NAME = path.split("/")[0]
    except Exception:
        DB_NAME = None

if not DB_NAME:
    DB_NAME = "mediconnect_db"
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "MediConnect <onboarding@resend.dev>",
)

CORS_ORIGINS = parse_list(os.environ.get("CORS_ORIGINS"))
if not CORS_ORIGINS:
    raise RuntimeError("CORS_ORIGINS must be explicitly set")

CORS_ALLOW_CREDENTIALS = parse_bool(
    os.environ.get("CORS_ALLOW_CREDENTIALS", "true"),
    True,
)

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

CORS_ALLOW_HEADERS = parse_list(
    os.environ.get("CORS_ALLOW_HEADERS")
) or [
    "Authorization",
    "Content-Type",
    "Accept",
    "Origin",
    "X-Requested-With",
    "X-Location-ID",
]

if CORS_ALLOW_CREDENTIALS and "*" in CORS_ORIGINS:
    raise RuntimeError(
        "CORS_ORIGINS cannot contain '*' when credentials are enabled"
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mediconnect")
