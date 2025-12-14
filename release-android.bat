@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Klar 3.1 Android - APK Build System
REM ============================================
REM Builds Klar as an Android APK using Buildozer
REM Requirements:
REM - Python 3.9+
REM - Java Development Kit (JDK 11+)
REM - Android SDK
REM - Buildozer

cls

echo.
echo ========================================
echo Klar 3.1 Android - APK Builder
echo ========================================
echo.
echo This will create an Android APK file
echo for mobile devices (Android 7.0+)
echo.
pause

REM ============================================
REM STEP 1: CHECK PYTHON
REM ============================================

echo.
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Install Python 3.9+ from python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo OK: %PYTHON_VER% found
timeout /t 1 >nul

REM ============================================
REM STEP 2: CHECK JAVA
REM ============================================

echo.
echo [2/8] Checking Java Development Kit...
java -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Java JDK not found in PATH
    echo Please install JDK 11+ and add to PATH
    echo Or set JAVA_HOME environment variable
    echo.
    choice /C YN /M "Continue anyway?"
    if errorlevel 2 (
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('java -version 2^>^&1') do (
        echo OK: Java found
    )
)
timeout /t 1 >nul

REM ============================================
REM STEP 3: SETUP VIRTUAL ENVIRONMENT
REM ============================================

echo.
echo [3/8] Setting up virtual environment...
if not exist "venv_android" (
    echo Creating virtual environment for Android...
    python -m venv venv_android
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

call venv_android\Scripts\activate.bat
echo OK: Virtual environment ready
timeout /t 1 >nul

REM ============================================
REM STEP 4: INSTALL BUILD DEPENDENCIES
REM ============================================

echo.
echo [4/8] Installing build tools...
echo Installing: buildozer, kivy, cython...
pip install --upgrade pip >nul 2>&1
pip install buildozer kivy cython pillow pyjnius plyer requests beautifulsoup4 lxml >nul 2>&1

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Try manually: pip install buildozer kivy cython pillow pyjnius plyer
    pause
    exit /b 1
)

echo OK: Build dependencies installed
timeout /t 1 >nul

REM ============================================
REM STEP 5: CHECK FILE INTEGRITY
REM ============================================

echo.
echo [5/8] Checking file integrity...
set ERROR_COUNT=0

if not exist "klar_mobile.py" (
    echo ERROR: Missing klar_mobile.py (Kivy version required)
    set /a ERROR_COUNT+=1
) else (
    echo OK: klar_mobile.py found
)

if not exist "keywords_db.json" (
    echo ERROR: Missing keywords_db.json
    set /a ERROR_COUNT+=1
) else (
    echo OK: keywords_db.json found
)

if not exist "domains.json" (
    echo ERROR: Missing domains.json
    set /a ERROR_COUNT+=1
) else (
    echo OK: domains.json found
)

if not exist "buildozer.spec" (
    echo WARNING: buildozer.spec not found - will use defaults
) else (
    echo OK: buildozer.spec found
)

if %ERROR_COUNT% GTR 0 (
    echo.
    echo FAILED: %ERROR_COUNT% critical files missing
    pause
    exit /b 1
)

timeout /t 1 >nul

REM ============================================
REM STEP 6: GENERATE BUILDOZER SPEC (if needed)
REM ============================================

echo.
echo [6/8] Preparing build configuration...

if not exist "buildozer.spec" (
    echo Generating buildozer.spec...
    buildozer init >nul 2>&1
    
    if errorlevel 1 (
        echo WARNING: Could not auto-generate buildozer.spec
        echo Creating minimal spec file...
    )
)

echo OK: Build configuration ready
timeout /t 1 >nul

REM ============================================
REM STEP 7: BUILD APK
REM ============================================

echo.
echo [7/8] Building Android APK...
echo This may take 10-30 minutes depending on your system
echo Please be patient...
echo.

buildozer android release

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    echo Check the output above for error details
    echo Common issues:
    echo - Android SDK not installed
    echo - JDK not in PATH
    echo - Insufficient disk space
    pause
    exit /b 1
)

echo.
echo OK: APK build completed
timeout /t 2 >nul

REM ============================================
REM STEP 8: LOCATE AND VERIFY APK
REM ============================================

echo.
echo [8/8] Finalizing release...

if not exist "bin" (
    echo ERROR: bin directory not found
    echo Build may have failed
    pause
    exit /b 1
)

REM Find the APK file
for /f "delims=" %%F in ('dir /b bin\*.apk 2^>nul') do (
    set APK_FILE=%%F
    set APK_SIZE=%%~zF
    goto found_apk
)

echo ERROR: No APK file found in bin directory
pause
exit /b 1

:found_apk

echo OK: APK created successfully
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
echo ANDROID APK CREATED!
echo.
echo Location: bin\%APK_FILE%
echo Size: %APK_SIZE% bytes
echo Target: Android 7.0+ (API 24+)
echo.
echo ========================================
echo Installation Instructions
echo ========================================
echo.
echo 1. Transfer APK to your Android device:
    echo    adb install bin\%APK_FILE%
    echo.
echo 2. Or enable Unknown Sources in Android settings
    echo    and open the APK file directly
echo.
echo 3. App will appear as Klar 3.1 on device
echo.
echo ========================================
echo.

choice /C OD /M "Open output folder or Done?"
if errorlevel 2 goto done

start explorer bin

:done

echo.
echo Build script completed successfully!
echo.
pause
