param([int]$Port = 8017)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) { throw 'Run .\setup.ps1 first.' }
& ./.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port $Port --limit-concurrency 128 --no-access-log

