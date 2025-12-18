from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .config import CORS_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS
import logging

logger = logging.getLogger("mediconnect")
from .routers import auth as auth_router
from .routers import clinics as clinics_router
from .routers import centers as centers_router
from .routers import doctors as doctors_router
from .routers import staff as staff_router
from .routers import services as services_router
from .routers import appointments as appointments_router
from .routers import reviews as reviews_router
from .routers import records as records_router
from .routers import migrate as migrate_router
from .routers import stats as stats_router
from .routers import organizations as organizations_router
from .routers import locations as locations_router
from .routers import access_requests as access_requests_router

app = FastAPI(title="MediConnect API", version="2.0.0")

# Add CORS middleware FIRST - this is critical for OPTIONS requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
    expose_headers=["*"],
    max_age=3600,
)

# Add request logging middleware AFTER CORS
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "MediConnect API",
        "version": "2.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Include routers
api_prefix = "/api"
app.include_router(auth_router.router, prefix=api_prefix)
app.include_router(clinics_router.router, prefix=api_prefix)
app.include_router(centers_router.router, prefix=api_prefix)
app.include_router(doctors_router.router, prefix=api_prefix)
app.include_router(staff_router.router, prefix=api_prefix)
app.include_router(services_router.router, prefix=api_prefix)
app.include_router(appointments_router.router, prefix=api_prefix)
app.include_router(reviews_router.router, prefix=api_prefix)
app.include_router(records_router.router, prefix=api_prefix)
app.include_router(migrate_router.router, prefix=api_prefix)
app.include_router(stats_router.router, prefix=api_prefix)
app.include_router(organizations_router.router, prefix=api_prefix)
app.include_router(locations_router.router, prefix=api_prefix)
app.include_router(access_requests_router.router, prefix=api_prefix)
