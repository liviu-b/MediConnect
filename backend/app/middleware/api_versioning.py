"""
API Versioning Middleware
Supports multiple API versions for backward compatibility
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import re

logger = logging.getLogger("mediconnect")


class APIVersionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle API versioning.
    
    Supports versioning via:
    1. URL path: /api/v1/users, /api/v2/users
    2. Header: X-API-Version: 1.0
    3. Query parameter: ?api_version=1.0
    
    Best Practices:
    - Maintain backward compatibility
    - Deprecate old versions gradually
    - Document version changes
    - Use semantic versioning
    """
    
    SUPPORTED_VERSIONS = ["1.0", "2.0"]
    DEFAULT_VERSION = "2.0"
    DEPRECATED_VERSIONS = ["1.0"]
    
    async def dispatch(self, request: Request, call_next):
        # Extract version from URL path
        version = self._extract_version_from_path(request.url.path)
        
        # If not in path, check header
        if not version:
            version = request.headers.get("X-API-Version")
        
        # If not in header, check query parameter
        if not version:
            version = request.query_params.get("api_version")
        
        # Use default version if none specified
        if not version:
            version = self.DEFAULT_VERSION
        
        # Validate version
        if version not in self.SUPPORTED_VERSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported API version: {version}. "
                       f"Supported versions: {', '.join(self.SUPPORTED_VERSIONS)}"
            )
        
        # Warn about deprecated versions
        if version in self.DEPRECATED_VERSIONS:
            logger.warning(
                f"Client using deprecated API version {version}. "
                f"Path: {request.url.path}"
            )
        
        # Store version in request state
        request.state.api_version = version
        
        # Process request
        response = await call_next(request)
        
        # Add version to response headers
        response.headers["X-API-Version"] = version
        
        # Add deprecation warning if applicable
        if version in self.DEPRECATED_VERSIONS:
            response.headers["X-API-Deprecated"] = "true"
            response.headers["X-API-Sunset"] = "2026-12-31"  # Deprecation date
        
        return response
    
    def _extract_version_from_path(self, path: str) -> str:
        """
        Extract version from URL path.
        
        Examples:
            /api/v1/users -> "1.0"
            /api/v2/doctors -> "2.0"
        """
        match = re.search(r'/api/v(\d+(?:\.\d+)?)', path)
        if match:
            return match.group(1)
        return None


def get_api_version(request: Request) -> str:
    """
    Get API version from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        API version string
    """
    return getattr(request.state, 'api_version', APIVersionMiddleware.DEFAULT_VERSION)
