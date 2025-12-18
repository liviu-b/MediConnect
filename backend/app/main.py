from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .config import CORS_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS
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

app = FastAPI(title="MediConnect API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
    expose_headers=["*"],
)

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
