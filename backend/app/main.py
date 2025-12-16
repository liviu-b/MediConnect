import os
import logging
from pathlib import Path
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="MediConnect API", version="2.0.0")

# CORS
frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (optional to avoid breaking during incremental refactor)

def _include_router_safely(module_path: str, router_attr: str = "router", prefix: str | None = None):
    try:
        # Import direct prin importlib
        import importlib
        mod = importlib.import_module(module_path)
        router = getattr(mod, router_attr)
        if prefix:
            app.include_router(router, prefix=prefix)
        else:
            app.include_router(router)
        logger.info(f"Included router: {module_path}")
    except Exception as e:
        logger.exception(f"Skipping router {module_path}: {e}")

# API routers expected under app.routers.* with their own prefixes
_include_router_safely('app.routers.auth')
_include_router_safely('app.routers.clinics')
_include_router_safely('app.routers.doctors')
_include_router_safely('app.routers.services')
_include_router_safely('app.routers.staff')
_include_router_safely('app.routers.appointments')
_include_router_safely('app.routers.stats')
_include_router_safely('app.routers.patients')
_include_router_safely('app.routers.medical')


@app.get("/health")
async def health_check():
    return {"status": "ok"}
