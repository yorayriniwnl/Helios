<#
Start both backend (uvicorn) and frontend (next dev) for local development.

Usage:
  .\scripts\dev_up.ps1            # starts backend+frontend unless ports are in use
  .\scripts\dev_up.ps1 -SkipFrontend
  .\scripts\dev_up.ps1 -SkipBackend

Creates a .dev_pids file with started process IDs (JSON). If a service is
already listening on the expected port it is skipped.
#>

param(
  [switch]$SkipBackend,
  [switch]$SkipFrontend
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location (Join-Path $scriptDir '..')

$pidFile = ".dev_pids"

# Prefer a virtualenv python executable if available (common names).
$pythonExec = "python"
try {
  if ($env:VIRTUAL_ENV) {
    $maybe = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
    if (Test-Path $maybe) { $pythonExec = $maybe }
  } elseif ($env:VENV_PATH) {
    $maybe = Join-Path $env:VENV_PATH "Scripts\python.exe"
    if (Test-Path $maybe) { $pythonExec = $maybe }
  } else {
    $candidates = @('.venv', '.venv-1', 'venv')
    $roots = @((Get-Location).Path, (Split-Path -Path (Get-Location).Path -Parent))
    foreach ($rootPath in $roots) {
      foreach ($c in $candidates) {
        $base = Join-Path $rootPath $c
        $pwin = Join-Path $base "Scripts\python.exe"
        $pposix = Join-Path $base "bin/python"
        if (Test-Path $pwin) { $pythonExec = $pwin; break }
        if (Test-Path $pposix) { $pythonExec = $pposix; break }
      }
      if ($pythonExec -ne 'python') { break }
    }
  }
} catch {
  # fallback to system python
  $pythonExec = "python"
}

function Test-PortOpen([int]$port) {
  try {
    $res = Test-NetConnection -ComputerName '127.0.0.1' -Port $port -WarningAction SilentlyContinue
    return $res.TcpTestSucceeded
  } catch {
    return $false
  }
}

$pids = @{}

if (-not $SkipBackend) {
  if (Test-PortOpen 8000) {
    Write-Host "Backend already listening on 127.0.0.1:8000; skipping backend start."
  } else {
    Write-Host "Starting backend (uvicorn) on 127.0.0.1:8000 using $pythonExec ..."
    $backendProc = Start-Process -FilePath $pythonExec -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload" -PassThru
    $pids["backend"] = $backendProc.Id
    Start-Sleep -Seconds 1
  }
}

if (-not $SkipFrontend) {
  if (Test-PortOpen 3000) {
    Write-Host "Frontend already listening on 127.0.0.1:3000; skipping frontend start."
  } else {
    Write-Host "Starting frontend (next dev) on 3000..."
    Push-Location ./frontend
    $frontendProc = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -PassThru
    Pop-Location
    $pids["frontend"] = $frontendProc.Id
    Start-Sleep -Seconds 1
  }
}

if ($pids.Count -gt 0) {
  $pids | ConvertTo-Json | Out-File $pidFile -Encoding utf8
  Write-Host "Started processes and wrote PIDs to $pidFile"
} else {
  Write-Host "No new processes started."
}
