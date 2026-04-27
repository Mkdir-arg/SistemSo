param(
    [switch]$Headed,
    [string]$BaseUrl = $env:E2E_BASE_URL,
    [string]$ComposeFile = "docker-compose.hybrid.yml",
    [string]$Service = "app",
    [int]$HealthTimeoutSec = 60,
    [switch]$SkipSeed
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
    $BaseUrl = "http://localhost:8000"
}
$BaseUrl = $BaseUrl.TrimEnd("/")
$env:E2E_BASE_URL = $BaseUrl

Write-Host "UI E2E base URL: $BaseUrl"

$healthUrl = "$BaseUrl/health/"
$deadline = (Get-Date).AddSeconds($HealthTimeoutSec)
$healthy = $false
while ((Get-Date) -lt $deadline) {
    try {
        Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5 | Out-Null
        $healthy = $true
        break
    } catch {
        Start-Sleep -Seconds 2
    }
}
if (-not $healthy) {
    throw "La app no responde en $healthUrl despues de $HealthTimeoutSec segundos. Levanta Docker antes de correr la suite."
}

if (-not $SkipSeed) {
    Write-Host "Seeding E2E Turnos data via Docker..."
    docker compose -f $ComposeFile exec -T $Service python manage.py seed_e2e_turnos
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo el seed E2E de Turnos."
    }
}

$pythonExe = "python"
$pythonPrefixArgs = @()
$pythonWorks = $false
if (Get-Command $pythonExe -ErrorAction SilentlyContinue) {
    try {
        & $pythonExe --version *> $null
        $pythonWorks = ($LASTEXITCODE -eq 0)
    } catch {
        $pythonWorks = $false
    }
}
if (-not $pythonWorks) {
    if (-not (Get-Command "py" -ErrorAction SilentlyContinue)) {
        throw "No encontre Python en PATH ni el launcher py."
    }
    $pythonExe = "py"
    $pythonPrefixArgs = @("-3")
}

$pytestArgs = @(
    "tests/ui",
    "-m",
    "ui",
    "--browser",
    "chromium",
    "--e2e-base-url=$BaseUrl"
)

if ($Headed) {
    $pytestArgs += "--headed"
}

$pythonArgs = @()
$pythonArgs += $pythonPrefixArgs
$pythonArgs += @("-m", "pytest")
$pythonArgs += $pytestArgs

& $pythonExe @pythonArgs
if ($LASTEXITCODE -ne 0) {
    throw "Fallo la suite UI E2E."
}
