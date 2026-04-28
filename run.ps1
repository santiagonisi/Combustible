if (-not (Test-Path .venv)) {
    python -m venv .venv
}

.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
