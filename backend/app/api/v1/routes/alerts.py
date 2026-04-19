from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi import UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, conint

try:
    from backend.app.repositories.alert_repository import list_alerts as repo_list_alerts
    from backend.app.schemas.alert import AlertResponse
    from backend.app.core.database import get_db
    from backend.app.services.alert_service import assign_alert as svc_assign_alert, resolve_alert as svc_resolve_alert
    from backend.app.schemas.alert import PriorityAlertResponse
    from backend.app.services.priority_service import get_prioritized_alerts as svc_get_prioritized_alerts
    from backend.app.dependencies.auth import get_current_user
except Exception:
    from ...repositories.alert_repository import list_alerts as repo_list_alerts
    from ...schemas.alert import AlertResponse
    from ...core.database import get_db
    from ...services.alert_service import assign_alert as svc_assign_alert, resolve_alert as svc_resolve_alert
    from ...schemas.alert import PriorityAlertResponse
    from ...services.priority_service import get_prioritized_alerts as svc_get_prioritized_alerts
    from ...services.evidence_service import save_file_and_create_record as svc_save_evidence
    from ...repositories.evidence_repository import list_evidence_by_alert as repo_list_evidence
    from fastapi.responses import FileResponse


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertResponse])
def list_alerts_route(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Return recent alerts (newest first)."""
    try:
        from backend.app.services.decision_service import generate_decision
    except Exception:
        from ...services.decision_service import generate_decision

    rows = repo_list_alerts(db, skip=skip, limit=limit)
    out = []
    for r in rows:
        try:
            item = {
                "id": getattr(r, 'id', None),
                "meter_id": getattr(r, 'meter_id', None),
                "reading_id": getattr(r, 'reading_id', None),
                "type": getattr(r, 'type', None),
                "score": getattr(r, 'score', None),
                "explanation": getattr(r, 'explanation', None),
                "assigned_to": getattr(r, 'assigned_to', None),
                "status": getattr(r, 'status', None),
                "severity": getattr(r, 'severity', None),
                "responded_at": getattr(r, 'responded_at', None),
                "resolved_at": getattr(r, 'resolved_at', None),
                "sla_breached": getattr(r, 'sla_breached', None),
                "created_at": getattr(r, 'created_at', None),
            }
        except Exception:
            item = {k: getattr(r, k, None) for k in ("id", "meter_id", "reading_id", "type", "score", "explanation", "assigned_to", "status", "severity", "created_at")}

        try:
            item["decision"] = generate_decision(r)
        except Exception:
            item["decision"] = None

        out.append(item)

    return out


class AssignRequest(BaseModel):
    user_id: conint(gt=0)


class ResolveRequest(BaseModel):
    notes: Optional[str] = None


@router.post("/{alert_id}/assign", response_model=AlertResponse)
def assign_alert_route(alert_id: int, payload: AssignRequest, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    try:
        res = svc_assign_alert(db, alert_id=alert_id, user_id=payload.user_id)
    except Exception:
        res = None
    if res is None:
        raise HTTPException(status_code=404, detail="Alert not found or assign failed")
    return res


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert_route(alert_id: int, payload: ResolveRequest, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    try:
        res = svc_resolve_alert(db, alert_id=alert_id, notes=payload.notes)
    except Exception:
        res = None
    if res is None:
        raise HTTPException(status_code=404, detail="Alert not found or resolve failed")
    return res



@router.get("/priority", response_model=List[PriorityAlertResponse])
def list_priority_alerts_route(skip: int = 0, limit: int = 100, window_hours: int = 24, high_risk_threshold: int = 5, db: Session = Depends(get_db)):
    try:
        results = svc_get_prioritized_alerts(db, skip=skip, limit=limit, window_hours=window_hours, high_risk_threshold=high_risk_threshold)
        return results
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to compute prioritized alerts")



@router.post("/{alert_id}/evidence")
def upload_evidence_route(alert_id: int, file: UploadFile = File(...), gps_lat: Optional[float] = Form(None), gps_lon: Optional[float] = Form(None), evidence_ts: Optional[str] = Form(None), notes: Optional[str] = Form(None), before_after: Optional[str] = Form(None), db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    try:
        contents = file.file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read uploaded file")

    try:
        rec = svc_save_evidence(db, alert_id=alert_id, file_bytes=contents, filename=file.filename or 'upload', user_id=getattr(current_user, 'id', None), gps_lat=gps_lat, gps_lon=gps_lon, evidence_ts=evidence_ts, notes=notes, before_after=before_after)
        return {
            "id": getattr(rec, 'id', None),
            "alert_id": getattr(rec, 'alert_id', None),
            "file_url": f"{get_db.__self__}" if False else f"/api/v1/alerts/evidence/{getattr(rec,'id',None)}/file",
            "original_filename": getattr(rec, 'original_filename', None),
            "gps_lat": getattr(rec, 'gps_lat', None),
            "gps_lon": getattr(rec, 'gps_lon', None),
            "evidence_ts": getattr(rec, 'evidence_ts', None),
            "notes": getattr(rec, 'notes', None),
            "before_after": getattr(rec, 'before_after', None),
            "created_at": getattr(rec, 'created_at', None),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save evidence: {exc}")



@router.get("/{alert_id}/evidence")
def list_evidence_route(alert_id: int, db: Session = Depends(get_db)):
    try:
        rows = repo_list_evidence(db, alert_id=alert_id)
        out = []
        for r in rows:
            out.append({
                "id": getattr(r, 'id', None),
                "alert_id": getattr(r, 'alert_id', None),
                "original_filename": getattr(r, 'original_filename', None),
                "file_url": f"/api/v1/alerts/evidence/{getattr(r,'id',None)}/file",
                "gps_lat": getattr(r, 'gps_lat', None),
                "gps_lon": getattr(r, 'gps_lon', None),
                "evidence_ts": getattr(r, 'evidence_ts', None),
                "notes": getattr(r, 'notes', None),
                "before_after": getattr(r, 'before_after', None),
                "created_at": getattr(r, 'created_at', None),
            })
        return out
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to list evidence")


@router.get("/evidence/{evidence_id}/file")
def get_evidence_file(evidence_id: int, db: Session = Depends(get_db)):
    try:
        from backend.app.repositories.evidence_repository import get_evidence_by_id
        rec = get_evidence_by_id(db, evidence_id)
        if rec is None:
            raise HTTPException(status_code=404, detail="Not found")
        path = getattr(rec, 'file_path', None)
        if not path:
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(path, filename=getattr(rec, 'original_filename', 'evidence'))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to serve evidence file")
