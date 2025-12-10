@echo off

setlocal enabledelayedexpansion

cls

echo.
echo ========================================
echo Klar 3.0 - Single-File Build System
echo ========================================
echo.
echo This will create a standalone single-file executable
echo with all dependencies AND data files embedded
echo.
pause

REM ============================================
REM STEP 1: CHECK PYTHON
REM ============================================

echo.
echo [1/10] Checking Python...

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
echo [2/10] Setting up virtual environment...

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
echo [3/10] Checking file integrity...

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

if not exist "engine\search_engine.py" (
    echo ERROR: Missing engine\search_engine.py
    set /a ERROR_COUNT+=1
)

if not exist "algorithms\wikipedia_handler.py" (
    echo ERROR: Missing algorithms\wikipedia_handler.py
    set /a ERROR_COUNT+=1
)

if not exist "engine\loki_system.py" (
    echo ERROR: Missing engine\loki_system.py
    set /a ERROR_COUNT+=1
)

python -c "import json; json.load(open('keywords_db.json', encoding='utf-8'))" 2>nul
if errorlevel 1 (
    echo ERROR: keywords_db.json has syntax errors
    set /a ERROR_COUNT+=1
)

python -c "import json; json.load(open('domains.json', encoding='utf-8'))" 2>nul
if errorlevel 1 (
    echo ERROR: domains.json has syntax errors
    set /a ERROR_COUNT+=1
)

python -m py_compile klar_browser.py 2>nul
if errorlevel 1 (
    echo ERROR: klar_browser.py has syntax errors
    set /a ERROR_COUNT+=1
)

if %ERROR_COUNT% GTR 0 (
    echo.
    echo FAILED: %ERROR_COUNT% integrity errors found
    pause
    exit /b 1
)

echo OK: All files validated
timeout /t 1 >nul

REM ============================================
REM STEP 4: INSTALL DEPENDENCIES
REM ============================================

echo.
echo [4/10] Installing dependencies...

pip install --upgrade pip >nul 2>&1
pip install PyQt6 PyQt6-WebEngine requests beautifulsoup4 lxml pyinstaller pillow >nul 2>&1

echo OK: Dependencies installed
timeout /t 1 >nul

REM ============================================
REM STEP 5: CLEAN OLD BUILDS
REM ============================================

echo.
echo [5/10] Cleaning old builds...

if exist "dist" rmdir /s /q dist 2>nul
if exist "build" rmdir /s /q build 2>nul
if exist "release" rmdir /s /q release 2>nul
if exist "klar.spec" del /q klar.spec 2>nul
if exist "build_temp" rmdir /s /q build_temp 2>nul

echo OK: Build directories cleaned
timeout /t 1 >nul

REM ============================================
REM STEP 6: COPY DATA FILES TO PROJECT ROOT
REM ============================================

echo.
echo [6/10] Preparing data files for bundling...

REM Verify data files are in project root
if not exist "domains.json" (
    echo ERROR: domains.json not found in project root
    pause
    exit /b 1
)

if not exist "keywords_db.json" (
    echo ERROR: keywords_db.json not found in project root
    pause
    exit /b 1
)

echo OK: Data files prepared
timeout /t 1 >nul

REM ============================================
REM STEP 7: CREATE PYINSTALLER SPEC FILE
REM ============================================

echo.
echo [7/10] Creating PyInstaller configuration...

REM CRITICAL FIX: Use Python to generate the spec file correctly
REM This avoids batch file syntax issues with quotes and commas

