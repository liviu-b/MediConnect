import os
from fastapi import Response

# ... existing imports ...

def set_auth_cookie(response: Response, session_token: str):
    """
    Sets the session cookie with appropriate security flags for dev/prod.
    """
    # Determine if we should use Secure flag (HTTPS only).
    # Default to False for local development ease, True for production.
    secure_cookie = os.getenv("COOKIE_SECURE", "false").strip().lower() in ("1", "true", "yes", "y")

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,       # JavaScript cannot access this cookie
        secure=secure_cookie, # False for HTTP (localhost), True for HTTPS
        samesite="none",     # Allows cookies to be sent in cross-site contexts
        path="/",
        max_age=7 * 24 * 60 * 60  # 7 days
    )