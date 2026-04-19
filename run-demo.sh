#!/usr/bin/env bash
# Run a quick demo seed. Usage:
# ./run-demo.sh [zones] [meters_per_zone] [hours] [interval_minutes] [--fast]

ZONES=${1:-3}
METERS=${2:-12}
HOURS=${3:-6}
INTERVAL=${4:-5}
FAST_FLAG=""
if [ "${5:-}" = "--fast" ]; then
  FAST_FLAG="--fast"
fi

echo "Seeding demo data: zones=${ZONES} metersPerZone=${METERS} hours=${HOURS} interval=${INTERVAL}"
python backend/scripts/seed.py --zones ${ZONES} --meters-per-zone ${METERS} --hours ${HOURS} --interval ${INTERVAL} ${FAST_FLAG}
