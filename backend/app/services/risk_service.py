"""Predictive risk service.

Provides simple, explainable meter- and zone-level risk scoring based on
recent anomaly events. The implementation is intentionally lightweight and
deterministic so results are interpretable during demos.

Functions
- `compute_meter_risk(db, meter_id, window_days=7)` -> dict
- `compute_zone_risk(db, zone_id, window_days=7)` -> dict
- `get_risk_summary(db, window_days=7, top_n=20)` -> dict with `meters` and `zones`
"""
from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy.orm import Session

try:
    from backend.app.repositories.anomaly_repository import (
        list_anomaly_events_by_meter as repo_list_anoms_by_meter,
        list_high_risk_meters as repo_list_high_risk_meters,
    )
    from backend.app.repositories.meter_repository import (
        get_meter_by_id as repo_get_meter_by_id,
        list_meters_by_zone as repo_list_meters_by_zone,
    )
    from backend.app.services.zone_service import list_zones as service_list_zones
except Exception:
    from ..repositories.anomaly_repository import (
        list_anomaly_events_by_meter as repo_list_anoms_by_meter,
        list_high_risk_meters as repo_list_high_risk_meters,
    )
    from ..repositories.meter_repository import (
        get_meter_by_id as repo_get_meter_by_id,
        list_meters_by_zone as repo_list_meters_by_zone,
    )
    from .zone_service import list_zones as service_list_zones


def _recency_weight(created_at: datetime, now: datetime, window_days: int) -> float:
    """Linear decay weight based on age in days. Keeps a small floor so
    very-old events still contribute slightly.
    """
    try:
        age_days = max(0.0, (now - created_at).total_seconds() / 86400.0)
        w = 1.0 - (age_days / max(1.0, float(window_days)))
        return max(0.05, min(1.0, w))
    except Exception:
        return 0.05


def compute_meter_risk(db: Session, meter_id: int, window_days: int = 7) -> Dict[str, Any]:
    """Compute a simple, explainable risk score for a meter.

    Strategy:
    - Fetch recent anomaly events for the meter.
    - Compute a recency-weighted average anomaly score.
    - Combine weighted score with a normalized frequency component.
    - Return human-friendly fields and contributing factors.
    """
    now = datetime.now(timezone.utc)

    try:
        events = repo_list_anoms_by_meter(db, meter_id, skip=0, limit=1000) or []
    except Exception:
        events = []

    # Filter/consider events and compute recency weights
    items = []
    for e in events:
        try:
            created = getattr(e, "created_at", None)
            if created is None:
                continue
            # allow events older than window but with low weight
            weight = _recency_weight(created, now, window_days)
            score = float(getattr(e, "score", 0.5) or 0.5)
            typ = getattr(e, "type", "unknown") or "unknown"
            items.append({"type": typ, "score": score, "created_at": created, "weight": weight})
        except Exception:
            continue

    count = len(items)

    # Weighted average score
    sum_w = sum(i["weight"] for i in items) if items else 0.0
    weighted_sum = sum(i["score"] * i["weight"] for i in items) if items else 0.0
    weighted_avg = (weighted_sum / sum_w) if sum_w > 0 else 0.0

    # Frequency normalized (cap at 10 events)
    freq_norm = min(1.0, count / 10.0)

    # Combine components (tunable) — favor per-event severity but include frequency
    final_score = max(0.0, min(1.0, 0.7 * weighted_avg + 0.3 * freq_norm))

    # Risk level
    if final_score >= 0.66:
        level = "high"
    elif final_score >= 0.33:
        level = "medium"
    else:
        level = "low"

    # Aggregate factor details by anomaly type
    factors: Dict[str, Dict[str, Any]] = {}
    for it in items:
        t = it["type"]
        f = factors.get(t) or {"type": t, "count": 0, "avg_score": 0.0, "max_recency_weight": 0.0}
        f["count"] += 1
        f["avg_score"] = ((f["avg_score"] * (f["count"] - 1)) + it["score"]) / f["count"]
        f["max_recency_weight"] = max(f["max_recency_weight"], it["weight"])
        factors[t] = f

    factor_list = sorted(list(factors.values()), key=lambda x: x["count"], reverse=True)

    # Top contributing types text
    top_types = [f["type"] for f in factor_list[:3]]

    # Meter metadata
    try:
        m = repo_get_meter_by_id(db, meter_id)
        meter_number = getattr(m, "meter_number", None)
        zone_id = getattr(m, "zone_id", None)
    except Exception:
        meter_number = None
        zone_id = None

    explanation = f"{count} anomaly events in last {window_days}d; top types: {', '.join(top_types) or 'none'}."

    return {
        "meter_id": int(meter_id),
        "meter_number": meter_number,
        "zone_id": zone_id,
        "risk_score": round(float(final_score), 3),
        "risk_level": level,
        "event_count": count,
        "factors": factor_list,
        "explanation": explanation,
    }


