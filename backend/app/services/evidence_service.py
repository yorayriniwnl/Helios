"""Evidence service: handle file writes and create evidence records."""
from typing import Optional
from sqlalchemy.orm import Session
from pathlib import Path

try:
    from backend.app.repositories.evidence_repository import create_evidence as repo_create_evidence
except Exception:
    from ..repositories.evidence_repository import create_evidence as repo_create_evidence


STORAGE_DIR = Path(__file__).resolve().parents[3] / "media" / "evidence"


def _ensure_storage():
    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def save_file_and_create_record(db: Session, alert_id: int, file_bytes: bytes, filename: str, user_id: Optional[int] = None, gps_lat: Optional[float] = None, gps_lon: Optional[float] = None, evidence_ts: Optional[str] = None, notes: Optional[str] = None, before_after: Optional[str] = None):
    """Save uploaded file to disk and create evidence DB record.

    Returns the created Evidence object (from repository).
    """
    _ensure_storage()
    # safe filename
    safe_name = filename.replace("\"", "").replace("/", "_").replace("..", "_")
    # add timestamp prefix to avoid collisions
    import time

    prefix = str(int(time.time()))
    out_name = f"{prefix}_{safe_name}"
    out_path = STORAGE_DIR / out_name
    try:
        with open(out_path, "wb") as f:
            f.write(file_bytes)
        file_path = str(out_path)
    except Exception:
        file_path = filename

    # create DB record
    rec = repo_create_evidence(db, alert_id=alert_id, user_id=user_id, file_path=file_path, original_filename=filename, gps_lat=gps_lat, gps_lon=gps_lon, evidence_ts=evidence_ts, notes=notes, before_after=before_after)
    return rec
