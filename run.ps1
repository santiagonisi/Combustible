$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Para lanzar la app desde PowerShell, copia y pega esta linea:" -ForegroundColor Yellow
Write-Host "Set-Location 'C:\Users\Usuario\Desktop\Combustible'; .\.venv\Scripts\Activate.ps1; uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Green
Write-Host ""

# Ejecutar siempre desde la raiz del proyecto, incluso si el script se inicia desde otra ubicacion.
Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    python -m venv .venv
}

& $venvPython -m pip install -r requirements.txt
& $venvPython -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
