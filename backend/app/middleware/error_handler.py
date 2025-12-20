"""
Error Handler Middleware
Comprehensive error handling and logging for the application
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import logging
import traceback
from datetime import datetime, timezone
from typing import Union

logger = logging.getLogger("mediconnect")


class ErrorHandler:
    """
    Centralized error handling for the application.
    Provides consistent error responses and comprehensive logging.
    """
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """
        Handle HTTP exceptions with proper logging.
        """
        error_id = f"ERR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        # Log the error
        logger.error(
            f"HTTP Exception [{error_id}]: {exc.status_code} - {exc.detail}",
            extra={
                "error_id": error_id,
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "detail": exc.detail
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "id": error_id,
                    "type": "http_error",
                    "status_code": exc.status_code,
                    "message": exc.detail,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    
    @staticmethod
    async def validation_exception_handler(request: Request, exc: Union[RequestValidationError, ValidationError]) -> JSONResponse:
        """
        Handle validation errors with detailed field-level information.
        """
        error_id = f"VAL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        # Extract validation errors
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        # Log the validation error
        logger.warning(
            f"Validation Error [{error_id}]: {len(errors)} field(s) failed validation",
            extra={
                "error_id": error_id,
                "path": request.url.path,
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "validation_errors": errors
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "id": error_id,
                    "type": "validation_error",
                    "status_code": 422,
                    "message": "Request validation failed",
                    "fields": errors,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    
    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle unexpected exceptions with full stack trace logging.
        """
        error_id = f"SYS-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        # Get full stack trace
        stack_trace = traceback.format_exc()
        
        # Log the error with full details
        logger.critical(
            f"Unhandled Exception [{error_id}]: {type(exc).__name__} - {str(exc)}",
            extra={
                "error_id": error_id,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "path": request.url.path,
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "stack_trace": stack_trace
            },
            exc_info=True
        )
        
        # Don't expose internal errors to clients in production
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "id": error_id,
                    "type": "internal_error",
                    "status_code": 500,
                    "message": "An internal server error occurred. Please contact support with error ID.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        )


def setup_error_handlers(app):
    """
    Register all error handlers with the FastAPI application.
    """
    app.add_exception_handler(StarletteHTTPException, ErrorHandler.http_exception_handler)
    app.add_exception_handler(RequestValidationError, ErrorHandler.validation_exception_handler)
    app.add_exception_handler(ValidationError, ErrorHandler.validation_exception_handler)
    app.add_exception_handler(Exception, ErrorHandler.general_exception_handler)
    
    logger.info("✅ Error handlers registered successfully")
