$ErrorActionPreference = "Stop"

# Ejecutar siempre desde la raiz del proyecto, incluso si el script se inicia desde otra ubicacion.
Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    python -m venv .venv
    & $venvPython -m pip install -r requirements.txt
}

& $venvPython -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
