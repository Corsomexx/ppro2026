#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "========================================================"
echo "  Půjčovna Hory a voda - Start serveru (FastAPI/Uvicorn)"
echo "========================================================"

# 1. Kontrola existence virtuálního prostředí .venv
if [ ! -d ".venv" ]; then
    echo "[INFO] Virtuální prostředí .venv nebylo nalezeno."
    echo "[INFO] Vytvářím nové prostředí .venv..."
    python3 -m venv .venv 2>/dev/null || python -m venv .venv
    source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
fi

# 2. Ověření uvicornu
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "[INFO] Knihovna uvicorn nenalezena, instaluji requirements.txt..."
    pip install -r requirements.txt
fi

# 3. Spuštění FastAPI serveru
echo "[INFO] Server běží na: http://localhost:8000"
echo "[INFO] Swagger API na:  http://localhost:8000/docs"
echo "[INFO] Ukončení klávesovou zkratkou Ctrl+C."
echo "--------------------------------------------------------"
python -m uvicorn src.main:app --reload --port 8000
