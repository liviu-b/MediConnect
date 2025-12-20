from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import CORS_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS
from .middleware import setup_error_handlers, RequestValidationMiddleware, setup_rate_limiting
from .middleware.rate_limiter import rate_limiter
from .redis_client import redis_client
import logging

logger = logging.getLogger("mediconnect")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting MediConnect API...")
    
    # Initialize Redis
    await redis_client.initialize()
    
    # Connect rate limiter to Redis
    rate_limiter.redis_client = redis_client
    
    logger.info("✅ MediConnect API started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down MediConnect API...")
    await redis_client.close()
    logger.info("✅ MediConnect API shutdown complete")
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
from .routers import invitations as invitations_router
from .routers import analytics as analytics_router
from .routers import health as health_router
from .middleware.request_id import RequestIDMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware
from .middleware.api_versioning import APIVersionMiddleware

app = FastAPI(
    title="MediConnect API",
    version="2.0.0",
    lifespan=lifespan,
    description="Modern healthcare appointment scheduling platform with best practices",
    docs_url="/docs",
    redoc_url="/redoc"
)

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

# Add best practices middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(APIVersionMiddleware)

# Include routers
api_prefix = "/api"
app.include_router(health_router.router)  # Health checks at root level
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
app.include_router(invitations_router.router, prefix=api_prefix)
app.include_router(analytics_router.router, prefix=api_prefix)

# Setup error handling and rate limiting middleware (after routers)
setup_error_handlers(app)
app.add_middleware(RequestValidationMiddleware)
setup_rate_limiting(app)

logger.info("✅ MediConnect API initialized successfully")
