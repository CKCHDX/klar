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
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.

    echo Installing required packages...
    call venv\Scripts\activate

    REM Install base requirements
    if exist requirements.txt (
        pip install --upgrade pip

        pip install -r requirements.txt

        REM Install additional packages required by klar
        pip install PyQt6
        pip install PyQt6-WebEngine
        pip install beautifulsoup4
        pip install lxml

        if errorlevel 1 (
            echo [ERROR] Failed to install required packages.
            pause
            exit /b 1
        ) else (
            echo All packages installed successfully.
        )
        call deactivate
    ) else (
        echo [WARNING] requirements.txt not found. Installing only extra packages...

        call venv\Scripts\activate

        pip install --upgrade pip
        pip install PyQt6
        pip install PyQt6-WebEngine
        pip install beautifulsoup4
        pip install lxml

        call deactivate
    )
) else (
    echo Virtual environment found.
)

echo.
echo Activating virtual environment...
start cmd /k "venv\Scripts\activate"
