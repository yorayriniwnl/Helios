"""Middleware to add security-related response headers.

Adds the following headers when appropriate:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security` (only set when request appears to be HTTPS)
"""
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, hsts_value: str = "max-age=63072000; includeSubDomains; preload"):
        super().__init__(app)
        self.hsts_value = hsts_value

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        try:
            # Prevent clickjacking
            response.headers.setdefault("X-Frame-Options", "DENY")
            # Prevent MIME sniffing
            response.headers.setdefault("X-Content-Type-Options", "nosniff")

            # Only set HSTS when request scheme indicates HTTPS. This avoids
            # setting HSTS for local development served over HTTP.
            scheme = getattr(request.url, "scheme", None) or request.headers.get("x-forwarded-proto")
            if scheme and scheme.lower() == "https":
                response.headers.setdefault("Strict-Transport-Security", self.hsts_value)
        except Exception:
            # best-effort, do not fail request on header errors
            pass
        return response
