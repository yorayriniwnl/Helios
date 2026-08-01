import importlib.util
import json
from pathlib import Path
from datetime import datetime
import pytest


def load_generator_module():
    root = Path(__file__).resolve().parents[2]
    gen_path = root / "data-simulator" / "generator.py"
    spec = importlib.util.spec_from_file_location("sim_generator", str(gen_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def test_output_schema_and_serialization():
    mod = load_generator_module()
    r = mod.generate_reading(1, seed=12345)
    assert isinstance(r, dict)
    for k in ("meter_id", "voltage", "current", "power", "timestamp"):
        assert k in r

    assert isinstance(r["meter_id"], int)
    assert isinstance(r["voltage"], (float, int))
    assert isinstance(r["current"], (float, int))
    assert isinstance(r["power"], (float, int))
    assert isinstance(r["timestamp"], datetime)
    assert r["timestamp"].tzinfo is not None

    # Simulate payload formatting as in stream.py and ensure JSON serializes
    payload = {
        "meter_id": r["meter_id"],
        "timestamp": r["timestamp"].isoformat(),
        "voltage": r["voltage"],
        "current": r["current"],
        "power_consumption": r["power"],
    }
    s = json.dumps(payload)
    assert isinstance(s, str)


def test_seed_determinism_and_variation():
    mod = load_generator_module()
    a = mod.generate_reading(2, seed=42)
    b = mod.generate_reading(2, seed=42)
    # numeric fields should be deterministic when seed provided
    assert a["voltage"] == b["voltage"] and a["current"] == b["current"] and a["power"] == b["power"]

    c = mod.generate_reading(2, seed=43)
    assert not (a["voltage"] == c["voltage"] and a["current"] == c["current"]) 


def test_randomness_without_seed():
    mod = load_generator_module()
    r1 = mod.generate_reading(3)
    r2 = mod.generate_reading(3)
    # extremely unlikely to be identical
    assert not (r1["voltage"] == r2["voltage"] and r1["current"] == r2["current"] and r1["power"] == r2["power"])


def test_anomaly_injection_always():
    mod = load_generator_module()
    reading = mod.generate_reading(4, seed=7, anomaly_prob=1.0, anomaly_magnitude=4.0)
    assert "anomaly" in reading
    an = reading["anomaly"]
    assert an["type"] == "power_spike"
    assert pytest.approx(an["factor"], 0.0001) == 4.0
    expected_current = round(an["original_current"] * an["factor"], 3)
    assert reading["current"] == expected_current
    assert reading["power"] == round(reading["voltage"] * reading["current"], 3)
