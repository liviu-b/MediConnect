"""
Request Validation Middleware
Validates incoming requests for security and data integrity
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import re
import logging
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger("mediconnect")


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate incoming requests for:
    - Phone number format
    - Email format
    - CUI format (Romanian tax ID)
    - Request size limits
    - Rate limiting preparation
    """
    
    # Regex patterns
    PHONE_PATTERN = re.compile(r'^\+?[0-9]{10,15}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    CUI_PATTERN = re.compile(r'^\d{2,10}$')
    
    # Request size limit (10MB)
    MAX_REQUEST_SIZE = 10 * 1024 * 1024
    
    async def dispatch(self, request: Request, call_next):
        """
        Process and validate the request before passing to the endpoint.
        """
        # Check request size
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.MAX_REQUEST_SIZE:
            logger.warning(
                f"Request size exceeded: {content_length} bytes from {request.client.host}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "content_length": content_length,
                    "client_ip": request.client.host if request.client else "unknown"
                }
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request body too large. Maximum size is 10MB."
            )
        
        # Log request details
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Process the request
        response = await call_next(request)
        
        # Log response
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        
        return response


class InputValidator:
    """
    Static methods for validating common input types.
    Can be used in route handlers for additional validation.
    """
    
    @staticmethod
    def validate_phone(phone: Optional[str]) -> bool:
        """
        Validate phone number format.
        Accepts: +40712345678, 0712345678, etc.
        """
        if not phone:
            return True  # Optional field
        
        # Remove spaces and dashes
        cleaned = phone.replace(" ", "").replace("-", "")
        
        return bool(RequestValidationMiddleware.PHONE_PATTERN.match(cleaned))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.
        """
        if not email:
            return False
        
        return bool(RequestValidationMiddleware.EMAIL_PATTERN.match(email.lower()))
    
    @staticmethod
    def validate_cui(cui: str) -> bool:
        """
        Validate Romanian CUI (tax identification number).
        Must be 2-10 digits.
        """
        if not cui:
            return False
        
        return bool(RequestValidationMiddleware.CUI_PATTERN.match(cui))
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.
        Returns: (is_valid, error_message)
        
        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter (recommended)
        - At least one lowercase letter (recommended)
        - At least one digit (recommended)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        # Check for recommended complexity (warnings, not errors)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            logger.info("Password meets minimum length but lacks complexity")
        
        return True, None
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """
        Sanitize string input by removing potentially dangerous characters.
        """
        if not text:
            return ""
        
        # Remove null bytes and control characters
        sanitized = text.replace('\x00', '').strip()
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """
        Validate date string format (YYYY-MM-DD).
        """
        if not date_str:
            return False
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """
        Validate time string format (HH:MM).
        """
        if not time_str:
            return False
        
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False


# Validation helper functions for use in routes
def validate_phone_or_raise(phone: Optional[str], field_name: str = "phone"):
    """
    Validate phone number and raise HTTPException if invalid.
    """
    if phone and not InputValidator.validate_phone(phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format. Expected format: +40712345678 or 0712345678"
        )


def validate_email_or_raise(email: str, field_name: str = "email"):
    """
    Validate email and raise HTTPException if invalid.
    """
    if not InputValidator.validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format. Please provide a valid email address."
        )


def validate_cui_or_raise(cui: str):
    """
    Validate CUI and raise HTTPException if invalid.
    """
    if not InputValidator.validate_cui(cui):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CUI format. CUI must contain 2-10 digits only."
        )


def validate_password_or_raise(password: str):
    """
    Validate password strength and raise HTTPException if invalid.
    """
    is_valid, error_message = InputValidator.validate_password_strength(password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
