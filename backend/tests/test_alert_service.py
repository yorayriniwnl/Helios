import json
from types import SimpleNamespace


def test_create_alert_calls_repo_and_broadcast(monkeypatch):
    from backend.app.services import alert_service

    dummy_alert = SimpleNamespace(
        id=123,
        meter_id=1,
        reading_id=2,
        type="high_power_spike",
        score=0.7,
        explanation="foo",
        created_at=None,
        updated_at=None,
    )

    # Patch repository creator to return our dummy
    monkeypatch.setattr(alert_service, "repo_create_alert", lambda db, **kwargs: dummy_alert)

    captured = {}

    def fake_broadcast(msg):
        captured["msg"] = msg

    monkeypatch.setattr(alert_service, "ws_broadcast_sync", fake_broadcast)
    monkeypatch.setattr(alert_service, "svc_log_action", lambda *a, **k: None)

    res = alert_service.create_alert(None, meter_id=1, reading_id=2, type="high_power_spike", score=0.7, explanation="foo")
    assert res is dummy_alert
    assert "msg" in captured
    # ensure payload looks like alert broadcast
    assert '"type": "alert"' in captured["msg"] or '"type":"alert"' in captured["msg"]
    # ensure id included
    assert '"id": 123' in captured["msg"]
