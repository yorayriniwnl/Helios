Param()
$ErrorActionPreference = "Stop"

Write-Host "[Helios] Hackathon setup (PowerShell) — beginning..."

# Find Python executable (prefer py -3 on Windows)
$pyCmd = "py -3"
try {
    & $pyCmd -V > $null 2>&1
} catch {
    $pyCmd = "python"
}

if (-not (Test-Path "backend\.venv")) {
    Write-Host "Creating virtual environment in backend\.venv..."
    & $pyCmd -m venv backend\.venv
}

$venvPython = "backend\.venv\Scripts\python.exe"
$venvPip = "backend\.venv\Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment python not found; trying fallback 'python'"
    $venvPython = "python"
    $venvPip = "pip"
}

Write-Host "Installing backend requirements..."
& $venvPip install -r backend/requirements.txt

if (Test-Path "frontend/package.json") {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Host "npm not found. Skipping frontend install. Install Node.js and run 'npm ci' in frontend if needed."
    } else {
        Write-Host "Installing frontend packages (npm ci)..."
        Push-Location frontend
        npm ci
        Pop-Location
    }
}

Write-Host "Running demo seeder (fast)..."
& $venvPython backend/scripts/seed.py --fast

Write-Host "Setup finished. To run locally:"
Write-Host "  & $venvPython -m uvicorn backend.app.main:app --reload --port 8000"
Write-Host "Then open http://localhost:8000/ and the frontend if running on port 3000."

Write-Host "Note: Replace demo video link in README.md with your recorded demo URL."
