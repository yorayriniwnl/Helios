"""Transformer service.

Provides simple status calculation for transformers.
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

try:
    from backend.app.models.transformer import Transformer
except Exception:
    from ..models.transformer import Transformer


def get_transformer_status(db: Session, transformer_id: int) -> Dict[str, Optional[float]]:
    """Return transformer status based on load percentage.

    Returns a dict with keys: `status` and `load_percent`.
    Status values: "ok", "warning", "critical", "not_found".

    Logic:
      - use `Transformer.load_percent` when available
      - if load_percent > 95 -> critical
      - elif load_percent > 80 -> warning
      - else -> ok
    """
    transformer = db.query(Transformer).filter(Transformer.id == transformer_id).first()
    if not transformer:
        return {"status": "not_found", "load_percent": None}

    # Calculate or read load percent (best-effort)
    try:
        lp_val = getattr(transformer, "load_percent", None)
        load_percent = float(lp_val) if lp_val is not None else 0.0
    except Exception:
        load_percent = 0.0

    if load_percent > 95.0:
        status = "critical"
    elif load_percent > 80.0:
        status = "warning"
    else:
        status = "ok"

    return {"status": status, "load_percent": load_percent}


def get_transformer_health(db: Session, transformer_id: int, window_hours: int = 24, anomaly_scale: int = 10) -> Dict[str, Optional[object]]:
    """Compute a transformer health score combining load %, anomaly frequency and voltage instability.

    Returns dict with keys: `health_score` (0..1), `status` (good/warning/critical),
    and component breakdown `{load_percent, load_score, anomaly_count, anomaly_score, voltage_instability, voltage_score}`.
    """
    transformer = db.query(Transformer).filter(Transformer.id == transformer_id).first()
    if not transformer:
        return {"health_score": None, "status": "not_found"}

    zone_id = getattr(transformer, "zone_id", None)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=window_hours)

    # load_percent: prefer stored value, else attempt to compute from zone analytics if available
    try:
        lp = getattr(transformer, "load_percent", None)
        load_percent = float(lp) if lp is not None else None
    except Exception:
        load_percent = None

    if load_percent is None:
        # try to use latest zone analytics if present
        try:
            from backend.app.repositories.zone_repository import get_latest_zone_analytics_by_zone as repo_get_latest_zone_analytics_by_zone
        except Exception:
            from ..repositories.zone_repository import get_latest_zone_analytics_by_zone as repo_get_latest_zone_analytics_by_zone
        try:
            za = repo_get_latest_zone_analytics_by_zone(db, zone_id) if zone_id is not None else None
            if za and getattr(za, "total_input", None) is not None and getattr(transformer, "capacity", None) is not None:
                total_input = float(getattr(za, "total_input", 0.0) or 0.0)
                cap = float(getattr(transformer, "capacity", 0.0) or 0.0)
                if cap > 0:
                    load_percent = min(100.0, (total_input / cap) * 100.0)
        except Exception:
            load_percent = None

    if load_percent is None:
        load_percent = 0.0

    # anomaly count within window for the zone
    try:
        from backend.app.repositories.anomaly_repository import count_anomaly_events_by_zone_since as repo_count_anomalies_since
    except Exception:
        from ..repositories.anomaly_repository import count_anomaly_events_by_zone_since as repo_count_anomalies_since

    try:
        anomaly_count = repo_count_anomalies_since(db, zone_id, cutoff) if zone_id is not None else 0
    except Exception:
        anomaly_count = 0

    # voltage instability across zone meters
    try:
        from backend.app.repositories.meter_repository import list_meters_by_zone as repo_list_meters_by_zone
    except Exception:
        from ..repositories.meter_repository import list_meters_by_zone as repo_list_meters_by_zone

    try:
        meters = repo_list_meters_by_zone(db, zone_id=zone_id, skip=0, limit=1000) if zone_id is not None else []
        meter_ids = [m.id for m in meters if getattr(m, "id", None) is not None]
    except Exception:
        meter_ids = []

    try:
        from backend.app.repositories.reading_repository import voltage_stats_by_meter_ids_since as repo_voltage_stats
    except Exception:
        from ..repositories.reading_repository import voltage_stats_by_meter_ids_since as repo_voltage_stats

    try:
        vstats = repo_voltage_stats(db, meter_ids, cutoff) if meter_ids else {"mean": 0.0, "stddev": 0.0, "count": 0, "out_of_range_frac": 0.0}
    except Exception:
        vstats = {"mean": 0.0, "stddev": 0.0, "count": 0, "out_of_range_frac": 0.0}

    out_frac = float(vstats.get("out_of_range_frac", 0.0) or 0.0)

    # Map components to 0..1 where higher is better
    load_score = max(0.0, min(1.0, 1.0 - (float(load_percent) / 100.0)))
    anomaly_score = 1.0 - min(1.0, float(anomaly_count) / float(anomaly_scale or 10))
    voltage_score = 1.0 - min(1.0, out_frac)

    # Weights
    LOAD_W = 0.5
    ANOM_W = 0.3
    VOLT_W = 0.2

    health_score = (LOAD_W * load_score) + (ANOM_W * anomaly_score) + (VOLT_W * voltage_score)
    health_score = max(0.0, min(1.0, health_score))

    if health_score >= 0.75:
        status = "good"
    elif health_score >= 0.4:
        status = "warning"
    else:
        status = "critical"

    return {
        "transformer_id": transformer_id,
        "health_score": round(float(health_score), 3),
        "status": status,
        "components": {
            "load_percent": round(float(load_percent), 3),
            "load_score": round(float(load_score), 3),
            "anomaly_count": int(anomaly_count),
            "anomaly_score": round(float(anomaly_score), 3),
            "voltage_out_of_range_frac": round(float(out_frac), 3),
            "voltage_score": round(float(voltage_score), 3),
        },
    }


def get_transformers_health_summary(db: Session, window_hours: int = 24):
    """Compute a lightweight summary across all transformers: avg health and status counts."""
    try:
        trs = db.query(Transformer).all()
    except Exception:
        trs = []

    if not trs:
        return {"average_health_score": 0.0, "counts": {"good": 0, "warning": 0, "critical": 0}, "total_transformers": 0}

    # Bulk fetch anomaly counts per zone (within window) to avoid per-transformer queries
    try:
        from datetime import datetime, timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        from backend.app.repositories.anomaly_repository import count_anomaly_events_grouped_by_zone as repo_count_anoms_grouped
    except Exception:
        from datetime import datetime, timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        from ..repositories.anomaly_repository import count_anomaly_events_grouped_by_zone as repo_count_anoms_grouped

    zone_ids = list({int(t.zone_id) for t in trs if getattr(t, "zone_id", None) is not None})
    try:
        anomaly_counts = repo_count_anoms_grouped(db, zone_ids, since=cutoff) if zone_ids else {}
    except Exception:
        anomaly_counts = {}

    stats = {"good": 0, "warning": 0, "critical": 0}
    scores = []

    for t in trs:
        try:
            load_percent = float(getattr(t, "load_percent", 0.0) or 0.0)
            zone_id = getattr(t, "zone_id", None)
            anomaly_count = int(anomaly_counts.get(int(zone_id), 0)) if zone_id is not None else 0

            # Component scores (approximate): higher is better
            load_score = max(0.0, min(1.0, 1.0 - (load_percent / 100.0)))
            anomaly_score = 1.0 - min(1.0, float(anomaly_count) / float(10))
            voltage_score = 1.0

            LOAD_W = 0.5
            ANOM_W = 0.3
            VOLT_W = 0.2

            health_score = (LOAD_W * load_score) + (ANOM_W * anomaly_score) + (VOLT_W * voltage_score)
            health_score = max(0.0, min(1.0, health_score))

            scores.append(health_score)
            if health_score >= 0.75:
                stats["good"] += 1
            elif health_score >= 0.4:
                stats["warning"] += 1
            else:
                stats["critical"] += 1
        except Exception:
            continue

    avg = float(sum(scores) / len(scores)) if scores else 0.0
    return {"average_health_score": round(avg, 3), "counts": stats, "total_transformers": len(trs)}
