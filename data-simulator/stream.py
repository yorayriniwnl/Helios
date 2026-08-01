"""Multi-meter streaming simulator for Helios.

Sends generated readings to the backend /api/v1/readings endpoint at a
configurable interval. Supports:
  - Multiple meters streamed in parallel (--meters 1,2,3 or --meters 5)
  - JWT authentication (--token or auto-login via --email/--password)
  - Configurable anomaly injection rate (--anomaly-prob 0.05)
  - Graceful shutdown on SIGINT/SIGTERM
  - Exponential backoff on connection errors

Usage examples
--------------
# Stream 3 meters every 2s with auto-login:
    python stream.py --meters 1,2,3 --interval 2 \\
        --email admin@example.com --password adminpass123

# Stream first 10 meters, 15% anomaly rate:
    python stream.py --meters 10 --anomaly-prob 0.15

# Provide a pre-existing JWT token:
    python stream.py --token eyJ... --meters 1
"""
from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
import threading
from datetime import datetime
from typing import List, Optional

import requests

from generator import generate_reading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [meter-%(thread)d] %(message)s",
)
logger = logging.getLogger("helios.simulator")

_shutdown = threading.Event()

# ── Auth ──────────────────────────────────────────────────────────────────────

def acquire_token(base_url: str, email: str, password: str) -> Optional[str]:
    """Login and return a JWT access token, or None on failure."""
    try:
        resp = requests.post(
            f"{base_url.rstrip('/')}/api/v1/auth/login",
            json={"email": email, "password": password},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception as exc:
        logger.error("Login failed: %s", exc)
        return None


# ── Per-meter stream ──────────────────────────────────────────────────────────

def stream_meter(
    meter_id: int,
    base_url: str,
    interval: float,
    anomaly_prob: float,
    token: Optional[str],
) -> None:
    """Continuously POST readings for a single meter until shutdown."""
    url = f"{base_url.rstrip('/')}/api/v1/readings/"
    session = requests.Session()
    if token:
        session.headers["Authorization"] = f"Bearer {token}"

    backoff = 1.0
    sent = 0

    logger.info("Streaming meter %d → %s (interval=%.1fs, anomaly_prob=%.2f)",
                meter_id, url, interval, anomaly_prob)

    while not _shutdown.is_set():
        try:
            reading = generate_reading(meter_id, anomaly_prob=anomaly_prob)
            payload = {
                "meter_id": reading["meter_id"],
                "timestamp": reading["timestamp"].isoformat(),
                "voltage": reading["voltage"],
                "current": reading["current"],
                "power_consumption": reading["power"],
            }
            resp = session.post(url, json=payload, timeout=5)
            resp.raise_for_status()
            sent += 1
            if sent % 10 == 0:
                logger.info("Meter %d: %d readings sent", meter_id, sent)
            backoff = 1.0  # reset on success
        except requests.exceptions.ConnectionError:
            logger.warning("Meter %d: connection error — retrying in %.0fs", meter_id, backoff)
            _shutdown.wait(backoff)
            backoff = min(backoff * 2, 30)
            continue
        except Exception as exc:
            logger.warning("Meter %d: send error — %s", meter_id, exc)

        _shutdown.wait(interval)

    session.close()
    logger.info("Meter %d stopped after %d readings.", meter_id, sent)


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_meters(arg: str) -> List[int]:
    """Parse '--meters 1,2,3' or '--meters 5' (meaning IDs 1..5)."""
    arg = arg.strip()
    if "," in arg:
        return [int(x.strip()) for x in arg.split(",") if x.strip()]
    n = int(arg)
    return list(range(1, n + 1))


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream simulated readings to Helios backend")
    parser.add_argument("--base-url", default="http://localhost:8000",
                        help="Backend base URL (default: http://localhost:8000)")
    parser.add_argument("--meters", default="1",
                        help="Comma-separated meter IDs or a count (e.g. '1,2,3' or '5')")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Seconds between readings per meter (default: 1.0)")
    parser.add_argument("--anomaly-prob", type=float, default=0.05,
                        help="Probability of injecting an anomaly (default: 0.05)")
    parser.add_argument("--token", default="",
                        help="Pre-existing JWT bearer token (skips login)")
    parser.add_argument("--email", default="admin@example.com",
                        help="Email for auto-login (default: admin@example.com)")
    parser.add_argument("--password", default="adminpass123",
                        help="Password for auto-login (default: adminpass123)")
    args = parser.parse_args()

    meter_ids = parse_meters(args.meters)

    # Acquire token
    token: Optional[str] = args.token or None
    if not token:
        logger.info("Logging in as %s…", args.email)
        token = acquire_token(args.base_url, args.email, args.password)
        if not token:
            logger.warning("Could not obtain token; proceeding without auth.")

    # Graceful shutdown
    def _handle_signal(sig, frame):
        logger.info("Shutdown signal received — stopping all streams…")
        _shutdown.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # Launch one thread per meter
    threads = []
    for mid in meter_ids:
        t = threading.Thread(
            target=stream_meter,
            args=(mid, args.base_url, args.interval, args.anomaly_prob, token),
            daemon=True,
            name=f"meter-{mid}",
        )
        t.start()
        threads.append(t)

    logger.info("Streaming %d meter(s). Press Ctrl-C to stop.", len(meter_ids))

    # Wait until shutdown
    _shutdown.wait()
    for t in threads:
        t.join(timeout=3)

    logger.info("All streams stopped.")


if __name__ == "__main__":
    main()
