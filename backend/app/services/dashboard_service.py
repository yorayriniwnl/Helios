"""Dashboard summary service.

Provides a simple summary used by dashboards or health endpoints.
"""
from typing import Dict
from sqlalchemy.orm import Session

try:
    from backend.app.repositories.meter_repository import count_meters as repo_count_meters
    from backend.app.repositories.reading_repository import count_readings as repo_count_readings
    from backend.app.repositories.alert_repository import count_alerts as repo_count_alerts
except Exception:
    from ..repositories.meter_repository import count_meters as repo_count_meters
    from ..repositories.reading_repository import count_readings as repo_count_readings
    from ..repositories.alert_repository import count_alerts as repo_count_alerts


def get_summary(db: Session) -> Dict[str, int]:
    """Return a summary with totals for meters, readings and alerts.

    Returns a dict with keys: `total_meters`, `total_readings`, `total_alerts`.
    """
    summary = {
        "total_meters": repo_count_meters(db),
        "total_readings": repo_count_readings(db),
        "total_alerts": repo_count_alerts(db),
    }

    # Add zone loss percentage (average across zones) if available
    try:
        from backend.app.services.zone_service import list_zones_overview as service_list_zones_overview
    except Exception:
        from ..services.zone_service import list_zones_overview as service_list_zones_overview

    try:
        zones = service_list_zones_overview(db, skip=0, limit=100)
        losses = [z.get("zone_loss_percentage", 0.0) for z in zones if z.get("zone_loss_percentage") is not None]
        if losses:
            avg_loss = sum(losses) / len(losses)
        else:
            avg_loss = 0.0
        summary["zone_loss_percentage"] = round(float(avg_loss), 3)
    except Exception:
        summary["zone_loss_percentage"] = 0.0

    # Add transformer health summary
    try:
        from backend.app.services.transformer_service import get_transformers_health_summary as service_transformer_health_summary
    except Exception:
        from ..services.transformer_service import get_transformers_health_summary as service_transformer_health_summary

    try:
        th = service_transformer_health_summary(db)
        summary["transformer_health"] = th
    except Exception:
        summary["transformer_health"] = {"average_health_score": 0.0, "counts": {"good": 0, "warning": 0, "critical": 0}, "total_transformers": 0}

    return summary


