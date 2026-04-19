#!/usr/bin/env bash
set -euo pipefail

echo "[Helios] Hackathon setup (POSIX) — beginning..."

# Find python
PY=python3
if ! command -v $PY >/dev/null 2>&1; then
  PY=python
fi

if [ ! -d backend/.venv ]; then
  echo "Creating virtualenv in backend/.venv..."
  $PY -m venv backend/.venv
fi

VENV_PY=backend/.venv/bin/python
VENV_PIP=backend/.venv/bin/pip

if [ ! -x "$VENV_PY" ]; then
  echo "Warning: virtualenv python not found; falling back to system python"
  VENV_PY=$PY
  VENV_PIP=pip
fi

echo "Installing backend requirements..."
$VENV_PIP install -r backend/requirements.txt

if [ -f frontend/package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    echo "Installing frontend packages (npm ci)..."
    (cd frontend && npm ci)
  else
    echo "npm not found — skip frontend install. Install Node.js and run 'npm ci' in frontend if needed."
  fi
fi

echo "Running demo seeder (fast)..."
$VENV_PY backend/scripts/seed.py --fast

echo "Setup complete. To run backend: $VENV_PY -m uvicorn backend.app.main:app --reload --port 8000"
