<#
Stop processes started by `dev_up.ps1` using the PID file `.dev_pids`.

Usage:
  .\scripts\dev_down.ps1
#>

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location (Join-Path $scriptDir '..')

$pidFile = ".dev_pids"
if (-not (Test-Path $pidFile)) {
  Write-Host "No pid file found ($pidFile). Nothing to stop."
  exit 0
}

try {
  $pids = Get-Content $pidFile | ConvertFrom-Json
} catch {
  Write-Host "Failed to read pid file; removing it and exiting."
  Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
  exit 0
}

foreach ($name in $pids.psobject.Properties.Name) {
  $pid = $pids.$name
  if ($pid -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
    try {
      Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
      Write-Host "Stopped $name (PID $pid)"
    } catch {
      Write-Host "Failed to stop $name (PID $pid): $_"
    }
  } else {
    Write-Host "$name (PID $pid) not running"
  }
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