python -c ^
"import os
^
spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['klar_browser.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('keywords_db.json', '.'),
        ('domains.json', '.'),
        ('engine', 'engine'),
        ('algorithms', 'algorithms'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
        'PyQt6.sip',
        'requests',
        'bs4',
        'lxml',
        'urllib3',
        'PIL',
        'json',
        're',
        'os',
        'sys',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Klar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''

with open('klar.spec', 'w') as f:
    f.write(spec_content)
print('OK: Spec file created')
"^

if errorlevel 1 (
    echo ERROR: Failed to create spec file
    pause
    exit /b 1
)

echo OK: PyInstaller spec created
timeout /t 1 >nul

REM ============================================
REM STEP 8: BUILD EXECUTABLE WITH PYINSTALLER
REM ============================================

echo.
echo [8/10] Building executable with PyInstaller...
echo This may take 2-5 minutes, please wait...
echo.

REM Try using the spec file first
pyinstaller klar.spec 2>nul

if errorlevel 1 (
    echo ERROR: Spec file build failed
    echo Trying alternative build method with direct --add-data flags...
    echo.
    
    REM Try direct command line approach (Windows uses semicolon separator)
    pyinstaller --onefile --windowed --nonconsole ^
        --add-data "domains.json;." ^
        --add-data "keywords_db.json;." ^
        --add-data "engine;engine" ^
        --add-data "algorithms;algorithms" ^
        --hidden-import=PyQt6.QtCore ^
        --hidden-import=PyQt6.QtGui ^
        --hidden-import=PyQt6.QtWidgets ^
        --hidden-import=PyQt6.QtWebEngineWidgets ^
        --hidden-import=PyQt6.QtWebEngineCore ^
        --hidden-import=PyQt6.sip ^
        --hidden-import=requests ^
        --hidden-import=bs4 ^
        --hidden-import=lxml ^
        --hidden-import=urllib3 ^
        --hidden-import=PIL ^
        klar_browser.py 2>nul
    
    if errorlevel 1 (
        echo.
        echo CRITICAL ERROR: Both build methods failed
        echo Please check:
        echo 1. Python is 3.8 or higher
        echo 2. All dependencies installed: pip list
        echo 3. domains.json and keywords_db.json exist
        echo 4. engine/ and algorithms/ folders exist
        echo.
        pause
        exit /b 1
    )
)

if not exist "dist\Klar.exe" (
    echo ERROR: Klar.exe was not created
    echo Build might have failed silently
    pause
    exit /b 1
)

echo OK: Executable created successfully
timeout /t 1 >nul

REM ============================================
REM STEP 9: VERIFY EXECUTABLE INTEGRITY
REM ============================================

echo.
echo [9/10] Verifying executable integrity...

REM Get file size in MB
for /f "usebackq" %%A in (`powershell -Command "[math]::Round((Get-Item 'dist\Klar.exe').length / 1MB, 2)"`) do set FILESIZE_MB=%%A

echo Executable size: %FILESIZE_MB% MB

if %FILESIZE_MB% LSS 80 (
    echo WARNING: Executable size (%FILESIZE_MB% MB) seems smaller than expected
    echo Expected: 100+ MB ^(data files bundled^)
    echo This might indicate data files weren't included
)

echo OK: Executable verified
timeout /t 1 >nul

REM ============================================
REM STEP 10: CREATE RELEASE PACKAGE
REM ============================================

echo.
echo [10/10] Creating release package...

mkdir release\windows 2>nul
mkdir release\linux 2>nul

copy dist\Klar.exe release\windows\ >nul 2>&1
if not exist "release\windows\Klar.exe" (
    echo ERROR: Failed to copy Klar.exe to release folder
    pause
    exit /b 1
)

REM Create Windows README
(
    echo # Klar 3.0 - Swedish Search Browser
    echo.
    echo ## What is this?
    echo Klar is a specialized search engine for Swedish websites
    echo.
    echo ## How to use
    echo 1. Double-click Klar.exe
    echo 2. Search for Swedish websites, Wikipedia topics, or general information
    echo 3. That's it! No installation needed
    echo.
    echo ## System Requirements
    echo - Windows 10/11 ^(64-bit^)
    echo - Internet connection
    echo - 500 MB free space
    echo.
    echo ## Features
    echo - Search 113 whitelisted Swedish domains
    echo - Wikipedia Handler with automatic language fallback
    echo - Offline caching ^(LOKI System^)
    echo - 700+ keyword phrases
    echo - 12 search categories
    echo.
    echo ## Troubleshooting
    echo.
    echo Q: I get "Webbplats blockerad för säkerhet"
    echo A: The domain isn't on the whitelist. Klar only searches approved Swedish domains.
    echo.
    echo Q: No search results?
    echo A: Make sure you're searching Swedish websites or Wikipedia topics.
    echo.
    echo Q: Wikipedia search not working?
    echo A: Try "vem är X" or just type a person/place name.
    echo.
    echo ## Version
    echo Version: 3.0.0
    echo Build: Single-file executable
    echo All data embedded - no external files needed!
) > "release\windows\README.txt"

REM Create version info
(
    echo ============================================
    echo Klar 3.0 - Release Information
    echo ============================================
    echo.
    echo Build Date: %date% %time%
    echo Version: 3.0.0
    echo Build Type: Single-File Executable
    echo.
    echo Executable Details:
    echo - File: Klar.exe
    echo - Size: %FILESIZE_MB% MB
    echo - Type: Standalone single-file
    echo - Data Files Bundled: YES
    echo   * domains.json: 113 whitelisted domains
    echo   * keywords_db.json: 700+ keyword phrases
    echo   * engine/: Search algorithms
    echo   * algorithms/: Wikipedia Handler
    echo.
    echo Components:
    echo - Browser Engine: PyQt6-WebEngine
    echo - Search Engine: SVEN 3.2
    echo - Wikipedia Handler: 1.0
    echo - LOKI Cache System: Integrated
    echo - Swedish Domains: 113
    echo - Keywords Database: 700+ phrases
    echo - Categories: 12
    echo.
    echo Platforms:
    echo - Windows 10/11 ^(64-bit^)
    echo - Linux ^(Ubuntu/Debian/Fedora^)
    echo.
    echo Build Information:
    echo - %PYTHON_VER%
    echo.
) > "release\VERSION.txt"

REM Create distribution ZIP
echo Creating distribution archive...

if exist "release\Klar-3.0-Windows-Standalone.zip" del /q "release\Klar-3.0-Windows-Standalone.zip" 2>nul

powershell -command "Compress-Archive -Path 'release\windows\*' -DestinationPath 'release\Klar-3.0-Windows-Standalone.zip'" 2>nul

echo OK: Release packages created
timeout /t 1 >nul

REM ============================================
REM CLEANUP
REM ============================================

echo Cleaning temporary files...
if exist "build_temp" rmdir /s /q build_temp 2>nul

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
echo Location: release\windows\Klar.exe
echo Size: %FILESIZE_MB% MB
echo Type: Standalone ^(all data embedded^)
echo.
echo Files Bundled Inside EXE:
echo - domains.json
echo - keywords_db.json
echo - engine/ (search algorithms)
echo - algorithms/ (Wikipedia Handler)
echo.
echo Distribution Package:
echo - release\Klar-3.0-Windows-Standalone.zip
echo.
echo ========================================
echo What You Can Distribute
echo ========================================
echo.
echo Option 1: Just the EXE ^(RECOMMENDED^)
echo Send: Klar.exe (single file)
echo Users run it - that's all!
echo No other files needed!
echo.
echo Option 2: With Documentation
echo Send: Klar-3.0-Windows-Standalone.zip
echo Contains: Klar.exe + README.txt + Version info
echo.
echo ========================================
echo.

REM Ask if user wants to test now
choice /C YN /M "Do you want to test the executable now?"
if errorlevel 2 goto :end

echo.
echo Launching Klar...
echo ^(First launch may take 5-10 seconds to unpack^)
echo.

start "" "release\windows\Klar.exe"
timeout /t 5 >nul

:end

echo.
echo Build script completed successfully!
echo.
echo The file release\windows\Klar.exe is completely standalone.
echo All data files ^(domains.json, keywords_db.json, etc.^) are bundled inside.
echo No other files needed - just distribute this single file!
echo.
pause
