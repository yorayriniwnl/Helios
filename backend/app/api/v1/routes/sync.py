from typing import List, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

try:
    from backend.app.core.database import get_db
    from backend.app.services.alert_service import assign_alert as svc_assign_alert, resolve_alert as svc_resolve_alert
    from backend.app.dependencies.auth import get_current_user
except Exception:
    from ...core.database import get_db
    from ...services.alert_service import assign_alert as svc_assign_alert, resolve_alert as svc_resolve_alert
    from ...dependencies.auth import get_current_user

router = APIRouter(prefix="/sync", tags=["sync"])


class SyncItem(BaseModel):
    id: str
    method: str
    url: str
    data: Optional[dict] = None
    ts: Optional[str] = None


class SyncRequest(BaseModel):
    actions: List[SyncItem] = []


@router.post("/actions")
def sync_actions(payload: SyncRequest, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    """Apply a batch of offline actions sent from clients. Returns applied ids."""
    results = []
    applied_ids: List[str] = []

    import re

    for act in payload.actions:
        res = {"id": act.id, "status": "skipped", "error": None}
        try:
            path = act.url or ''

            m = re.match(r"^/alerts/(\d+)/assign/?$", path)
            if m and act.method.lower() == 'post':
                alert_id = int(m.group(1))
                user_id = (act.data or {}).get('user_id')
                if user_id is None:
                    raise ValueError('missing user_id')
                out = svc_assign_alert(db, alert_id=alert_id, user_id=int(user_id))
                if out is None:
                    raise Exception('assign failed')
                res['status'] = 'ok'
                res['result'] = {'id': getattr(out, 'id', None)}
                applied_ids.append(act.id)
                results.append(res)
                continue

            m = re.match(r"^/alerts/(\d+)/resolve/?$", path)
            if m and act.method.lower() in ('patch', 'put'):
                alert_id = int(m.group(1))
                notes = (act.data or {}).get('notes')
                out = svc_resolve_alert(db, alert_id=alert_id, notes=notes)
                if out is None:
                    raise Exception('resolve failed')
                res['status'] = 'ok'
                res['result'] = {'id': getattr(out, 'id', None)}
                applied_ids.append(act.id)
                results.append(res)
                continue

            # unsupported action -> return as skipped
            res['status'] = 'unsupported'
            results.append(res)
        except Exception as exc:
            res['status'] = 'error'
            res['error'] = str(exc)
            results.append(res)

    return {"applied": applied_ids, "results": results}
