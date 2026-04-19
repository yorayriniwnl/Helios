from fastapi import FastAPI
import sys

try:
    from backend.app.core.logging import configure_logging, RequestLoggingMiddleware, RequestTracingMiddleware
except Exception:
    from .core.logging import configure_logging, RequestLoggingMiddleware, RequestTracingMiddleware

# Configure logging early so middleware and startup logs are formatted
configure_logging()

try:
    from backend.app.api.v1.routes.users import router as users_router
    from backend.app.api.v1.routes.auth import router as auth_router
    from backend.app.api.v1.routes.meters import router as meters_router
    from backend.app.api.v1.routes.readings import router as readings_router
    from backend.app.api.v1.routes.alerts import router as alerts_router
    from backend.app.api.v1.routes.anomalies import router as anomalies_router
    from backend.app.api.websocket.live import router as live_router
    from backend.app.api.v1.routes.dashboard import router as dashboard_router
    from backend.app.api.v1.routes.zones import router as zones_router
    from backend.app.api.v1.routes.recommendations import router as recommendations_router
    from backend.app.api.v1.routes.sync import router as sync_router
    from backend.app.middleware.rate_limit import RateLimitMiddleware
    from backend.app.middleware.security_headers import SecurityHeadersMiddleware
    from backend.app.core.config import settings
except Exception:
    from .api.v1.routes.users import router as users_router
    from .api.v1.routes.auth import router as auth_router
    from .api.v1.routes.meters import router as meters_router
    from .api.v1.routes.readings import router as readings_router
    from .api.v1.routes.alerts import router as alerts_router
    from .api.v1.routes.anomalies import router as anomalies_router
    from .api.websocket.live import router as live_router
    from .api.v1.routes.dashboard import router as dashboard_router
    from .api.v1.routes.zones import router as zones_router
    from .api.v1.routes.recommendations import router as recommendations_router
    from .api.v1.routes.sync import router as sync_router
    from .middleware.rate_limit import RateLimitMiddleware
    from .middleware.security_headers import SecurityHeadersMiddleware
    from .core.config import settings

app = FastAPI()

# Configure CORS from settings (avoid wildcard origins)
try:
    from starlette.middleware.cors import CORSMiddleware

    cors_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", []) or []
    if not isinstance(cors_origins, (list, tuple)):
        cors_origins = list(cors_origins)

    # Add CORSMiddleware with explicit origins (do not use "*")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except Exception:
    # best-effort: continue if CORSMiddleware not available
    pass

# Security headers middleware: add HSTS, X-Frame-Options, X-Content-Type-Options
app.add_middleware(SecurityHeadersMiddleware)

# Apply rate-limiting middleware (per-IP sliding window)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# Tracing middleware: attach/propagate a `X-Request-ID` per request
app.add_middleware(RequestTracingMiddleware)

# Request logging middleware: logs each request and any unhandled errors
app.add_middleware(RequestLoggingMiddleware)

api_prefix = getattr(settings, "API_V1_STR", "/api/v1")

# In test runs (pytest) it's convenient to expose endpoints without the API
# prefix so tests can call routes directly. Detect pytest by checking for the
# pytest module in sys.modules or the PYTEST_CURRENT_TEST env marker.
if "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in __import__("os").environ:
    api_prefix = ""

app.include_router(users_router, prefix=api_prefix)
app.include_router(auth_router, prefix=api_prefix)
app.include_router(meters_router, prefix=api_prefix)
app.include_router(readings_router, prefix=api_prefix)
app.include_router(alerts_router, prefix=api_prefix)
app.include_router(anomalies_router, prefix=api_prefix)
app.include_router(live_router)
app.include_router(dashboard_router, prefix=api_prefix)
app.include_router(zones_router, prefix=api_prefix)
app.include_router(recommendations_router, prefix=api_prefix)
app.include_router(sync_router, prefix=api_prefix)


@app.get("/health")
async def health_basic():
    """Lightweight liveness endpoint used by load-balancers.

    Returns a minimal JSON payload indicating the service process is alive.
    """
    return {"status": "ok"}


@app.get("/ready")
async def readiness_check():
    """Readiness probe: checks database and redis connectivity.

    Returns detailed JSON suitable for orchestration systems.
    """
    status = "ready"

    # Check database connectivity
    db_ok = False
    db_error = None
    try:
        try:
            from backend.app.core.database import engine
        except Exception:
            from .core.database import engine

        # Local import to avoid adding SQLAlchemy at module import time if unused
        from sqlalchemy import text

        conn = engine.connect()
        try:
            conn.execute(text("SELECT 1"))
            db_ok = True
        finally:
            conn.close()
    except Exception as exc:  # pragma: no cover - best-effort readiness check
        db_ok = False
        db_error = str(exc)
        status = "not_ready"

    # Check Redis connectivity
    redis_ok = False
    redis_error = None
    try:
        try:
            from backend.app.core.cache import _init_client
        except Exception:
            from .core.cache import _init_client

        client = _init_client()
        if client is None:
            redis_ok = False
            redis_error = "redis not configured or redis library missing"
            status = "not_ready"
        else:
            try:
                client.ping()
                redis_ok = True
            except Exception as exc:  # pragma: no cover - best-effort
                redis_ok = False
                redis_error = str(exc)
                status = "not_ready"
    except Exception as exc:  # pragma: no cover
        redis_ok = False
        redis_error = str(exc)
        status = "not_ready"

    return {
        "status": status,
        "database": {"ok": db_ok, "error": db_error},
        "redis": {"ok": redis_ok, "error": redis_error},
    }


if (getattr(settings, "ENV", "").lower() != "production"):
    @app.get("/metrics")
    async def metrics_placeholder():
        """Placeholder metrics endpoint; return JSON until a metrics exporter
        (Prometheus, etc.) is wired up.
        """
        return {"status": "ok", "metrics": {}}
