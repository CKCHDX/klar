@echo off
setlocal enabledelayedexpansion

cls

echo.
echo ========================================
echo Klar 3.1 - Single-File Build System
echo ========================================
echo.
echo This will create a standalone single-file executable
echo with all dependencies embedded (no external files needed)
echo.
pause

REM ============================================
REM STEP 1: CHECK PYTHON
REM ============================================

echo.
echo [1/7] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo OK: %PYTHON_VER% found
timeout /t 1 >nul

REM ============================================
REM STEP 2: ACTIVATE VIRTUAL ENVIRONMENT
REM ============================================

echo.
echo [2/7] Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat
echo OK: Virtual environment ready
timeout /t 1 >nul

REM ============================================
REM STEP 3: CHECK FILE INTEGRITY
REM ============================================

echo.
echo [3/7] Checking file integrity...
set ERROR_COUNT=0

if not exist "klar_browser.py" (
    echo ERROR: Missing klar_browser.py
    set /a ERROR_COUNT+=1
)

if not exist "keywords_db.json" (
    echo ERROR: Missing keywords_db.json
    set /a ERROR_COUNT+=1
)

if not exist "domains.json" (
    echo ERROR: Missing domains.json
    set /a ERROR_COUNT+=1
)

if not exist "klar.ico" (
    echo ERROR: Missing klar.ico
    set /a ERROR_COUNT+=1
)

if %ERROR_COUNT% GTR 0 (
    echo.
    echo FAILED: %ERROR_COUNT% files missing
    pause
    exit /b 1
)

python -c "import json; json.load(open('keywords_db.json', encoding='utf-8'))" 2>nul
if errorlevel 1 (
    echo ERROR: keywords_db.json has syntax errors
    pause
    exit /b 1
)

python -c "import json; json.load(open('domains.json', encoding='utf-8'))" 2>nul
if errorlevel 1 (
    echo ERROR: domains.json has syntax errors
    pause
    exit /b 1
)

python -m py_compile klar_browser.py 2>nul
if errorlevel 1 (
    echo ERROR: klar_browser.py has syntax errors
    pause
    exit /b 1
)

echo OK: All files validated
timeout /t 1 >nul

REM ============================================
REM STEP 4: INSTALL DEPENDENCIES
REM ============================================

echo.
echo [4/7] Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install PyQt6 PyQt6-WebEngine requests beautifulsoup4 lxml pyinstaller >nul 2>&1
echo OK: Dependencies installed
timeout /t 1 >nul

REM ============================================
REM STEP 5: CLEAN OLD BUILDS
REM ============================================

echo.
echo [5/7] Cleaning old builds...
if exist "dist" rmdir /s /q dist 2>nul
if exist "build" rmdir /s /q build 2>nul
if exist "release" rmdir /s /q release 2>nul
if exist "klar.spec" del /q klar.spec 2>nul
echo OK: Build directories cleaned
timeout /t 1 >nul

REM ============================================
REM STEP 6: BUILD WITH PYINSTALLER (DIRECT METHOD)
REM ============================================

echo.
echo [6/7] Building single-file Windows executable...
echo This may take 3-7 minutes, please wait...
echo.

REM Get full path to icon
for %%F in (klar.ico) do set ICON_PATH=%%~dpF%%~nxF

REM Build with direct pyinstaller command (like old working script)
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --icon="%ICON_PATH%" ^
    --add-data "keywords_db.json:." ^
    --add-data "domains.json:." ^
    --add-data "klar.ico:." ^
    --add-data "engine:engine" ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtWebEngineWidgets ^
    --hidden-import=PyQt6.QtWebEngineCore ^
    --hidden-import=PyQt6.sip ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    --hidden-import=lxml ^
    --hidden-import=engine.domain_whitelist ^
    --hidden-import=engine.demographic_detector ^
    --hidden-import=engine.loki_system ^
    --hidden-import=engine.setup_wizard ^
    --exclude-module PySide6 ^
    --name=Klar ^
    klar_browser.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    echo Check the output above for errors
    pause
    exit /b 1
)

if not exist "dist\Klar.exe" (
    echo.
    echo ERROR: Klar.exe was not created
    pause
    exit /b 1
)

echo.
echo OK: Single-file executable built successfully
timeout /t 2 >nul

REM ============================================
REM STEP 7: CREATE RELEASE STRUCTURE
REM ============================================

echo.
echo [7/7] Creating release packages...

mkdir release 2>nul
mkdir release\windows 2>nul

echo Packaging Windows release...
copy "dist\Klar.exe" "release\windows\Klar.exe" >nul

for %%F in ("release\windows\Klar.exe") do set FILESIZE=%%~zF

echo Building complete! Klar.exe is ready.
timeout /t 1 >nul

REM ============================================
REM COMPLETION
REM ============================================

cls

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo SINGLE-FILE EXECUTABLE CREATED!
echo.
echo Windows:
echo Location: release\windows\Klar.exe
echo Size: %FILESIZE% bytes
echo Type: Standalone (no external files)
echo.
echo ========================================
echo What You Can Distribute
echo ========================================
echo.
echo Just send: release\windows\Klar.exe
echo Users run it - that's all!
echo.
echo ========================================
echo.

REM Ask if user wants to test now
choice /C YN /M "Do you want to test the executable now?"
if errorlevel 2 goto end

echo.
echo Launching Klar...
echo (First launch may take 5-10 seconds to unpack)
echo.

start "" "release\windows\Klar.exe"
timeout /t 5 >nul

:end

echo.
echo Build script completed successfully!
echo.
echo The file release\windows\Klar.exe is completely standalone.
echo No other files needed - just distribute this single file!
echo.
pause
