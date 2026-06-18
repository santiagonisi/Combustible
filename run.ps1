$ErrorActionPreference = "Stop"

# Always run from the project root even if script is launched elsewhere.
Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    python -m venv .venv
}

& $venvPython -m pip install -r requirements.txt
& $venvPython -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
