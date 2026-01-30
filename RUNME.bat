@echo off
chcp 65001 >nul
cls
echo ======================================================
echo      Klar Search Engine - Setup & Launch
echo ======================================================

REM === STEP 1: Create/Activate Virtual Environment ===
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create venv. Is Python installed?
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment exists
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate venv
    pause
    exit /b 1
)
echo ✓ venv activated

REM === STEP 2: Upgrade pip ===
echo Upgrading pip...
python -m pip install --upgrade pip

REM === STEP 3: Install requirements ===
if exist "requirements.txt" (
    echo Installing requirements...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo WARNING: requirements.txt install had issues, trying common packages...
        pip install flask flask-cors psutil PyYAML requests beautifulsoup4 lxml PyQt6
    )
) else (
    echo WARNING: requirements.txt not found, installing common packages...
    pip install flask flask-cors psutil PyYAML requests beautifulsoup4 lxml PyQt6
)
echo ✓ Dependencies installed

REM === STEP 4: Test PyQt6 ===
echo Testing PyQt6...
python -c "try: from PyQt6 import QtWidgets; print('✓ PyQt6 OK'); except Exception as e: print('✗ PyQt6 ERROR:', e)" || (
    echo.
    echo PyQt6 failed. Installing Visual C++ Redistributable may help:
    echo https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
)

REM === STEP 5: Launch GUI ===
echo.
echo ======================================================
echo          Launching KSE GUI...
echo ======================================================
python scripts/start_gui.py

REM === Keep window open ===
echo.
echo Press any key to exit...
pause >nul