def get_recovery_metrics(db: Session, days: int = 30) -> Dict[str, object]:
    """Compute simple recovery-related metrics using existing alert and meter data.

    Returns a dict with:
    - total_recovered_value: float (INR estimate)
    - zone_recovery: list of {zone_id, zone_name, recovered_value}
    - inspector_stats: list of {user_id, name, assigned, resolved, success_rate, avg_time_to_close_minutes}
    - success_rate: overall resolved/total for the window
    - avg_time_to_close_minutes: overall average for resolved alerts
    - window_days: int

    Logic is intentionally simple and explainable: each resolved alert is given an
    estimated recovery minutes based on severity (critical/high/medium/low) multiplied
    by a confidence proxy (alert.score or 0.5), then converted to INR via a per-minute
    impact (default ₹5). Aggregations are computed per zone and per assigned inspector.
    """
    from datetime import datetime, timedelta, timezone
    try:
        from backend.app.models.alert import Alert
    except Exception:
        from ..models.alert import Alert

    try:
        from backend.app.models.meter import Meter
    except Exception:
        from ..models.meter import Meter

    try:
        from backend.app.models.zone import Zone
    except Exception:
        from ..models.zone import Zone

    try:
        from backend.app.models.user import User
    except Exception:
        from ..models.user import User

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=int(days or 30))

    # fetch resolved alerts within window
    try:
        alerts = db.query(Alert).filter(Alert.resolved_at.isnot(None)).filter(Alert.resolved_at >= since).all()
    except Exception:
        alerts = []

    # explainable base minutes per severity
    base_by_severity = {"critical": 120, "high": 60, "medium": 20, "low": 5}
    per_minute_inr = 5.0

    total_value = 0.0
    zone_map = {}  # zone_id -> {zone_name, value}
    inspector_map = {}  # user_id -> stats

    resolved_count = 0
    total_count = 0
    times_to_close = []

    for a in alerts:
        total_count += 1
        try:
            sev = (a.severity or "medium").lower()
            base = base_by_severity.get(sev, 10)
            score = float(a.score) if a.score is not None else 0.5
            # Confidence proxy clipped to [0.2,1.0] to avoid zeroing estimates
            conf = max(0.2, min(1.0, score))
            est_minutes = int(round(base * conf))
            est_value = float(est_minutes) * per_minute_inr
        except Exception:
            est_minutes = 0
            est_value = 0.0

        # aggregate totals
        total_value += est_value

        # zone aggregation via meter -> zone
        try:
            zone_id = None
            zone_name = None
            if a.meter_id:
                m = db.query(Meter).filter(Meter.id == a.meter_id).first()
                if m is not None:
                    zone_id = getattr(m, "zone_id", None)
                    if zone_id:
                        z = db.query(Zone).filter(Zone.id == zone_id).first()
                        zone_name = getattr(z, "name", None) if z is not None else None
            if zone_id is None:
                zone_id = 0
                zone_name = zone_name or "unknown"
            zm = zone_map.get(zone_id) or {"zone_id": zone_id, "zone_name": zone_name or "unknown", "recovered_value": 0.0}
            zm["recovered_value"] = float(zm.get("recovered_value", 0.0)) + est_value
            zone_map[zone_id] = zm
        except Exception:
            pass

        # inspector aggregation
        try:
            uid = a.assigned_to if getattr(a, "assigned_to", None) is not None else None
            if uid is not None:
                st = inspector_map.get(uid) or {"user_id": uid, "name": None, "assigned": 0, "resolved": 0, "total_time_min": 0.0}
                st["assigned"] = int(st.get("assigned", 0)) + 1
                # since we queried resolved alerts, count resolved
                st["resolved"] = int(st.get("resolved", 0)) + 1
                # compute time to close
                try:
                    if a.resolved_at and a.created_at:
                        delta = a.resolved_at - a.created_at
                        mins = max(0.0, delta.total_seconds() / 60.0)
                        st["total_time_min"] = float(st.get("total_time_min", 0.0)) + mins
                        times_to_close.append(mins)
                except Exception:
                    pass
                inspector_map[uid] = st
        except Exception:
            pass

        # overall resolved counts and times
        try:
            if a.resolved_at is not None:
                resolved_count += 1
                if a.created_at:
                    delta = a.resolved_at - a.created_at
                    times_to_close.append(max(0.0, delta.total_seconds() / 60.0))
        except Exception:
            pass

    # finalize inspector stats: fetch user names and compute averages
    inspector_stats = []
    for uid, st in inspector_map.items():
        try:
            u = db.query(User).filter(User.id == uid).first()
            name = getattr(u, "name", None) if u is not None else None
        except Exception:
            name = None
        assigned = int(st.get("assigned", 0))
        resolved = int(st.get("resolved", 0))
        success_rate = (resolved / assigned) if assigned > 0 else 0.0
        avg_time = (st.get("total_time_min", 0.0) / resolved) if resolved > 0 else 0.0
        inspector_stats.append({"user_id": uid, "name": name or "unknown", "assigned": assigned, "resolved": resolved, "success_rate": round(success_rate, 3), "avg_time_to_close_minutes": round(avg_time, 1)})

    # finalize zone list
    zone_recovery = [ {"zone_id": k, "zone_name": v.get("zone_name"), "recovered_value": round(float(v.get("recovered_value",0.0)),2)} for k,v in zone_map.items() ]

    # overall success rate and average time to close
    overall_success = (resolved_count / total_count) if total_count > 0 else 0.0
    overall_avg_time = (sum(times_to_close) / len(times_to_close)) if times_to_close else 0.0

    return {
        "total_recovered_value": round(float(total_value), 2),
        "zone_recovery": zone_recovery,
        "inspector_stats": inspector_stats,
        "success_rate": round(overall_success, 3),
        "avg_time_to_close_minutes": round(overall_avg_time, 1),
        "window_days": int(days or 30),
    }
