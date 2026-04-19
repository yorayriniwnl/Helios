from typing import Optional
from sqlalchemy.orm import Session

try:
    from backend.app.models.anomaly_event import AnomalyEvent
except Exception:
    from ..models.anomaly_event import AnomalyEvent


def create_anomaly_event(db: Session, meter_id: Optional[int], reading_id: Optional[int], type: str, score: Optional[float], explanation: Optional[str]) -> AnomalyEvent:
    event = AnomalyEvent(
        meter_id=meter_id,
        reading_id=reading_id,
        type=type,
        score=score,
        explanation=explanation,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_anomaly_events(db: Session, skip: int = 0, limit: int = 100):
    """Return recent anomaly events ordered by newest first."""
    try:
        return db.query(AnomalyEvent).order_by(AnomalyEvent.created_at.desc()).offset(skip).limit(limit).all()
    except Exception:
        return []


def list_anomaly_events_by_meter(db: Session, meter_id: int, skip: int = 0, limit: int = 100):
    """Return recent anomaly events for a specific meter, newest first."""
    try:
        return (
            db.query(AnomalyEvent)
            .filter(AnomalyEvent.meter_id == meter_id)
            .order_by(AnomalyEvent.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    except Exception:
        return []


def count_anomaly_events_by_zone(db: Session, zone_id: int) -> int:
    """Count anomaly events for all meters in the given zone."""
    try:
        # Join AnomalyEvent -> Meter -> filter by Meter.zone_id
        from sqlalchemy import func
        try:
            from backend.app.models.meter import Meter
        except Exception:
            from ..models.meter import Meter

        return int(
            db.query(func.count(AnomalyEvent.id))
            .join(Meter, AnomalyEvent.meter_id == Meter.id)
            .filter(Meter.zone_id == zone_id)
            .scalar()
            or 0
        )
    except Exception:
        return 0


def count_anomaly_events_by_zone_since(db: Session, zone_id: int, since) -> int:
    """Count anomaly events for all meters in the given zone since `since` datetime."""
    try:
        from sqlalchemy import func
        try:
            from backend.app.models.meter import Meter
        except Exception:
            from ..models.meter import Meter

        return int(
            db.query(func.count(AnomalyEvent.id))
            .join(Meter, AnomalyEvent.meter_id == Meter.id)
            .filter(Meter.zone_id == zone_id)
            .filter(AnomalyEvent.created_at >= since)
            .scalar()
            or 0
        )
    except Exception:
        return 0


    def count_anomaly_events_grouped_by_zone(db: Session, zone_ids: list, since=None) -> dict:
        """Return a dict mapping zone_id -> anomaly_count for the provided zone_ids.

        If `since` is provided, only count events on/after that timestamp.
        """
        try:
            if not zone_ids:
                return {}
            from sqlalchemy import func
            try:
                from backend.app.models.meter import Meter
            except Exception:
                from ..models.meter import Meter

            q = db.query(Meter.zone_id, func.count(AnomalyEvent.id).label("cnt")).join(AnomalyEvent, AnomalyEvent.meter_id == Meter.id).filter(Meter.zone_id.in_(zone_ids))
            if since is not None:
                q = q.filter(AnomalyEvent.created_at >= since)
            rows = q.group_by(Meter.zone_id).all()
            return {int(r[0]): int(r[1]) for r in rows}
        except Exception:
            return {}


def list_high_risk_meters(db: Session, window_hours: int = 24, threshold: int = 5, limit: int = 100):
    """Return meters with anomaly counts >= threshold within the given time window.

    Returns a list of dicts: {"meter_id": int, "count": int}
    """
    try:
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import func

        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)

        rows = (
            db.query(AnomalyEvent.meter_id, func.count(AnomalyEvent.id).label("cnt"))
            .filter(AnomalyEvent.meter_id.isnot(None))
            .filter(AnomalyEvent.created_at >= cutoff)
            .group_by(AnomalyEvent.meter_id)
            .having(func.count(AnomalyEvent.id) >= threshold)
            .order_by(func.count(AnomalyEvent.id).desc())
            .limit(limit)
            .all()
        )

        result = []
        for r in rows:
            # SQLAlchemy returns a tuple-like row; label accessible by index or attr
            try:
                meter_id = int(r[0])
                cnt = int(r[1])
            except Exception:
                # fallback when access by attr
                meter_id = int(getattr(r, "meter_id", 0) or 0)
                cnt = int(getattr(r, "cnt", 0) or 0)
            result.append({"meter_id": meter_id, "count": cnt})
        return result
    except Exception:
        return []
