"""
Request ID Middleware
Adds unique request ID to each request for tracing
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import logging
from ..services.logging_config import request_id_var

logger = logging.getLogger("mediconnect")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request.
    
    Best Practices:
    - Enables request tracing across services
    - Helps with debugging and log correlation
    - Useful for distributed systems
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Store in context variable for logging
        request_id_var.set(request_id)
        
        # Add to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = request_id
        
        return response


def get_request_id(request: Request) -> str:
    """
    Get request ID from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Request ID string
    """
    return getattr(request.state, 'request_id', 'unknown')
