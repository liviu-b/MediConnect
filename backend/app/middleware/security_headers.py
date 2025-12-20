"""
Security Headers Middleware
Adds security headers to all responses
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("mediconnect")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.
    
    Best Practices:
    - Protect against XSS attacks
    - Prevent clickjacking
    - Enforce HTTPS
    - Control content type sniffing
    - Implement CSP (Content Security Policy)
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent XSS attacks
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enforce HTTPS (in production)
        # Uncomment for production with HTTPS
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        # Remove server header (security through obscurity)
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response