def compute_zone_risk(db: Session, zone_id: int, window_days: int = 7, top_meters: int = 5) -> Dict[str, Any]:
    """Compute a simple zone-level risk summary by aggregating meter risks.

    Uses the maximum meter risk as a conservative zone score and returns the
    top contributing meters for explainability.
    """
    try:
        meters = repo_list_meters_by_zone(db, zone_id, skip=0, limit=1000) or []
    except Exception:
        meters = []

    meter_scores = []
    for m in meters:
        try:
            mid = int(getattr(m, "id", 0) or 0)
            mr = compute_meter_risk(db, mid, window_days=window_days)
            meter_scores.append({"meter_id": mid, "meter_number": getattr(m, "meter_number", None), "risk_score": mr.get("risk_score", 0.0), "risk_level": mr.get("risk_level", "low"), "event_count": mr.get("event_count", 0)})
        except Exception:
            continue

    if not meter_scores:
        zone_score = 0.0
        zone_level = "low"
        top = []
    else:
        meter_scores.sort(key=lambda x: x["risk_score"], reverse=True)
        zone_score = float(meter_scores[0]["risk_score"])
        if zone_score >= 0.66:
            zone_level = "high"
        elif zone_score >= 0.33:
            zone_level = "medium"
        else:
            zone_level = "low"
        top = meter_scores[:top_meters]

    explanation = f"Zone risk {zone_level} (score={round(zone_score,3)}). Top meters: {[t.get('meter_number') for t in top]}"

    return {
        "zone_id": int(zone_id),
        "risk_score": round(zone_score, 3),
        "risk_level": zone_level,
        "top_meters": top,
        "explanation": explanation,
    }


def get_risk_summary(db: Session, window_days: int = 7, top_n: int = 20) -> Dict[str, Any]:
    """Return a summary of top high-risk meters and zone risk list.

    - `meters`: top `top_n` meters by recent anomaly counts (candidates) with computed risk
    - `zones`: all zones with simple aggregated risk
    """
    window_hours = int(window_days) * 24

    # candidate meters based on anomaly counts in the window (threshold=1 so we capture frequent anomalies)
    try:
        candidates = repo_list_high_risk_meters(db, window_hours=window_hours, threshold=1, limit=top_n) or []
        meter_ids = [int(x.get("meter_id")) for x in candidates if x.get("meter_id")]
    except Exception:
        meter_ids = []

    meters_out: List[Dict[str, Any]] = []
    for mid in meter_ids:
        try:
            mr = compute_meter_risk(db, mid, window_days=window_days)
            meters_out.append(mr)
        except Exception:
            continue

    # zones: use existing zone list and compute zone risk by aggregating meters
    zones_out: List[Dict[str, Any]] = []
    try:
        zones = service_list_zones(db, skip=0, limit=200) or []
    except Exception:
        zones = []

    for z in zones:
        try:
            zid = int(getattr(z, "id", 0) or 0)
            zr = compute_zone_risk(db, zid, window_days=window_days, top_meters=3)
            zr["zone_name"] = getattr(z, "name", None)
            zones_out.append(zr)
        except Exception:
            continue

    return {"meters": meters_out, "zones": zones_out, "window_days": int(window_days)}
