"""Service to detect and cache high-risk meters based on anomaly frequency.

This service uses the anomaly repository to compute meters that exceed a
configured anomaly count within a time window. Results are cached in Redis
when available; otherwise an in-memory cache is used for a short TTL.
"""
from __future__ import annotations

from typing import Any, Dict, List
import time

try:
    from backend.app.repositories.anomaly_repository import list_high_risk_meters as repo_list_high_risk_meters
except Exception:
    from ..repositories.anomaly_repository import list_high_risk_meters as repo_list_high_risk_meters

try:
    from backend.app.core.cache import get_cache, set_cache
except Exception:
    from ..core.cache import get_cache, set_cache

# Simple in-memory fallback cache
_local_cache: Dict[str, Dict[str, Any]] = {}


def _cache_key(window_hours: int, threshold: int) -> str:
    return f"high_risk_meters:{window_hours}:{threshold}"


def get_high_risk_meters(db, window_hours: int = 24, threshold: int = 5, limit: int = 100, ttl: int = 300, force_refresh: bool = False) -> List[Dict[str, Any]]:
    key = _cache_key(window_hours, threshold)

    if not force_refresh:
        # try redis cache first
        try:
            cached = get_cache(key)
            if cached:
                return cached
        except Exception:
            pass

        # try local in-memory cache
        entry = _local_cache.get(key)
        if entry and (time.time() - entry.get("ts", 0) < (ttl or 300)):
            return entry.get("value", [])

    # compute fresh
    try:
        results = repo_list_high_risk_meters(db, window_hours=window_hours, threshold=threshold, limit=limit)
    except Exception:
        results = []

    # write caches (best-effort)
    try:
        set_cache(key, results, ex=ttl)
    except Exception:
        pass

    _local_cache[key] = {"ts": time.time(), "value": results}
    return results


__all__ = ["get_high_risk_meters"]
