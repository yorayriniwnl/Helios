from typing import List, Optional
from sqlalchemy.orm import Session

try:
    from backend.app.models.zone import Zone
except Exception:
    from ..models.zone import Zone
try:
    from backend.app.models.zone_analytics import ZoneAnalytics
except Exception:
    from ..models.zone_analytics import ZoneAnalytics


def create_zone(db: Session, name: str, city: Optional[str] = None, state: Optional[str] = None) -> Zone:
    zone = Zone(
        name=name,
        city=city,
        state=state,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


def get_zone_by_id(db: Session, zone_id: int) -> Optional[Zone]:
    return db.query(Zone).filter(Zone.id == zone_id).first()


def list_zones(db: Session, skip: int = 0, limit: int = 100) -> List[Zone]:
    return db.query(Zone).offset(skip).limit(limit).all()


def create_zone_analytics(db: Session, zone_id: int, window_start, window_end, total_input: float, total_consumption: float, loss_percentage: float):
    try:
        za = ZoneAnalytics(
            zone_id=zone_id,
            window_start=window_start,
            window_end=window_end,
            total_input=total_input,
            total_consumption=total_consumption,
            loss_percentage=loss_percentage,
        )
        db.add(za)
        db.commit()
        db.refresh(za)
        return za
    except Exception:
        return None


def get_latest_zone_analytics_by_zone(db: Session, zone_id: int):
    try:
        return (
            db.query(ZoneAnalytics)
            .filter(ZoneAnalytics.zone_id == zone_id)
            .order_by(ZoneAnalytics.created_at.desc())
            .first()
        )
    except Exception:
        return None


def get_latest_zone_analytics_for_zones(db: Session, zone_ids: list) -> dict:
    """Return a dict mapping zone_id -> latest ZoneAnalytics row (object) for the given zone_ids.

    Uses a grouped subquery to locate the max(created_at) per zone and then joins back to retrieve the row.
    """
    try:
        if not zone_ids:
            return {}
        from sqlalchemy import func, and_

        subq = (
            db.query(ZoneAnalytics.zone_id.label("zone_id"), func.max(ZoneAnalytics.created_at).label("maxc"))
            .filter(ZoneAnalytics.zone_id.in_(zone_ids))
            .group_by(ZoneAnalytics.zone_id)
            .subquery()
        )

        rows = (
            db.query(ZoneAnalytics)
            .join(subq, and_(ZoneAnalytics.zone_id == subq.c.zone_id, ZoneAnalytics.created_at == subq.c.maxc))
            .all()
        )
        out = {}
        for r in rows:
            try:
                out[int(r.zone_id)] = r
            except Exception:
                continue
        return out
    except Exception:
        return {}
