import os
import traceback
from datetime import datetime

# Ensure test environment before importing app/config
os.environ.setdefault("ENV", "development")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test_e2e_jwt_secret_1234567890")


def _to_dt(s):
    if isinstance(s, str):
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    return s


def test_end_to_end_flow():
    try:
        from backend.app.core.database import engine, Base, SessionLocal
        from backend.app.core.security import hash_password, verify_password, create_access_token
        from backend.app.repositories.user_repository import create_user
        from backend.app.repositories.meter_repository import create_meter
        from backend.app.services.reading_service import create_reading as svc_create_reading
        from backend.app.repositories.alert_repository import list_alerts

        # Create schema
        Base.metadata.create_all(engine)
        db = SessionLocal()

        # Create user and login
        user = create_user(db, name="E2E User", email="e2e@example.com", password_hash=hash_password("password123"))
        assert verify_password("password123", user.password_hash)
        token = create_access_token(user.id)

        # Create meter
        meter = create_meter(db, meter_number="M-E2E", household_name="E2E House", status="active")
        meter_id = getattr(meter, "id", None)

        # Ingest readings via service (this will run anomaly detection + create alerts)
        r1 = svc_create_reading(db, meter_id=meter_id, timestamp=_to_dt("2025-01-01T12:00:00Z"), voltage=230.0, current=1.0, power_consumption=100.0)
        r2 = svc_create_reading(db, meter_id=meter_id, timestamp=_to_dt("2025-01-01T12:01:00Z"), voltage=230.0, current=15.0, power_consumption=3500.0)

        alerts = list_alerts(db)
        found = any(getattr(a, "type", None) in ("high_power_absolute", "high_power_spike", "abnormal_night_usage") for a in alerts)
        assert found, "No anomaly alert found after ingesting high-power reading"
    except Exception:
        traceback.print_exc()
        raise
