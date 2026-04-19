"""Inference entrypoint for Helios ML engine.

Dispatches to the best available model for a given reading:
  1. IsolationForest (sklearn) — primary model; loaded from saved_models/
  2. Rule-based fallback — always available even with no trained model

Public API
----------
predict(features) -> float
    Returns an anomaly score in [0, 1]. Higher means more anomalous.

predict_anomaly(reading, model_path=None) -> float
    Compatibility alias used by anomaly_service.py.

predict_batch(records) -> List[float]
    Scores a list of reading dicts/objects in one call.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Lazy loader — IsolationForest model
# ---------------------------------------------------------------------------

_iso_model = None
_iso_loaded: bool = False


def _load_iso():
    global _iso_model, _iso_loaded
    if _iso_loaded:
        return _iso_model
    _iso_loaded = True
    try:
        import joblib  # type: ignore
        candidate = ROOT / "saved_models" / "isolation_forest.joblib"
        if candidate.exists():
            _iso_model = joblib.load(str(candidate))
    except Exception:
        _iso_model = None
    return _iso_model


# ---------------------------------------------------------------------------
# Feature extraction helpers
# ---------------------------------------------------------------------------

def _get(obj: Any, *keys: str) -> Optional[Any]:
    """Get first non-None value from obj (dict or object) for given keys."""
    for k in keys:
        if obj is None:
            return None
        v = obj.get(k) if isinstance(obj, dict) else getattr(obj, k, None)
        if v is not None:
            return v
    return None


def _to_feature_vector(reading: Any) -> List[Optional[float]]:
    """Extract [power, voltage, current, power_factor] from a reading."""
    power   = _get(reading, "power_consumption", "power")
    voltage = _get(reading, "voltage")
    current = _get(reading, "current")

    try:
        power   = float(power)   if power   is not None else None
    except Exception:
        power = None
    try:
        voltage = float(voltage) if voltage is not None else None
    except Exception:
        voltage = None
    try:
        current = float(current) if current is not None else None
    except Exception:
        current = None

    pf: Optional[float] = None
    try:
        if power is not None and voltage is not None and current is not None:
            denom = voltage * current
            if denom != 0:
                pf = power / denom
    except Exception:
        pf = None

    return [power, voltage, current, pf]


def _impute(value: Optional[float], default: float = 0.0) -> float:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return default
    return value


# ---------------------------------------------------------------------------
# Rule-based fallback scorer
# ---------------------------------------------------------------------------
_SPIKE_THRESHOLD = 3000.0


def _rule_score(reading: Any) -> float:
    """Simple rule-based anomaly score in [0, 1]."""
    power = _get(reading, "power_consumption", "power")
    try:
        power = float(power) if power is not None else 0.0
    except Exception:
        power = 0.0

    tamper = bool(_get(reading, "tamper", "tamper_flag"))
    if tamper:
        return 1.0

    if power >= _SPIKE_THRESHOLD:
        excess = power - _SPIKE_THRESHOLD
        return min(1.0, 0.5 + 0.5 * min(1.0, excess / _SPIKE_THRESHOLD))

    return min(0.45, power / _SPIKE_THRESHOLD * 0.45)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict(features: Any) -> float:
    """Return an anomaly score in [0, 1] for a single reading.

    Tries the trained IsolationForest first; falls back to rule-based scoring
    when the model is unavailable or raises an error.

    Args:
        features: dict or ORM object with fields power_consumption / power,
                  optionally voltage, current.

    Returns:
        float in [0, 1] — higher means more anomalous.
    """
    try:
        model = _load_iso()
        if model is not None:
            feat = _to_feature_vector(features)
            try:
                import numpy as np  # type: ignore
                X = np.array([[_impute(f) for f in feat]], dtype=float)
                # sklearn IsolationForest score_samples returns values in
                # (-inf, 0]; more negative = more anomalous.
                # Map to [0,1]: score = clip(-raw / 0.7, 0, 1)
                raw = float(model.score_samples(X)[0])
                return round(max(0.0, min(1.0, -raw / 0.7)), 4)
            except Exception:
                pass
    except Exception:
        pass

    return _rule_score(features)


def predict_anomaly(reading: Any, model_path: Optional[Union[str, Path]] = None) -> float:
    """Compatibility alias for predict() used by anomaly_service.py."""
    return predict(reading)


def predict_batch(records: Sequence[Any]) -> List[float]:
    """Score a sequence of readings in one call.

    Prefers vectorised sklearn inference when model is available.
    """
    if not records:
        return []

    try:
        model = _load_iso()
        if model is not None:
            import numpy as np  # type: ignore
            rows = [[_impute(f) for f in _to_feature_vector(r)] for r in records]
            X = np.array(rows, dtype=float)
            raws = model.score_samples(X)
            return [round(max(0.0, min(1.0, float(-r) / 0.7)), 4) for r in raws]
    except Exception:
        pass

    return [_rule_score(r) for r in records]
