"""Simple recommendation engine that maps alerts/anomalies to operator actions.

Rules are intentionally simple and explainable:
- tamper -> inspect meter
- voltage/spike/transformer -> check transformer
- repeated or high-score anomalies -> monitor zone

Keep logic lightweight and deterministic so frontend can display clear
operator guidance.
"""
from typing import Any, Dict

try:
    from backend.app.repositories.alert_repository import get_alert_by_id as repo_get_alert
    from backend.app.repositories.meter_repository import get_meter_by_id as repo_get_meter
except Exception:
    from ..repositories.alert_repository import get_alert_by_id as repo_get_alert
    from ..repositories.meter_repository import get_meter_by_id as repo_get_meter


def _safe_text(a: Any) -> str:
    if a is None:
        return ""
    if isinstance(a, str):
        return a.lower()
    try:
        return str(a).lower()
    except Exception:
        return ""


def get_recommendation_for_alert(db, alert_id: int) -> Dict[str, Any]:
    """Return a recommendation dict for the provided alert id."""
    a = repo_get_alert(db, alert_id)
    if a is None:
        return {
            "primary_action": "monitor_zone",
            "action_text": "Monitor the zone for further anomalies.",
            "reason": "Alert not found; default to monitoring.",
            "confidence": 0.45,
            "meter_id": None,
            "zone_id": None,
            "alternatives": ["monitor_zone"],
        }

    text = _safe_text(getattr(a, "explanation", None) or getattr(a, "type", None))
    score = float(getattr(a, "score", 0.0) or 0.0)
    meter_id = getattr(a, "meter_id", None)

    # Default recommendation
    primary = "monitor_zone"
    action_text = "Monitor the zone for further anomalies and increase sampling frequency."
    reason = "Pattern detected needs operator monitoring."
    confidence = max(0.0, min(1.0, score if score else 0.6))
    alternatives = []

    # Rule: tamper-related -> inspect meter
    if "tamper" in text or "tampering" in text or "tamper" == _safe_text(getattr(a, "type", None)):
        primary = "inspect_meter"
        action_text = "Inspect the meter on-site, verify seals and device integrity; consider replacing the meter if tampered."
        reason = "Device tampering indicators present in telemetry/explanation."
        confidence = max(confidence, 0.75)
        alternatives = ["monitor_zone", "inspect_meter"]

    # Rule: transformer/voltage/spike -> check transformer
    elif any(k in text for k in ("voltage", "spike", "overvoltage", "transformer")):
        primary = "check_transformer"
        action_text = "Schedule transformer inspection and check for overloads; consider temporary load redistribution."
        reason = "Voltage/transformer stress indicators observed." 
        confidence = max(confidence, 0.7)
        alternatives = ["inspect_meter", "monitor_zone"]

    # Rule: high score -> escalate to monitoring + meter inspection suggestion
    elif score >= 0.66:
        primary = "monitor_zone"
        action_text = "High anomaly score: monitor zone closely and inspect top offenders' meters."
        reason = "High anomaly score indicates concentrated abnormal behavior in area."
        confidence = max(confidence, 0.6)
        alternatives = ["inspect_meter", "check_transformer"]

    else:
        # low-medium score: monitor
        primary = "monitor_zone"
        action_text = "Monitor the zone and collect more samples; schedule remote diagnostics."
        reason = "Low/moderate anomaly score — requires observation and data collection."
        confidence = max(confidence, 0.45)
        alternatives = ["monitor_zone"]

    # Try to derive zone_id from meter if available
    zone_id = None
    try:
        if meter_id is not None:
            m = repo_get_meter(db, int(meter_id))
            zone_id = getattr(m, "zone_id", None) if m is not None else None
    except Exception:
        zone_id = None

    return {
        "primary_action": primary,
        "action_text": action_text,
        "reason": reason,
        "confidence": round(float(confidence), 3),
        "meter_id": meter_id,
        "zone_id": zone_id,
        "alternatives": alternatives,
    }


__all__ = ["get_recommendation_for_alert"]
