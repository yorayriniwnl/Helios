"""Simple, explainable decision engine for alerts.

Produces a small `decision` dict with keys:
- root_cause
- confidence
- recommended_action (id/title/description/one_click)
- estimated_recovery_minutes
- estimated_recovery_value_usd

Keep logic deterministic and auditable.
"""
from typing import Any, Dict

def _get_field(obj: Any, *keys: str):
    if obj is None:
        return None
    for k in keys:
        if isinstance(obj, dict):
            v = obj.get(k)
        else:
            v = getattr(obj, k, None)
        if v is not None:
            return v
    return None


def _severity_from_score(score: float) -> str:
    try:
        s = float(score or 0.0)
    except Exception:
        return 'medium'
    if s >= 0.66:
        return 'high'
    if s >= 0.33:
        return 'medium'
    return 'low'


def generate_decision(alert: Any) -> Dict[str, Any]:
    """Generate a small explainable decision dict from an `alert` object or dict.

    Accepts ORM object or dict-like with fields `type`, `score`, `severity`, `explanation`.
    """
    decision = {
        "root_cause": None,
        "confidence": 0.0,
        "recommended_action": None,
        "estimated_recovery_minutes": 0,
        "estimated_recovery_value_usd": 0.0,
    }

    try:
        a_type = _get_field(alert, "type", "alert_type") or "unknown"
        score = _get_field(alert, "score")
        try:
            score = float(score) if score is not None else 0.0
        except Exception:
            score = 0.0

        severity = _get_field(alert, "severity") or _severity_from_score(score)

        # map known alert types to root causes and actions
        mapping = {
            "high_power_spike": (
                "sudden power spike",
                {
                    "id": "inspect_spike",
                    "title": "Inspect recent load change",
                    "description": "Check recent load changes and schedule inspection; verify meter/readings.",
                    "one_click": False,
                },
            ),
            "high_power_absolute": (
                "sustained high consumption",
                {
                    "id": "inspect_high_power",
                    "title": "Investigate sustained high consumption",
                    "description": "Inspect device/process for runaway usage, consider maintenance or load shedding.",
                    "one_click": False,
                },
            ),
            "abnormal_night_usage": (
                "unexpected night usage",
                {
                    "id": "check_night_jobs",
                    "title": "Check scheduled/night jobs",
                    "description": "Verify scheduled tasks or unexpected background processes running at night.",
                    "one_click": False,
                },
            ),
            "tamper": (
                "possible tampering",
                {
                    "id": "isolate_device",
                    "title": "Isolate device and open incident",
                    "description": "Quarantine the device, collect evidence, and escalate to security.",
                    "one_click": False,
                },
            ),
            "tamper_suspicion": (
                "possible tampering",
                {
                    "id": "isolate_device",
                    "title": "Isolate device and open incident",
                    "description": "Quarantine the device, collect evidence, and escalate to security.",
                    "one_click": False,
                },
            ),
        }

        if a_type in mapping:
            root, action = mapping[a_type]
        else:
            expl = _get_field(alert, "explanation")
            root = a_type if a_type and a_type != "unknown" else (str(expl)[:120] if expl else "unknown")
            action = {
                "id": "inspect",
                "title": "Investigate alert",
                "description": "Open alert details and inspect evidence and logs.",
                "one_click": False,
            }

        # Confidence: based on score and severity; simple linear mapping
        if score and score > 0:
            confidence = max(0.0, min(1.0, 0.4 + 0.6 * float(score)))
        else:
            # fallback: higher for high severity
            confidence = 0.8 if severity == "high" else 0.6 if severity == "medium" else 0.4

        # Estimate recovery minutes (rule): base minutes per severity scaled by confidence
        base_by_sev = {"high": 60, "medium": 20, "low": 5}
        base_minutes = base_by_sev.get(severity, 10)
        est_minutes = int(round(base_minutes * confidence))

        # Per-minute value (USD) - simple default, allow reading-level overrides if present
        per_minute = _get_field(alert, "impact_per_minute") or 5.0
        try:
            per_minute = float(per_minute)
        except Exception:
            per_minute = 5.0

        est_value = round(float(est_minutes) * per_minute, 2)

        decision.update(
            {
                "root_cause": root,
                "confidence": round(float(confidence), 3),
                "recommended_action": action,
                "estimated_recovery_minutes": int(est_minutes),
                "estimated_recovery_value_usd": float(est_value),
            }
        )
    except Exception:
        # return defaults on failure
        pass

    return decision
