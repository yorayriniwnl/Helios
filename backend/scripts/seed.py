#!/usr/bin/env python3
"""
Seed demo data: zones, meters, and readings.

Usage (from the `backend` directory):

python scripts/seed.py --zones 3 --meters-per-zone 12 --hours 6 --interval 5

The script is idempotent for zones and meter numbers it creates (skips existing).
"""
import argparse
import random
import time
from datetime import datetime, timedelta
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Seed demo zones, meters and readings")
    p.add_argument("--zones", type=int, default=3, help="Number of zones to create")
    p.add_argument("--meters-per-zone", type=int, default=12, help="Meters to create per zone")
    p.add_argument("--hours", type=float, default=6.0, help="How many hours of historical readings to seed")
    p.add_argument("--interval", type=int, default=5, help="Reading interval in minutes")
    p.add_argument("--start", type=str, default=None, help="ISO start timestamp (defaults to now - hours)")
    p.add_argument("--fast", action="store_true", help="Use faster ingestion (skip anomaly detection) where possible")
    return p.parse_args()


def ensure_path():
    # When run from project root, ensure we can import `app` package by adding backend to sys.path
    import sys

    here = Path(__file__).resolve().parents[1]
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))


def main():
    args = parse_args()
    ensure_path()

    # Local imports (after sys.path adjusted)
    from app.core.database import SessionLocal
    from app.services.zone_service import create_zone as svc_create_zone
    from app.services.meter_service import create_meter as svc_create_meter
    from app.services.reading_service import create_reading as svc_create_reading
    from app.repositories.reading_repository import create_reading as repo_create_reading
    from app.models.zone import Zone
    from app.models.meter import Meter

    db = SessionLocal()

    try:
        sample_zone_names = [
            "Northside",
            "Riverside",
            "Downtown",
            "West End",
            "East Ridge",
            "Lakeshore",
            "Hillcrest",
        ]

        zone_names = sample_zone_names[: args.zones]

        print(f"Seeding {len(zone_names)} zones")
        created_zones = []
        for name in zone_names:
            # idempotent: reuse existing zone with same name
            existing = db.query(Zone).filter(Zone.name == name).first()
            if existing:
                print(f" - zone exists: {name} (id={existing.id})")
                created_zones.append(existing)
                continue
            z = svc_create_zone(db, name=name)
            print(f" - created zone: {name} (id={z.id})")
            created_zones.append(z)

        total_meters = 0
        created_meters = []
        print(f"Creating up to {args.meters_per_zone} meters per zone")
        for z in created_zones:
            for i in range(args.meters_per_zone):
                meter_number = f"{z.name[:3].upper()}-{i+1:04d}"
                # skip if meter exists
                existing_m = db.query(Meter).filter(Meter.meter_number == meter_number).first()
                if existing_m:
                    created_meters.append(existing_m)
                    continue
                m = svc_create_meter(db, meter_number=meter_number, household_name=f"Household {i+1}")
                # attach to zone (repository create_meter doesn't accept zone_id)
                try:
                    m.zone_id = z.id
                    db.add(m)
                    db.commit()
                    db.refresh(m)
                except Exception:
                    db.rollback()
                created_meters.append(m)
                total_meters += 1

        print(f"Created/Found meters: {len(created_meters)} (newly created: {total_meters})")

        # Prepare reading timeline
        interval = timedelta(minutes=args.interval)
        points = max(1, int(args.hours * 60 // args.interval))
        if args.start:
            start = datetime.fromisoformat(args.start)
        else:
            start = datetime.utcnow() - timedelta(hours=args.hours)

        print(f"Seeding {points} readings per meter ({args.hours}h @ {args.interval}m)")

        meter_count = len(created_meters)
        progress = 0
        t0 = time.time()

        for mi, m in enumerate(created_meters):
            # per-meter base consumption
            base = random.uniform(60.0, 600.0)
            voltage_base = random.uniform(220.0, 240.0)
            for p in range(points):
                ts = start + p * interval
                # add small random variation
                noise = random.uniform(-0.06, 0.06)  # +-6%
                power = max(0.1, base * (1.0 + noise))
                # occasional spike
                if random.random() < 0.015:
                    power *= random.uniform(2.0, 4.5)

                voltage = voltage_base * (1.0 + random.uniform(-0.02, 0.02))
                current = power / max(1.0, voltage)

                try:
                    if args.fast:
                        repo_create_reading(db, meter_id=m.id, timestamp=ts, voltage=round(voltage, 2), current=round(current, 3), power_consumption=round(power, 2))
                    else:
                        svc_create_reading(db, meter_id=m.id, timestamp=ts, voltage=round(voltage, 2), current=round(current, 3), power_consumption=round(power, 2))
                except Exception as e:
                    print(f"  ! failed to write reading for meter {m.id}: {e}")
                    try:
                        db.rollback()
                    except Exception:
                        pass

            progress += 1
            if progress % 5 == 0 or progress == meter_count:
                elapsed = time.time() - t0
                print(f"  seeded readings for {progress}/{meter_count} meters (elapsed: {int(elapsed)}s)")

        print("Seeding complete.")

    finally:
        try:
            db.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
