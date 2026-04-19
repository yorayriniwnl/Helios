"""Anomaly explanation engine for Helios.

Generates human-readable explanations and feature-importance hints for
detected anomalies. This module is intentionally lightweight and heuristic
— it produces interpretable templates suitable for UI tooltips or alert
messages in the dashboard.

Public API:
- `explain_anomalies(reading, anomalies, previous_reading=None, rule_score=None, ml_score=None, final_score=None, confidence=None)`
  returns a list of explanation dicts aligned with `anomalies`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence
from math import isfinite


TEMPLATES = {
    "high_power_spike": (
        "Sudden power spike detected: {prev_power} → {power} (ratio {ratio:.2f}).",
        "Spike detection"
    ),
    "high_power_absolute": (
        "Absolute high power observed: {power}W exceeds threshold.",
        "High absolute power"
    ),
    "abnormal_night_usage": (
        "Unusually high consumption at night: {power}W at {timestamp}.",
        "Night usage"
    ),
    "tamper_suspicion": (
        "Tamper indication present on the reading; sensor or meter tampering suspected.",
        "Tamper suspicion"
    ),
    "default": (
        "Anomaly of type {type} detected with score {score}.",
        "Anomaly"
    ),
}


def _get_field(obj: Any, *keys: str):
    for k in keys:
        if obj is None:
            return None
        if isinstance(obj, dict):
            v = obj.get(k)
        else:
            v = getattr(obj, k, None)
        if v is not None:
            return v
    return None


def _safe_float(v: Any) -> Optional[float]:
    try:
        f = float(v)
        if not isfinite(f):
            return None
        return f
    except Exception:
        return None


def _feature_hints_for_type(anom_type: str) -> Dict[str, float]:
    # Heuristic feature importance hints (0..1). These are suggestions
    # for UI to highlight which features likely contributed.
    if anom_type == "high_power_spike":
        return {"consumption_delta": 0.9, "rolling_mean": 0.6, "power_consumption": 0.6}
    if anom_type == "high_power_absolute":
        return {"power_consumption": 0.95, "voltage": 0.3, "current": 0.3}
    if anom_type == "abnormal_night_usage":
        return {"night_usage_ratio": 0.9, "power_consumption": 0.6}
    if anom_type in ("tamper_suspicion", "tamper", "tamper_flag"):
        return {"tamper": 1.0, "consumption_delta": 0.4}
    return {"power_consumption": 0.5}


def explain_anomalies(
    reading: Any,
    anomalies: Sequence[Dict[str, Any]],
    previous_reading: Optional[Any] = None,
    rule_score: Optional[float] = None,
    ml_score: Optional[float] = None,
    final_score: Optional[float] = None,
    confidence: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Return a list of explanation dicts aligned with `anomalies`.

    Each explanation dict contains:
    - `type`: anomaly type
    - `text`: human-readable explanation
    - `template`: short template name
    - `feature_hints`: dict mapping feature -> importance (0..1)
    """
    results: List[Dict[str, Any]] = []

    power = _safe_float(_get_field(reading, "power_consumption", "power"))
    prev_power = _safe_float(_get_field(previous_reading, "power_consumption", "power")) if previous_reading is not None else None
    timestamp = _get_field(reading, "timestamp", "created_at")

    for a in anomalies:
        atype = str(a.get("type", "unknown"))
        score = a.get("score", None)
        template, short = TEMPLATES.get(atype, TEMPLATES["default"])

        context = {"type": atype, "score": score, "power": power, "timestamp": timestamp, "prev_power": prev_power}
        # Compute ratio when possible
        try:
            if power is not None and prev_power is not None and prev_power != 0:
                context["ratio"] = float(power) / float(prev_power)
            else:
                context["ratio"] = 0.0
        except Exception:
            context["ratio"] = 0.0

        # Build a textual explanation from template
        try:
            text = template.format(
                power=f"{power:.2f}" if power is not None else "unknown",
                prev_power=f"{prev_power:.2f}" if prev_power is not None else "unknown",
                ratio=context.get("ratio", 0.0),
                timestamp=timestamp,
                type=atype,
                score=(f"{float(score):.3f}" if score is not None else "unknown"),
            )
        except Exception:
            text = a.get("explanation") or template

        feature_hints = _feature_hints_for_type(atype)

        # Add ML/rule context hints at top-level for UI
        meta: Dict[str, Any] = {"rule_score": rule_score, "ml_score": ml_score, "final_score": final_score, "confidence": confidence}

        results.append({
            "type": atype,
            "template": short,
            "text": text,
            "feature_hints": feature_hints,
            "meta": meta,
        })

    return results


__all__ = ["explain_anomalies"]
