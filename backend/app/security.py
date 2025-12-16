import os
from fastapi import Response

# ... (keep your existing imports and other functions like hash_password, verify_password) ...

def set_auth_cookie(response: Response, session_token: str):
    """
    Sets the session cookie with appropriate security flags for dev/prod.
    """
    # Force secure=False if COOKIE_SECURE is explicitly 'false', otherwise default to True
    # For local development (HTTP), this MUST be False.
    is_secure = os.getenv("COOKIE_SECURE", "false").strip().lower() in ("true", "1", "yes")

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,       # JavaScript cannot access this cookie
        secure=is_secure,    # False for HTTP (localhost), True for HTTPS
        samesite="lax",      # 'lax' is usually sufficient for same-origin; use 'none' if cross-site needed
        path="/",
        max_age=7 * 24 * 60 * 60  # 7 days
    )