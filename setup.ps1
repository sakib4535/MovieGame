param([switch]$Compose)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if ($Compose) {
    if (-not (Test-Path -LiteralPath '.env')) {
        function New-Secret {
            $bytes = New-Object byte[] 32
            $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
            try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
            return [System.BitConverter]::ToString($bytes).Replace('-', '').ToLowerInvariant()
        }
        @("POSTGRES_PASSWORD=$(New-Secret)", "RATE_SECRET=$(New-Secret)", "METRICS_TOKEN=$(New-Secret)") | Set-Content -LiteralPath '.env' -Encoding ascii
    }
    docker compose up --build -d
    if ($LASTEXITCODE -ne 0) { throw 'Docker setup failed. Start Docker Desktop and retry.' }
    Write-Host 'MovieGame: http://localhost:8080'
} else {
    if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the virtual environment.' }
    }
    & ./.venv/Scripts/python.exe -m pip install -r requirements-dev.txt -c requirements.lock
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    & ./.venv/Scripts/python.exe -m app.manage init
    if ($LASTEXITCODE -ne 0) { throw 'Database setup failed.' }
    Write-Host 'Ready. Run .\start.ps1, then open http://localhost:8017'
}

