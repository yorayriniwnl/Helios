import random
from datetime import datetime, timezone
from typing import Optional


def generate_reading(meter_id: int, seed: Optional[int] = None, anomaly_prob: float = 0.0, anomaly_magnitude: float = 5.0) -> dict:
    """Generate a simulated reading for a meter.

    Args:
        meter_id: numeric meter identifier.
        seed: optional seed for a local RNG to make a single reading deterministic.
        anomaly_prob: probability in [0,1] to inject an anomaly into this reading.
        anomaly_magnitude: multiplicative factor applied to current when a power_spike anomaly occurs.

    Returns a dict with keys: meter_id, voltage, current, power, timestamp.
    If an anomaly is injected, an `anomaly` key is present with details.
    """
    rng = random if seed is None else random.Random(seed)

    voltage = round(rng.gauss(220, 2), 2)  # around 220V
    current = round(rng.uniform(0.0, 10.0), 3)  # amps
    power = round(voltage * current, 3)  # watts
    timestamp = datetime.now(timezone.utc)

    reading = {
        "meter_id": meter_id,
        "voltage": voltage,
        "current": current,
        "power": power,
        "timestamp": timestamp,
    }

    # Optional anomaly injection (power spike) with simple metadata
    try:
        if anomaly_prob and rng.random() < float(anomaly_prob):
            orig_current = reading["current"]
            new_current = round(orig_current * float(anomaly_magnitude), 3)
            reading["current"] = new_current
            reading["power"] = round(reading["voltage"] * new_current, 3)
            reading["anomaly"] = {"type": "power_spike", "factor": float(anomaly_magnitude), "original_current": orig_current}
    except Exception:
        # best-effort: do not crash generator on anomaly logic errors
        pass

    return reading
