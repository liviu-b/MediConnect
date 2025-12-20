"""
Health Check Endpoints
Comprehensive health checks for monitoring and orchestration
"""

from fastapi import APIRouter, status
from datetime import datetime
import logging
from ..db import db
from ..redis_client import redis_client

logger = logging.getLogger("mediconnect")
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 if service is running.
    
    Used by:
    - Load balancers
    - Docker health checks
    - Kubernetes liveness probes
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MediConnect API"
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness check endpoint.
    Verifies all dependencies are available.
    
    Used by:
    - Kubernetes readiness probes
    - Load balancer health checks
    - Deployment verification
    """
    checks = {
        "database": False,
        "redis": False,
        "overall": False
    }
    
    # Check MongoDB
    try:
        await db.command('ping')
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis
    try:
        if redis_client.is_available():
            client = await redis_client.get_client()
            if client:
                await client.ping()
                checks["redis"] = True
        else:
            # Redis is optional, so we mark it as healthy if disabled
            checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    
    # Overall status
    checks["overall"] = checks["database"] and checks["redis"]
    
    if not checks["overall"]:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check endpoint.
    Returns 200 if application is alive (not deadlocked).
    
    Used by:
    - Kubernetes liveness probes
    - Container orchestration
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/startup", status_code=status.HTTP_200_OK)
async def startup_check():
    """
    Startup check endpoint.
    Verifies application has completed initialization.
    
    Used by:
    - Kubernetes startup probes
    - Deployment verification
    """
    checks = {
        "database": False,
        "redis": False
    }
    
    # Check MongoDB
    try:
        await db.command('ping')
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database startup check failed: {e}")
        return {
            "status": "starting",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }
    
    # Check Redis (optional)
    try:
        if redis_client.is_available():
            client = await redis_client.get_client()
            if client:
                await client.ping()
                checks["redis"] = True
        else:
            checks["redis"] = True
    except Exception as e:
        logger.warning(f"Redis startup check failed: {e}")
        checks["redis"] = False
    
    return {
        "status": "started",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }


@router.get("/metrics", status_code=status.HTTP_200_OK)
async def metrics():
    """
    Basic metrics endpoint.
    Returns application metrics for monitoring.
    
    Used by:
    - Prometheus
    - Monitoring systems
    - Performance tracking
    """
    metrics_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "N/A",  # Would need to track startup time
    }
    
    # Redis metrics
    if redis_client.is_available():
        try:
            client = await redis_client.get_client()
            if client:
                info = await client.info()
                metrics_data["redis"] = {
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "0B"),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                }
                
                # Calculate hit rate
                hits = info.get("keyspace_hits", 0)
                misses = info.get("keyspace_misses", 0)
                total = hits + misses
                if total > 0:
                    metrics_data["redis"]["hit_rate"] = f"{(hits / total * 100):.2f}%"
        except Exception as e:
            logger.error(f"Failed to get Redis metrics: {e}")
            metrics_data["redis"] = {"status": "unavailable"}
    
    # Database metrics
    try:
        server_status = await db.command('serverStatus')
        metrics_data["database"] = {
            "connections": server_status.get("connections", {}).get("current", 0),
            "operations": {
                "insert": server_status.get("opcounters", {}).get("insert", 0),
                "query": server_status.get("opcounters", {}).get("query", 0),
                "update": server_status.get("opcounters", {}).get("update", 0),
                "delete": server_status.get("opcounters", {}).get("delete", 0),
            }
        }
    except Exception as e:
        logger.error(f"Failed to get database metrics: {e}")
        metrics_data["database"] = {"status": "unavailable"}
    
    return metrics_data
