## Local development

This document explains how to run the Helios backend and frontend locally without Docker.

Prerequisites
- Python 3.11+ and a virtual environment (activate before running the backend)
- Node.js and npm (to run the Next.js frontend)

Quick start (PowerShell)

1. From the `helios-ai` project root, install Python deps (in a venv):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

2. Install frontend deps:

```powershell
Push-Location frontend
npm install
Pop-Location
```

3. Start both services (background):

```powershell
.\scripts\dev_up.ps1
```

This will start the backend at `http://127.0.0.1:8000` and the frontend at `http://localhost:3000`.
The script writes a `.dev_pids` file with process IDs for later cleanup.

4. To stop these processes:

```powershell
.\scripts\dev_down.ps1
```

Notes
- `dev_up.ps1` skips starting a service if a process is already listening on the expected port.
- Use the `-SkipBackend` or `-SkipFrontend` switches to start only one service.
- CI workflow is configured in `.github/workflows/ci.yml` to run tests and lint on push/PR.
