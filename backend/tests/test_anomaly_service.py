import pytest


def test_detect_anomalies_no_power(monkeypatch):
    from backend.app.services import anomaly_service

    # Ensure ML predictor not used in tests
    monkeypatch.setattr(anomaly_service, "_predict_anomaly", None)
    monkeypatch.setattr(anomaly_service, "_explain_anomalies", None)

    res = anomaly_service.detect_anomalies({})
    assert res["anomaly_score"] == 0.0
    assert res["severity"] == "low"
    assert res["anomalies"] == []


def test_detect_anomalies_spike_and_scores(monkeypatch):
    from backend.app.services import anomaly_service

    monkeypatch.setattr(anomaly_service, "_predict_anomaly", None)
    monkeypatch.setattr(anomaly_service, "_explain_anomalies", None)

    reading = {"power_consumption": 300, "timestamp": "2023-01-01T12:00:00Z"}
    previous = {"power_consumption": 100, "timestamp": "2023-01-01T11:59:00Z"}
    res = anomaly_service.detect_anomalies(reading, previous_reading=previous, recent_anomaly_count=2)

    assert isinstance(res.get("anomalies"), list)
    assert 0.0 <= float(res.get("anomaly_score", 0)) <= 1.0
    assert res.get("severity") in ("low", "medium", "high")
    assert "rule_score" in res and "ml_score" in res
