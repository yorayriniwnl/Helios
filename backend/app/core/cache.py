"""Redis cache helper.

Provides a simple Redis client created from `REDIS_URL` in settings
and utility functions `set_cache` and `get_cache`.

This module is best-effort: if the `redis` package is not installed or
`REDIS_URL` is not configured, the functions will silently no-op and
return `None` / `False` as appropriate.
"""
from typing import Any, Optional
import json
import logging

try:
    from backend.app.core.config import settings
except Exception:
    from .config import settings

try:
    import redis
except Exception:
    redis = None

_logger = logging.getLogger(__name__)
_client: Optional[Any] = None


def _init_client() -> Optional[Any]:
    global _client
    if _client is not None:
        return _client
    if redis is None:
        _logger.info("redis library not installed; cache disabled")
        return None
    url = getattr(settings, "REDIS_URL", None)
    if not url:
        _logger.info("REDIS_URL not configured; cache disabled")
        return None
    try:
        # Use decode_responses so we get strings back instead of bytes
        _client = redis.Redis.from_url(url, decode_responses=True)
        # Optionally test the connection once (best-effort)
        try:
            _client.ping()
        except Exception:
            _logger.info("redis ping failed; client created but may be unreachable")
        return _client
    except Exception as exc:
        _logger.exception("Failed to create Redis client: %s", exc)
        _client = None
        return None


def set_cache(key: str, value: Any, ex: Optional[int] = None) -> bool:
    """Set a value in the cache.

    - `key`: cache key
    - `value`: JSON-serializable value (datetime will be stringified)
    - `ex`: optional expiry in seconds

    Returns True on success, False otherwise.
    """
    client = _init_client()
    if client is None:
        return False
    try:
        payload = json.dumps(value, default=str)
        if ex is not None:
            client.set(name=key, value=payload, ex=ex)
        else:
            client.set(name=key, value=payload)
        return True
    except Exception:
        _logger.exception("Failed to set cache key %s", key)
        return False


def get_cache(key: str) -> Optional[Any]:
    """Get a value from the cache.

    Returns the deserialized Python object, the raw string if JSON
    decoding fails, or `None` when not found / on error.
    """
    client = _init_client()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return raw
    except Exception:
        _logger.exception("Failed to get cache key %s", key)
        return None
