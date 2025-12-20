"""
Middleware package for MediConnect.
"""

from .permissions import (
    require_permission,
    require_role,
    require_location_access,
    block_admin_appointment_modification,
    check_appointment_access,
    check_location_access,
    check_organization_access,
    get_user_permissions,
    refresh_user_permissions
)

from .error_handler import ErrorHandler, setup_error_handlers

from .request_validation import (
    RequestValidationMiddleware,
    InputValidator,
    validate_phone_or_raise,
    validate_email_or_raise,
    validate_cui_or_raise,
    validate_password_or_raise
)

from .rate_limiter import (
    RateLimiter,
    RateLimitMiddleware,
    rate_limiter,
    setup_rate_limiting
)

from .request_id import (
    RequestIDMiddleware,
    get_request_id
)

from .security_headers import SecurityHeadersMiddleware

from .api_versioning import (
    APIVersionMiddleware,
    get_api_version
)

__all__ = [
    # Permissions
    'require_permission',
    'require_role',
    'require_location_access',
    'block_admin_appointment_modification',
    'check_appointment_access',
    'check_location_access',
    'check_organization_access',
    'get_user_permissions',
    'refresh_user_permissions',
    # Error Handling
    'ErrorHandler',
    'setup_error_handlers',
    # Request Validation
    'RequestValidationMiddleware',
    'InputValidator',
    'validate_phone_or_raise',
    'validate_email_or_raise',
    'validate_cui_or_raise',
    'validate_password_or_raise',
    # Rate Limiting
    'RateLimiter',
    'RateLimitMiddleware',
    'rate_limiter',
    'setup_rate_limiting',
    # Request ID
    'RequestIDMiddleware',
    'get_request_id',
    # Security Headers
    'SecurityHeadersMiddleware',
    # API Versioning
    'APIVersionMiddleware',
    'get_api_version'
]
