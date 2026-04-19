"""Isolation Forest wrapper for Helios anomaly detection.

Provides a lightweight training and prediction API:

- train(save_path=None, sample_limit=None, **kwargs)
- predict(reading, model_path=None)
- predict_anomaly(reading, model_path=None)  # compatibility alias

The model is saved to `saved_models/isolation_forest.joblib` by default.

Training pulls historical readings from the project's backend database when
available (best-effort). Input features used: `power_consumption`, `voltage`,
`current`, and a derived `power_factor` computed as ``power / (voltage * current)``
when `voltage` and `current` are present.
"""

from __future__ import annotations

import os
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union
import importlib.util

try:
    import numpy as np
except Exception:  # pragma: no cover - runtime dependency
    np = None  # type: ignore

try:
    import joblib
except Exception:  # pragma: no cover - runtime dependency
    joblib = None  # type: ignore

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
except Exception:  # pragma: no cover - runtime dependency
    IsolationForest = None  # type: ignore
    SimpleImputer = None  # type: ignore
    StandardScaler = None  # type: ignore
    Pipeline = None  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = ROOT / "saved_models"
DEFAULT_MODEL_PATH = DEFAULT_MODEL_DIR / "isolation_forest.joblib"


def _ensure_model_dir(path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def _extract_features_from_record(rec: Any) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    # Accept dict-like or object with attributes
    def _get(k1, k2=None):
        if rec is None:
            return None
        if isinstance(rec, dict):
            v = rec.get(k1)
            if v is None and k2:
                v = rec.get(k2)
            return v
        return getattr(rec, k1, None) if hasattr(rec, k1) else (getattr(rec, k2, None) if k2 and hasattr(rec, k2) else None)

    power = _get("power_consumption", "power")
    voltage = _get("voltage", None)
    current = _get("current", None)

    # compute a best-effort power factor
    pf = None
    try:
        if power is not None and voltage is not None and current is not None:
            denom = float(voltage) * float(current)
            if denom != 0:
                pf = float(power) / denom
    except Exception:
        pf = None

    try:
        p = None if power is None else float(power)
    except Exception:
        p = None
    try:
        v = None if voltage is None else float(voltage)
    except Exception:
        v = None
    try:
        c = None if current is None else float(current)
    except Exception:
        c = None

    return p, v, c, pf


def _prepare_matrix(records: Sequence[Any]) -> "np.ndarray":
    if np is None:
        raise RuntimeError("numpy is required for feature preparation")

    # Try to use an external feature engineering module if present. This is
    # loaded dynamically from the sibling `training/feature_engineering.py`
    # file so the package layout (hyphenated folder names) does not prevent
    # importing.
    try:
        fe_path = Path(__file__).resolve().parents[1] / "training" / "feature_engineering.py"
        if fe_path.exists():
            spec = importlib.util.spec_from_file_location("helios_feature_engineering", str(fe_path))
            if spec and spec.loader:
                fe_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(fe_mod)  # type: ignore
                if hasattr(fe_mod, "records_to_feature_matrix"):
                    try:
                        X = fe_mod.records_to_feature_matrix(records)
                        if isinstance(X, np.ndarray):
                            return X
                    except Exception:
                        # if feature engineering fails, fall back to simple extractor
                        pass
    except Exception:
        pass

    # Fallback: simple per-record numeric extraction
    rows: List[List[float]] = []
    for r in records:
        p, v, c, pf = _extract_features_from_record(r)
        rows.append([
            float(p) if p is not None else np.nan,
            float(v) if v is not None else np.nan,
            float(c) if c is not None else np.nan,
            float(pf) if pf is not None else np.nan,
        ])
    X = np.array(rows, dtype=float)
    return X


def train(
    save_path: Optional[Union[str, Path]] = None,
    sample_limit: Optional[int] = None,
    contamination: float = 0.01,
    n_estimators: int = 100,
    max_samples: Union[int, float, str] = "auto",
    random_state: int = 42,
) -> Optional[Path]:
    """Train an Isolation Forest on historical readings from the backend DB.

    This function will attempt to import the project's backend database session
    and the `Reading` model. If unavailable, it will raise an informative
    error.

    Returns the path to the saved model on success, or None on failure.
    """
    if IsolationForest is None or Pipeline is None or joblib is None or np is None:
        raise RuntimeError("scikit-learn, joblib and numpy are required to train the model")

    # Try to import the backend DB session and Reading model
    try:
        try:
            from backend.app.core.database import SessionLocal
            from backend.app.models.reading import Reading
        except Exception:
            # Try relative imports when executed from different cwd
            from ..backend.app.core.database import SessionLocal  # type: ignore
            from ..backend.app.models.reading import Reading  # type: ignore
    except Exception as exc:
        raise RuntimeError("Could not import backend DB SessionLocal/Reading: %s" % exc)

    session = SessionLocal()
    try:
        q = session.query(Reading).order_by(Reading.timestamp)
        if sample_limit:
            q = q.limit(sample_limit)
        records = q.all()
    finally:
        try:
            session.close()
        except Exception:
            pass

    if not records:
        raise RuntimeError("No historical readings found to train on")

    X = _prepare_matrix(records)

    # Create pipeline: imputer -> scaler -> isolation forest
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    clf = IsolationForest(n_estimators=n_estimators, max_samples=max_samples, contamination=contamination, random_state=random_state)

    pipeline = Pipeline([("imputer", imputer), ("scaler", scaler), ("clf", clf)])

    pipeline.fit(X)

    # Persist model
    target = Path(save_path) if save_path else DEFAULT_MODEL_PATH
    _ensure_model_dir(target)
    try:
        joblib.dump(pipeline, str(target))
    except Exception as exc:
        raise RuntimeError(f"Failed to save model to {target}: {exc}")

    return target


def load_model(model_path: Optional[Union[str, Path]] = None):
    if joblib is None:
        return None
    path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
    if not path.exists():
        return None
    try:
        return joblib.load(str(path))
    except Exception:
        return None


def predict(
    reading: Any,
    model_path: Optional[Union[str, Path]] = None,
    model: Optional[Any] = None,
) -> float:
    """Return an anomaly score in [0,1] for a single reading.

    Higher values indicate more anomalous.
    """
    if np is None:
        return 0.0

    if model is None:
        model = load_model(model_path)
    if model is None:
        # model not available
        return 0.0

    X = _prepare_matrix([reading])
    try:
        # decision_function: higher values -> more normal; invert via sigmoid
        df = model.decision_function(X.reshape(1, -1) if X.ndim == 1 else X)[0]
    except Exception:
        try:
            df = model.named_steps["clf"].decision_function(X)[0]
        except Exception:
            return 0.0

    # map df to [0,1] with logistic so that lower df (anomalous) -> higher score
    try:
        score = 1.0 / (1.0 + math.exp(float(df)))
    except Exception:
        score = float(df)
    score = max(0.0, min(1.0, score))
    return score


def predict_anomaly(reading: Any, model_path: Optional[Union[str, Path]] = None) -> float:
    return predict(reading, model_path=model_path)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Train an Isolation Forest on historical readings and save the model.")
    p.add_argument("--out", default=str(DEFAULT_MODEL_PATH), help="Output model path")
    p.add_argument("--limit", type=int, default=0, help="Limit number of readings to train on (0 = no limit)")
    p.add_argument("--contamination", type=float, default=0.01)
    args = p.parse_args()

    lim = args.limit if args.limit and args.limit > 0 else None
    print("Training Isolation Forest (this may take a while)...")
    mpath = train(save_path=Path(args.out), sample_limit=lim, contamination=args.contamination)
    print("Saved model to", mpath)
"""Isolation Forest model stubs for anomaly scoring.

This module contains a lightweight `predict_anomaly` stub used by
the rest of the codebase while a proper ML implementation is added.
"""

from typing import Any, Dict, Optional
import random

def predict_anomaly(data: Optional[Dict[str, Any]] = None) -> float:
	"""
	Return a simple anomaly score in [0.0, 1.0].

	This is a stub implementation:
	- If `data` is falsy, return a random score.
	- If `data` contains a numeric `power` or `power_consumption` value,
	  compute a simple normalized deviation against an expected value.
	"""
	if not data:
		return random.random()

	try:
		power = float(data.get("power", data.get("power_consumption", 0)))
		expected = float(data.get("expected_power", 100.0))
		score = abs(power - expected) / max(1.0, expected)
		return min(1.0, max(0.0, score))
	except Exception:
		return random.random()
