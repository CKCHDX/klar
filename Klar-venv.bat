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
echo.

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
    echo.
    
    echo Installing requirements from requirements.txt...
    if exist "requirements.txt" (
        call venv\Scripts\activate.bat
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [WARNING] Some packages may have failed to install.
            echo Please check the output above for errors.
        ) else (
            echo All packages installed successfully.
        )
        call deactivate
    ) else (
        echo [WARNING] requirements.txt not found. Skipping package installation.
    )
) else (
    echo Virtual environment found.
)

echo.
echo Activating virtual environment...
start cmd /k "venv\Scripts\activate"
