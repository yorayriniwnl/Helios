"""Zone service.

Lightweight service that delegates to the `zone_repository`.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

try:
    from backend.app.repositories.zone_repository import (
        create_zone as repo_create_zone,
        get_zone_by_id as repo_get_zone_by_id,
        list_zones as repo_list_zones,
    )
except Exception:
    from ..repositories.zone_repository import (
        create_zone as repo_create_zone,
        get_zone_by_id as repo_get_zone_by_id,
        list_zones as repo_list_zones,
    )
try:
    from backend.app.repositories.alert_repository import count_alerts_by_zone as repo_count_alerts_by_zone
except Exception:
    from ..repositories.alert_repository import count_alerts_by_zone as repo_count_alerts_by_zone
try:
    from backend.app.repositories.reading_repository import sum_power_by_meter_ids_since as repo_sum_power_by_meter_ids_since
except Exception:
    from ..repositories.reading_repository import sum_power_by_meter_ids_since as repo_sum_power_by_meter_ids_since

try:
    from backend.app.repositories.zone_repository import create_zone_analytics as repo_create_zone_analytics
except Exception:
    from ..repositories.zone_repository import create_zone_analytics as repo_create_zone_analytics

try:
    from backend.app.repositories.meter_repository import list_meters_by_zone as repo_list_meters_by_zone
except Exception:
    from ..repositories.meter_repository import list_meters_by_zone as repo_list_meters_by_zone


def create_zone(db: Session, name: str, city: Optional[str] = None, state: Optional[str] = None):
    return repo_create_zone(db, name=name, city=city, state=state)


def get_zone(db: Session, zone_id: int):
    return repo_get_zone_by_id(db, zone_id)


def list_zones(db: Session, skip: int = 0, limit: int = 100) -> List:
    return repo_list_zones(db, skip=skip, limit=limit)


def calculate_zone_risk(db: Session, zone_id: int, alert_count_override: int = None) -> str:
    """Calculate a simple risk level for the zone based on alert counts.

    Returns one of: "low", "medium", "high".
    Logic (simple):
      - 0 alerts -> low
      - 1-3 alerts -> medium
      - 4+ alerts -> high
    """
    try:
        if alert_count_override is not None:
            count = int(alert_count_override)
        else:
            count = repo_count_alerts_by_zone(db, zone_id)
    except Exception:
        count = 0

    if count <= 0:
        return "low"
    if 1 <= count <= 3:
        return "medium"
    return "high"


def estimate_zone_loss(db: Session, zone_id: int, window_hours: int = 24, store: bool = True):
    """Estimate energy loss percentage for a zone over the past `window_hours`.

    The function attempts to identify upstream (feeder) meters using simple
    heuristics (meter_number or household_name containing 'FEED', 'MAIN', or 'SUPPLY').
    If no feeder meters are found, the function falls back to returning 0.0
    and does not store analytics (unless forced).

    Returns the loss percentage as a float (0.0 - 100.0).
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=window_hours)

    try:
        meters = repo_list_meters_by_zone(db, zone_id=zone_id, skip=0, limit=1000)
    except Exception:
        meters = []

    meter_ids = [m.id for m in meters if getattr(m, "id", None) is not None]
    if not meter_ids:
        return 0.0

    # Heuristic: feeder meters contain keywords in meter_number or household_name
    feeder_keywords = ("FEED", "MAIN", "SUPPLY", "SUBSTATION")
    feeder_ids = []
    consumer_ids = []
    for m in meters:
        mn = (getattr(m, "meter_number", "") or "").upper()
        hn = (getattr(m, "household_name", "") or "").upper()
        if any(k in mn or k in hn for k in feeder_keywords):
            feeder_ids.append(m.id)
        else:
            consumer_ids.append(m.id)

    # If no feeder meters identified, we cannot compute input reliably
    if not feeder_ids:
        # Optionally attempt an alternate heuristic: treat the meter with the highest recent reading as supply
        try:
            sums = []
            for mid in meter_ids:
                s = repo_sum_power_by_meter_ids_since(db, [mid], cutoff)
                sums.append((mid, s))
            if sums:
                sums.sort(key=lambda x: x[1], reverse=True)
                feeder_ids = [sums[0][0]]
                consumer_ids = [m for m in meter_ids if m != feeder_ids[0]]
        except Exception:
            feeder_ids = []

    total_input = 0.0
    total_consumption = 0.0
    try:
        if feeder_ids:
            total_input = float(repo_sum_power_by_meter_ids_since(db, feeder_ids, cutoff) or 0.0)
        # sum consumers
        if consumer_ids:
            total_consumption = float(repo_sum_power_by_meter_ids_since(db, consumer_ids, cutoff) or 0.0)
        else:
            # If consumer_ids empty (all meters considered feeders), sum all as consumption
            total_consumption = float(repo_sum_power_by_meter_ids_since(db, meter_ids, cutoff) or 0.0)
    except Exception:
        total_input = 0.0
        total_consumption = 0.0

    loss_pct = 0.0
    if total_input and total_input > 0:
        loss_pct = max(0.0, min(100.0, (float(total_input) - float(total_consumption)) / float(total_input) * 100.0))

    # Store analytics
    if store:
        try:
            repo_create_zone_analytics(db, zone_id=zone_id, window_start=cutoff, window_end=now, total_input=total_input, total_consumption=total_consumption, loss_percentage=loss_pct)
        except Exception:
            pass

    return round(float(loss_pct), 3)


