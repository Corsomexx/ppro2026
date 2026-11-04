@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo  Pujcovna Hory a voda - Start serveru (FastAPI/Uvicorn)
echo ========================================================

REM 1. Kontrola existence virtualniho prostredi .venv
if not exist ".venv" (
    echo [INFO] Virtualni prostredi .venv nebylo nalezeno.
    echo [INFO] Vytvarim nove prostredi .venv...
    py -m venv .venv 2>nul || python -m venv .venv
    if errorlevel 1 (
        echo [CHYBA] Nepodarilo se vytvorit virtualni prostredi .venv. Zkontrolujte instalaci Pythonu.
        pause
        exit /b 1
    )
    echo [INFO] Instaluji zavislosti z requirements.txt...
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [CHYBA] Instalace zavislosti selhala.
        pause
        exit /b 1
    )
) else (
    call .venv\Scripts\activate.bat
)

REM 2. Overeni uvicornu
python -c "import uvicorn" 2>nul
if errorlevel 1 (
    echo [INFO] Knihovny nejsou kompletni, instaluji z requirements.txt...
    pip install -r requirements.txt
)

REM 3. Spusteni FastAPI serveru
echo [INFO] Server bezi na: http://localhost:8000
echo [INFO] Swagger API na:  http://localhost:8000/docs
echo [INFO] Ukonceni klavesovou zkratkou Ctrl+C.
echo --------------------------------------------------------
python -m uvicorn src.main:app --reload --port 8000
