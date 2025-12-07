@echo off
cd /d "%~dp0"

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python detected: 
python --version

echo Checking for virtual environment...
if not exist "venv\Scripts\activate" (
    echo Virtual environment not found. Creating new venv...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        echo Make sure you have the venv module installed.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment found.
)

echo Activating virtual environment...
start cmd /k "venv\Scripts\activate"
