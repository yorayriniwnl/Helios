<#
.\run-demo.ps1 [-Zones 3] [-MetersPerZone 12] [-Hours 6] [-Interval 5] [-Fast]
#>
param(
    [int]$Zones = 3,
    [int]$MetersPerZone = 12,
    [int]$Hours = 6,
    [int]$Interval = 5,
    [switch]$Fast
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $root

# Activate backend venv if available
$venvActivate = Join-Path -Path $root -ChildPath "backend\.venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activating backend virtualenv..."
    & $venvActivate
}

$fastFlag = ''
if ($Fast) { $fastFlag = '--fast' }

Write-Host "Seeding demo data: zones=$Zones metersPerZone=$MetersPerZone hours=$Hours interval=$Interval"
python backend\scripts\seed.py --zones $Zones --meters-per-zone $MetersPerZone --hours $Hours --interval $Interval $fastFlag

Pop-Location
