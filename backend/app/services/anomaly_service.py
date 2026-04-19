"""Advanced anomaly detection and scoring (rule-based).

Detects simple anomalies on individual readings (power spikes, absolute high
power, night usage) and computes a combined anomaly score and severity.

Scoring combines three components (rule-based):
- power deviation score (from detected power anomalies)
- frequency score (how many recent anomalies detected - optional input)
- tamper flag (if present on the reading)

The function returns a dict with keys:
- `anomalies`: list of detected anomaly dicts (`type`, `score`, `explanation`)
- `anomaly_score`: float in [0,1]
- `severity`: one of `low`, `medium`, `high`

Keep this rule-based and interpretable; weights and thresholds are tunable.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session

try:
    from backend.app.repositories.anomaly_repository import create_anomaly_event as repo_create_anomaly_event
except Exception:
    from ..repositories.anomaly_repository import create_anomaly_event as repo_create_anomaly_event
import json

try:
    from backend.app.services.websocket_service import broadcast_sync as ws_broadcast_sync
except Exception:
    from .websocket_service import broadcast_sync as ws_broadcast_sync


# ML predictor loader (best-effort). The project folder is named `ml-engine`,
# which is not a valid Python package name, so try a normal import first
# then fall back to loading the module directly from the file system.
try:
    from ml_engine.models.isolation_forest import predict_anomaly as _predict_anomaly
except Exception:
    _predict_anomaly = None
    try:
        import importlib.util
        from pathlib import Path

        _proj_root = Path(__file__).resolve().parents[3]
        _module_path = _proj_root / "ml-engine" / "models" / "isolation_forest.py"
        if _module_path.exists():
            _spec = importlib.util.spec_from_file_location("ml_isolation_forest", str(_module_path))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)  # type: ignore
            _predict_anomaly = getattr(_mod, "predict_anomaly", None)
    except Exception:
        _predict_anomaly = None


# Explanation engine loader (best-effort)
try:
    from ml_engine.inference.explain import explain_anomalies as _explain_anomalies
except Exception:
    _explain_anomalies = None
    try:
        import importlib.util
        from pathlib import Path

        _proj_root = Path(__file__).resolve().parents[3]
        _explain_path = _proj_root / "ml-engine" / "inference" / "explain.py"
        if _explain_path.exists():
            _spec_ex = importlib.util.spec_from_file_location("ml_explain", str(_explain_path))
            _mod_ex = importlib.util.module_from_spec(_spec_ex)
            _spec_ex.loader.exec_module(_mod_ex)  # type: ignore
            _explain_anomalies = getattr(_mod_ex, "explain_anomalies", None)
    except Exception:
        _explain_anomalies = None


# Tunable thresholds (kept conservative/simple)
SPIKE_FACTOR = 2.0  # power must be >= SPIKE_FACTOR * previous to count as a spike
ABSOLUTE_POWER_THRESHOLD = 3000.0  # watts, absolute high-power threshold
NIGHT_HOUR_START = 23
NIGHT_HOUR_END = 6
NIGHT_POWER_THRESHOLD = 500.0  # watts considered unusual at night

# Scoring weights (sum to 1.0)
POWER_WEIGHT = 0.6
FREQUENCY_WEIGHT = 0.3
TAMPER_WEIGHT = 0.1

# Hybrid weights for combining rule-based and ML scores (sum to 1.0)
HYBRID_RULE_WEIGHT = 0.6
HYBRID_ML_WEIGHT = 0.4


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


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        # support ISO format strings; handle trailing Z as UTC
        s = str(value)
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


def detect_anomalies(
    reading: Any,
    previous_reading: Optional[Any] = None,
    recent_anomaly_count: int = 0,
    db: Optional[Session] = None,
) -> Dict[str, Union[List[Dict[str, object]], float, str]]:
    """Detect anomalies and compute a combined anomaly score.

    Args:
        reading: dict or object containing at least `power_consumption` (or `power`) and `timestamp`.
        previous_reading: optional previous reading (dict or object) to detect spikes.
        recent_anomaly_count: optional integer count of recent anomalies for this meter (used to compute frequency score).

    Returns:
        dict with keys `anomalies` (list), `anomaly_score` (0..1 float), and `severity` (low/medium/high).
    """
    anomalies: List[Dict[str, object]] = []

    power = _get_field(reading, "power_consumption", "power")
    if power is None:
        return {"anomalies": anomalies, "anomaly_score": 0.0, "severity": "low"}
    try:
        power = float(power)
    except Exception:
        return {"anomalies": anomalies, "anomaly_score": 0.0, "severity": "low"}

    # Previous-power-based spike detection
    prev_power = _get_field(previous_reading, "power_consumption", "power") if previous_reading is not None else None
    if prev_power is not None:
        try:
            prev_power = float(prev_power)
        except Exception:
            prev_power = None

    if prev_power and prev_power > 0:
        ratio = power / prev_power
        if ratio >= SPIKE_FACTOR:
            # Score grows as ratio exceeds SPIKE_FACTOR; mapping to [0,1]
            score = min(1.0, (ratio - SPIKE_FACTOR) / SPIKE_FACTOR)
            explanation = f"Power spike: {prev_power:.2f}W → {power:.2f}W (ratio {ratio:.2f})."
            anomalies.append({"type": "high_power_spike", "score": round(score, 3), "explanation": explanation})

    # Absolute high-power anomaly
    if power >= ABSOLUTE_POWER_THRESHOLD:
        score = min(1.0, (power - ABSOLUTE_POWER_THRESHOLD) / ABSOLUTE_POWER_THRESHOLD)
        explanation = f"Absolute high power: {power:.2f}W >= {ABSOLUTE_POWER_THRESHOLD}W threshold."
        anomalies.append({"type": "high_power_absolute", "score": round(score, 3), "explanation": explanation})

    # Night usage anomaly
    ts = _parse_timestamp(_get_field(reading, "timestamp", "created_at"))
    if ts is not None:
        hour = ts.hour
        is_night = (hour >= NIGHT_HOUR_START) or (hour < NIGHT_HOUR_END)
        if is_night and power >= NIGHT_POWER_THRESHOLD:
            score = min(1.0, (power - NIGHT_POWER_THRESHOLD) / max(1.0, NIGHT_POWER_THRESHOLD))
            explanation = f"Abnormal night usage: {power:.2f}W at {ts.isoformat()}."
            anomalies.append({"type": "abnormal_night_usage", "score": round(score, 3), "explanation": explanation})

    # Tamper flag (if provided on the reading)
    tamper_flag = _get_field(reading, "tamper", "tamper_flag")
    tamper_score = 1.0 if bool(tamper_flag) else 0.0

    # Compute component scores
    # power_score: max score among detected power-related anomalies, else 0
    power_scores = [float(a.get("score", 0.0)) for a in anomalies if a.get("type") in ("high_power_spike", "high_power_absolute", "abnormal_night_usage")]
    power_score = max(power_scores) if power_scores else 0.0

    # frequency_score: map recent_anomaly_count into [0,1], cap at 5 recent anomalies
    try:
        freq = int(recent_anomaly_count or 0)
    except Exception:
        freq = 0
    frequency_score = min(1.0, freq / 5.0)

    # Combine scores with weights (rule-based baseline)
    anomaly_score = (POWER_WEIGHT * power_score) + (FREQUENCY_WEIGHT * frequency_score) + (TAMPER_WEIGHT * tamper_score)
    anomaly_score = max(0.0, min(1.0, anomaly_score))

    # Obtain ML model score (best-effort). If the ML predictor isn't available
    # or raises an error, fall back to the rule-based anomaly_score so behavior
    # remains unchanged.
    ml_score = anomaly_score
    if _predict_anomaly is not None:
        try:
            if isinstance(reading, dict):
                _reading_data = reading
            else:
                _reading_data = {
                    "power": _get_field(reading, "power", "power_consumption"),
                    "timestamp": _get_field(reading, "timestamp", "created_at"),
                    "tamper": _get_field(reading, "tamper", "tamper_flag"),
                }
            _ml_raw = _predict_anomaly(_reading_data)
            ml_score = float(_ml_raw)
            ml_score = max(0.0, min(1.0, ml_score))
        except Exception:
            ml_score = anomaly_score

    # Weighted hybrid combine: prefer rule-based when ML not available
    if _predict_anomaly is None:
        final_score = anomaly_score
    else:
        final_score = (HYBRID_RULE_WEIGHT * anomaly_score) + (HYBRID_ML_WEIGHT * ml_score)
    final_score = max(0.0, min(1.0, final_score))

    # Confidence calculation: agreement between rule and ML and anomaly presence
    try:
        if _predict_anomaly is not None:
            agreement = 1.0 - abs(anomaly_score - ml_score)
            anomaly_presence = min(1.0, len(anomalies) / 3.0)
            confidence = agreement * (0.5 + 0.5 * anomaly_presence)
        else:
            # Without ML, base confidence on presence of rule-detected anomalies
            anomaly_presence = min(1.0, len(anomalies) / 3.0)
            confidence = 0.5 + 0.5 * anomaly_presence
    except Exception:
        confidence = 0.0

    confidence = max(0.0, min(1.0, confidence))

    # Severity buckets based on final hybrid score
    if final_score >= 0.66:
        severity = "high"
    elif final_score >= 0.33:
        severity = "medium"
    else:
        severity = "low"

    # Persist anomaly events if DB session provided (best-effort)
    if db is not None and anomalies:
        try:
            # derive meter_id/reading_id from reading when possible
            meter_id = _get_field(reading, "meter_id", "meter")
            reading_id = _get_field(reading, "id", "reading_id")
            for a in anomalies:
                try:
                    event = repo_create_anomaly_event(
                        db,
                        meter_id=getattr(meter_id, "id", meter_id) if meter_id is not None else None,
                        reading_id=getattr(reading_id, "id", reading_id) if reading_id is not None else None,
                        type=a.get("type"),
                        score=a.get("score"),
                        explanation=a.get("explanation"),
                    )

                    # Broadcast anomaly event to connected websocket clients (best-effort)
                    try:
                        event_data = {
                            "id": getattr(event, "id", None),
                            "meter_id": getattr(event, "meter_id", None),
                            "reading_id": getattr(event, "reading_id", None),
                            "type": getattr(event, "type", None),
                            "score": getattr(event, "score", None),
                            "explanation": getattr(event, "explanation", None),
                            "created_at": getattr(event, "created_at", None).isoformat() if getattr(event, "created_at", None) is not None else None,
                            "severity": severity,
                        }
                        try:
                            ws_broadcast_sync(json.dumps({"type": "anomaly", "data": event_data}))
                        except Exception:
                            pass
                    except Exception:
                        pass

                except Exception:
                    # persist errors should not break scoring
                    pass
        except Exception:
            pass

    # Generate human-readable explanations (best-effort)
    explanations = []
    try:
        if _explain_anomalies is not None:
            explanations = _explain_anomalies(
                reading,
                anomalies,
                previous_reading=previous_reading if 'previous_reading' in locals() else None,
                rule_score=anomaly_score,
                ml_score=ml_score,
                final_score=final_score,
                confidence=confidence,
            )
    except Exception:
        explanations = []

    # Attach per-anomaly explanation details where available
    try:
        if explanations and len(explanations) >= 1:
            for idx, expl in enumerate(explanations):
                if idx < len(anomalies) and isinstance(expl, dict):
                    if "text" in expl:
                        anomalies[idx]["explanation"] = expl.get("text")
                    if "template" in expl:
                        anomalies[idx]["explanation_template"] = expl.get("template")
                    if "feature_hints" in expl:
                        anomalies[idx]["feature_hints"] = expl.get("feature_hints")
    except Exception:
        pass

    # Simple decision engine (explainable, rule-based)
    # Produces: root_cause, recommended_action, estimated_recovery_minutes, estimated_recovery_value_usd
    decision = {
        "root_cause": None,
        "recommended_action": None,
        "estimated_recovery_minutes": 0,
        "estimated_recovery_value_usd": 0.0,
    }

    try:
        if anomalies:
            # pick the highest-scoring anomaly as the primary signal
            top = max(anomalies, key=lambda x: float(x.get("score", 0.0)))
            t = top.get("type", "unknown")
            # map types to human-friendly root causes and actions
            mapping = {
                "high_power_spike": (
                    "sudden power spike",
                    {
                        "id": "inspect_spike",
                        "title": "Inspect recent load change",
                        "description": "Check recent deployments, scheduled jobs, or sudden load shifts; consider throttling or reverting recent changes.",
                        "one_click": False,
                    },
                ),
                "high_power_absolute": (
                    "sustained high power consumption",
                    {
                        "id": "inspect_high_power",
                        "title": "Investigate sustained high consumption",
                        "description": "Inspect device/process for runaway usage or misconfiguration; consider load shedding or maintenance.",
                        "one_click": False,
                    },
                ),
                "abnormal_night_usage": (
                    "unexpected night usage",
                    {
                        "id": "check_night_jobs",
                        "title": "Check scheduled/night jobs",
                        "description": "Verify if cron jobs, backups, or batch processes are running unexpectedly during night hours.",
                        "one_click": False,
                    },
                ),
                "tamper": (
                    "possible tampering",
                    {
                        "id": "isolate_device",
                        "title": "Isolate device and open incident",
                        "description": "Quarantine the device, collect evidence, and escalate to security for investigation.",
                        "one_click": False,
                    },
                ),
            }

            if t in mapping:
                root, action = mapping[t]
            else:
                # fallback when type is unknown: summarize by explanation text
                root = top.get("type") or (top.get("explanation") and str(top.get("explanation"))[:80]) or "unknown cause"
                action = {
                    "id": "inspect",
                    "title": "Investigate alert",
                    "description": "Open the alert details and inspect attached evidence and logs.",
                    "one_click": False,
                }

            decision["root_cause"] = root
            decision["recommended_action"] = action

            # Estimate recovery value (explainable rule): base minutes by severity
            try:
                base_by_severity = {"high": 60, "medium": 20, "low": 5}
                base_minutes = base_by_severity.get(severity, 10)
                est_minutes = int(round(base_minutes * confidence))
                # per-minute impact (USD) - allow override via reading context
                per_minute = float(_get_field(reading, "impact_per_minute") or 5.0)
                est_value = est_minutes * per_minute
            except Exception:
                est_minutes = 0
                est_value = 0.0

            decision["estimated_recovery_minutes"] = int(est_minutes)
            decision["estimated_recovery_value_usd"] = round(float(est_value), 2)
    except Exception:
        # keep decision defaults on error
        pass

    # Return a unified anomaly response with both components, final score, confidence, explanations and decision
    return {
        "anomalies": anomalies,
        "rule_score": round(anomaly_score, 3),
        "ml_score": round(ml_score, 3),
        "anomaly_score": round(final_score, 3),
        "confidence": round(confidence, 3),
        "severity": severity,
        "explanations": explanations,
        "decision": decision,
    }