def list_zones_overview(db: Session, skip: int = 0, limit: int = 100):
    """Return zones with lightweight metrics for heatmap visualization.

    Each item includes: id, name, city, state, meter_count, alert_count, anomaly_count, anomaly_density, risk
    """
    zones = repo_list_zones(db, skip=skip, limit=limit)
    out = []

    zone_ids = [z.id for z in zones if getattr(z, "id", None) is not None]

    # Bulk fetch counts to avoid N+1 queries
    try:
        from backend.app.repositories.meter_repository import count_meters_grouped_by_zone as repo_count_meters_grouped
    except Exception:
        from ..repositories.meter_repository import count_meters_grouped_by_zone as repo_count_meters_grouped

    try:
        from backend.app.repositories.alert_repository import count_alerts_grouped_by_zone as repo_count_alerts_grouped
    except Exception:
        from ..repositories.alert_repository import count_alerts_grouped_by_zone as repo_count_alerts_grouped

    try:
        from backend.app.repositories.anomaly_repository import count_anomaly_events_grouped_by_zone as repo_count_anoms_grouped
    except Exception:
        from ..repositories.anomaly_repository import count_anomaly_events_grouped_by_zone as repo_count_anoms_grouped

    try:
        from backend.app.repositories.zone_repository import get_latest_zone_analytics_for_zones as repo_latest_zone_analytics
    except Exception:
        from ..repositories.zone_repository import get_latest_zone_analytics_for_zones as repo_latest_zone_analytics

    try:
        meter_counts = repo_count_meters_grouped(db, zone_ids)
    except Exception:
        meter_counts = {}
    try:
        alert_counts = repo_count_alerts_grouped(db, zone_ids)
    except Exception:
        alert_counts = {}
    try:
        anomaly_counts = repo_count_anoms_grouped(db, zone_ids)
    except Exception:
        anomaly_counts = {}
    try:
        latest_analytics = repo_latest_zone_analytics(db, zone_ids)
    except Exception:
        latest_analytics = {}

    for z in zones:
        try:
            zid = int(getattr(z, "id", 0) or 0)
            meter_count = int(meter_counts.get(zid, 0))
            alert_count = int(alert_counts.get(zid, 0))
            anomaly_count = int(anomaly_counts.get(zid, 0))
            density = float(anomaly_count) / max(1, meter_count) if meter_count else float(anomaly_count)
            risk = calculate_zone_risk(db, zid, alert_count_override=alert_count)
            za = latest_analytics.get(zid)
            zone_loss = round(float(za.loss_percentage), 3) if za and getattr(za, "loss_percentage", None) is not None else 0.0

            out.append({
                "id": zid,
                "name": z.name,
                "city": getattr(z, "city", None),
                "state": getattr(z, "state", None),
                "meter_count": meter_count,
                "alert_count": alert_count,
                "anomaly_count": anomaly_count,
                "anomaly_density": round(density, 3),
                "risk": risk,
                "zone_loss_percentage": zone_loss,
            })
        except Exception:
            continue

    return out
