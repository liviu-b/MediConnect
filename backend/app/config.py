from pathlib import Path
import os
import logging
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / '.env'
load_dotenv(ENV_PATH)

MONGO_URL = os.environ.get('MONGO_URL', '')
if not MONGO_URL:
    raise ValueError("MONGO_URL environment variable is required")

DB_NAME = os.environ.get('DB_NAME', 'mediconnect_db')

RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'MediConnect <onboarding@resend.dev>')

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mediconnect")
