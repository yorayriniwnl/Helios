"""Operator priority engine.

Ranks alerts for operators based on multiple signals:
- severity (string -> numeric)
- anomaly score (alert.score)
- repeated offender (high-risk meter counts)
- zone risk

Public API:
- `get_prioritized_alerts(db, skip=0, limit=100, window_hours=24, high_risk_threshold=5)`
  returns list of dicts with alert fields plus `priority_score` and `components`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

try:
    from backend.app.repositories.alert_repository import list_alerts as repo_list_alerts
    from backend.app.services.high_risk_service import get_high_risk_meters as svc_high_risk
    from backend.app.services.zone_service import list_zones_overview as svc_zones_overview
    from backend.app.repositories.meter_repository import get_meter_by_id as repo_get_meter_by_id
except Exception:
    from ..repositories.alert_repository import list_alerts as repo_list_alerts
    from ..services.high_risk_service import get_high_risk_meters as svc_high_risk
    from ..services.zone_service import list_zones_overview as svc_zones_overview
    from ..repositories.meter_repository import get_meter_by_id as repo_get_meter_by_id


def _severity_to_score(sev: Optional[str]) -> float:
    m = (sev or "medium").lower()
    return {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}.get(m, 0.5)


def _zone_risk_to_score(risk: Optional[str]) -> float:
    r = (risk or "low").lower()
    return {"high": 1.0, "medium": 0.5, "low": 0.0}.get(r, 0.0)


def get_prioritized_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    window_hours: int = 24,
    high_risk_threshold: int = 5,
) -> List[Dict[str, Any]]:
    """Return open alerts ranked by priority.

    The function loads recent alerts (via repo_list_alerts), computes helper
    signals (repeated offender counts and zone risk), and returns alerts with
    a `priority_score` in [0,1] and a `components` breakdown.
    """
    alerts = repo_list_alerts(db, skip=skip, limit=limit)

    # high-risk meters mapping
    try:
        hr = svc_high_risk(db, window_hours=window_hours, threshold=high_risk_threshold, limit=1000)
        hr_map = {int(x.get("meter_id")): int(x.get("count")) for x in (hr or [])}
    except Exception:
        hr_map = {}

    # zone risk mapping
    try:
        zones = svc_zones_overview(db, skip=0, limit=1000)
        zone_map = {int(z.get("id")): z.get("risk") for z in (zones or [])}
    except Exception:
        zone_map = {}

    prioritized: List[Dict[str, Any]] = []

    # Weights (sum to 1.0)
    W_SEV = 0.4
    W_ANOM = 0.35
    W_OFF = 0.15
    W_ZONE = 0.1

    for a in alerts:
        try:
            meter_id = getattr(a, "meter_id", None)
            # severity
            sev = getattr(a, "severity", None)
            sev_score = _severity_to_score(sev)

            # anomaly score stored on alert
            try:
                an = float(getattr(a, "score", 0.0) or 0.0)
                an_score = max(0.0, min(1.0, an))
            except Exception:
                an_score = 0.0

            # repeated offender
            count = int(hr_map.get(int(meter_id), 0)) if meter_id is not None else 0
            # normalize: count relative to threshold*2
            off_score = min(1.0, float(count) / max(1.0, high_risk_threshold * 2))

            # zone risk via meter -> zone
            try:
                zone_id = None
                if meter_id is not None:
                    m = repo_get_meter_by_id(db, int(meter_id))
                    zone_id = getattr(m, "zone_id", None) if m is not None else None
                zone_risk = zone_map.get(int(zone_id)) if zone_id is not None else None
            except Exception:
                zone_risk = None
            zone_score = _zone_risk_to_score(zone_risk)

            priority = (W_SEV * sev_score) + (W_ANOM * an_score) + (W_OFF * off_score) + (W_ZONE * zone_score)
            priority = max(0.0, min(1.0, priority))

            prioritized.append({
                "id": getattr(a, "id", None),
                "meter_id": meter_id,
                "type": getattr(a, "type", None),
                "score": getattr(a, "score", None),
                "severity": sev,
                "status": getattr(a, "status", None),
                "created_at": getattr(a, "created_at", None),
                "priority_score": round(float(priority), 3),
                "components": {
                    "severity_score": round(float(sev_score), 3),
                    "anomaly_score": round(float(an_score), 3),
                    "repeated_offender_score": round(float(off_score), 3),
                    "zone_score": round(float(zone_score), 3),
                },
            })
        except Exception:
            continue

    # sort descending by priority_score
    prioritized.sort(key=lambda x: x.get("priority_score", 0.0), reverse=True)
    return prioritized


__all__ = ["get_prioritized_alerts"]
