"""
Rate Limiting Middleware
Protects API endpoints from abuse and DDoS attacks
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import logging
import asyncio

logger = logging.getLogger("mediconnect")


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self):
        # Store: {client_ip: [(timestamp, endpoint), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
        
        # Rate limits (requests per minute)
        self.limits = {
            "default": 60,  # 60 requests per minute for most endpoints
            "auth": 10,     # 10 requests per minute for auth endpoints
            "upload": 5,    # 5 requests per minute for file uploads
        }
        
        # Cleanup old entries every 5 minutes
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(minutes=5)
    
    async def is_rate_limited(self, client_ip: str, endpoint: str) -> Tuple[bool, int, int]:
        """
        Check if client has exceeded rate limit.
        
        Returns:
            (is_limited, current_count, limit)
        """
        async with self.lock:
            now = datetime.now()
            
            # Cleanup old entries if needed
            if now - self.last_cleanup > self.cleanup_interval:
                await self._cleanup_old_entries()
                self.last_cleanup = now
            
            # Determine rate limit for this endpoint
            limit = self._get_limit_for_endpoint(endpoint)
            
            # Get requests from last minute
            one_minute_ago = now - timedelta(minutes=1)
            recent_requests = [
                (ts, ep) for ts, ep in self.requests[client_ip]
                if ts > one_minute_ago
            ]
            
            # Update stored requests
            self.requests[client_ip] = recent_requests
            
            # Count requests to this endpoint
            endpoint_requests = [ep for ts, ep in recent_requests if ep == endpoint]
            current_count = len(endpoint_requests)
            
            # Check if limit exceeded
            if current_count >= limit:
                logger.warning(
                    f"Rate limit exceeded for {client_ip} on {endpoint}",
                    extra={
                        "client_ip": client_ip,
                        "endpoint": endpoint,
                        "current_count": current_count,
                        "limit": limit
                    }
                )
                return True, current_count, limit
            
            # Add current request
            self.requests[client_ip].append((now, endpoint))
            
            return False, current_count + 1, limit
    
    def _get_limit_for_endpoint(self, endpoint: str) -> int:
        """
        Determine rate limit based on endpoint pattern.
        """
        if "/auth/" in endpoint or "/login" in endpoint or "/register" in endpoint:
            return self.limits["auth"]
        elif "/upload" in endpoint or "/file" in endpoint:
            return self.limits["upload"]
        else:
            return self.limits["default"]
    
    async def _cleanup_old_entries(self):
        """
        Remove entries older than 2 minutes to prevent memory bloat.
        """
        now = datetime.now()
        two_minutes_ago = now - timedelta(minutes=2)
        
        for client_ip in list(self.requests.keys()):
            self.requests[client_ip] = [
                (ts, ep) for ts, ep in self.requests[client_ip]
                if ts > two_minutes_ago
            ]
            
            # Remove empty entries
            if not self.requests[client_ip]:
                del self.requests[client_ip]
        
        logger.info(f"Rate limiter cleanup completed. Active IPs: {len(self.requests)}")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting on API endpoints.
    """
    
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        
        # Endpoints to exclude from rate limiting
        self.excluded_paths = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Check rate limit before processing request.
        """
        # Skip rate limiting for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        endpoint = request.url.path
        
        # Check rate limit
        is_limited, current_count, limit = await self.rate_limiter.is_rate_limited(
            client_ip, endpoint
        )
        
        if is_limited:
            # Return 429 Too Many Requests
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {limit} requests per minute allowed.",
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(60)  # Seconds until reset
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(limit - current_count)
        response.headers["X-RateLimit-Reset"] = str(60)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request, considering proxies.
        """
        # Check X-Forwarded-For header (for proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"


# Global rate limiter instance
rate_limiter = RateLimiter()


def setup_rate_limiting(app):
    """
    Add rate limiting middleware to the application.
    """
    app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)
    logger.info("✅ Rate limiting middleware registered successfully")
