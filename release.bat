@echo off
setlocal enabledelayedexpansion
cls

echo.
echo ========================================
echo   Klar 3.0 - Single-File Build System
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
echo [1/9] Checking Python...
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
echo [2/9] Setting up virtual environment...
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
echo [3/9] Checking file integrity...

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
if not exist "engine\results_page.py" (
    echo ERROR: Missing engine\results_page.py
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
echo [4/9] Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install PyQt6 PyQt6-WebEngine requests beautifulsoup4 lxml pyinstaller pillow >nul 2>&1
echo OK: Dependencies installed
timeout /t 1 >nul

REM ============================================
REM STEP 5: CLEAN OLD BUILDS
REM ============================================
echo.
echo [5/9] Cleaning old builds...
if exist "dist" rmdir /s /q dist 2>nul
if exist "build" rmdir /s /q build 2>nul
if exist "release" rmdir /s /q release 2>nul
if exist "klar.spec" del /q klar.spec 2>nul
echo OK: Build directories cleaned
timeout /t 1 >nul

REM ============================================
REM STEP 6: CREATE PYINSTALLER SPEC
REM ============================================
echo.
echo [6/9] Creating single-file build configuration...

(
echo # -*- mode: python ; coding: utf-8 -*-
echo import sys
echo from pathlib import Path
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['klar_browser.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[
echo         ^('keywords_db.json', '.'^),
echo         ^('domains.json', '.'^),
echo         ^('engine/__init__.py', 'engine'^),
echo         ^('engine/search_engine.py', 'engine'^),
echo         ^('engine/results_page.py', 'engine'^)
echo     ],
echo     hiddenimports=[
echo         'PyQt6.QtCore',
echo         'PyQt6.QtGui',
echo         'PyQt6.QtWidgets',
echo         'PyQt6.QtWebEngineWidgets',
echo         'PyQt6.QtWebEngineCore',
echo         'PyQt6.sip',
echo         'requests',
echo         'bs4',
echo         'lxml',
echo         'urllib3',
echo         'certifi'
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='Klar',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo ^)
) > klar.spec

echo OK: Single-file configuration created
timeout /t 1 >nul

REM ============================================
REM STEP 7: BUILD SINGLE-FILE EXECUTABLE
REM ============================================
echo.
echo [7/9] Building single-file Windows executable...
echo This may take 3-7 minutes, please wait...
echo.

pyinstaller --clean --noconfirm klar.spec

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
REM STEP 8: CREATE RELEASE STRUCTURE
REM ============================================
echo.
echo [8/9] Creating release packages...

REM Create directories
mkdir release 2>nul
mkdir release\windows 2>nul
mkdir release\linux 2>nul

REM Copy Windows executable
echo Packaging Windows release...
copy "dist\Klar.exe" "release\windows\Klar.exe" >nul

REM Get file size
for %%F in ("release\windows\Klar.exe") do set FILESIZE=%%~zF

REM Create Windows README
(
    echo ============================================
    echo   Klar 3.0 - Swedish Browser
    echo ============================================
    echo.
    echo STANDALONE SINGLE-FILE EXECUTABLE
    echo No installation required!
    echo.
    echo Installation:
    echo   1. Just run Klar.exe
    echo   2. That's it!
    echo.
    echo File: Klar.exe (Single file, all-in-one^)
    echo Size: %FILESIZE% bytes
    echo.
    echo System Requirements:
    echo   - Windows 10 or Windows 11
    echo   - 4GB RAM minimum
    echo   - Internet connection for searches
    echo.
    echo Features:
    echo   - 111 Swedish domains
    echo   - 700+ keywords
    echo   - No tracking or ads
    echo   - Fast search engine
    echo   - Dark mode interface
    echo   - Completely standalone
    echo   - No external files needed
    echo.
    echo First Run:
    echo   - May take 5-10 seconds to start (unpacking^)
    echo   - After first run, starts instantly
    echo.
    echo Support:
    echo   https://github.com/CKCHDX/klar
    echo.
    echo Version: 3.0.0
    echo Build Date: %date%
    echo Build Type: Single-File Executable
    echo.
) > "release\windows\README.txt"

REM Copy Linux files
echo Packaging Linux release...
copy "klar_browser.py" "release\linux\" >nul 2>&1
copy "keywords_db.json" "release\linux\" >nul 2>&1
copy "domains.json" "release\linux\" >nul 2>&1
xcopy /E /I /Q "engine" "release\linux\engine\" >nul 2>&1

REM Create Linux build script
(
    echo #!/bin/bash
    echo echo "============================================"
    echo echo "  Klar 3.0 - Linux Single-File Build"
    echo echo "============================================"
    echo echo
    echo echo "[1/4] Creating virtual environment..."
    echo python3 -m venv venv
    echo source venv/bin/activate
    echo echo
    echo echo "[2/4] Installing dependencies..."
    echo pip install PyQt6 PyQt6-WebEngine requests beautifulsoup4 lxml
    echo echo
    echo echo "[3/4] Installing PyInstaller..."
    echo pip install pyinstaller
    echo echo
    echo echo "[4/4] Building single-file executable..."
    echo pyinstaller --onefile --windowed --add-data "keywords_db.json:." --add-data "domains.json:." --add-data "engine:engine" --name Klar klar_browser.py
    echo echo
    echo echo "============================================"
    echo echo "  Build Complete!"
    echo echo "============================================"
    echo echo
    echo echo "Single file created: ./dist/Klar"
    echo echo "Run with: ./dist/Klar"
    echo echo
) > "release\linux\build_linux.sh"

REM Create Linux README
(
    echo # Klar 3.0 - Swedish Browser (Linux Single-File^)
    echo.
    echo ## Build Instructions
    echo.
    echo 1. Make executable: `chmod +x build_linux.sh`
    echo 2. Run build: `./build_linux.sh`
    echo 3. Run Klar: `./dist/Klar`
    echo.
    echo This creates a single standalone file with everything embedded.
    echo.
    echo ## System Requirements
    echo.
    echo - Ubuntu 20.04+ / Debian 11+ / Fedora 35+
    echo - Python 3.8+
    echo - 4GB RAM minimum
    echo.
) > "release\linux\README.md"

echo OK: Release packages created
timeout /t 1 >nul

REM ============================================
REM STEP 9: GENERATE CHECKSUMS AND INFO
REM ============================================
echo.
echo [9/9] Generating checksums and version info...

REM Generate checksum for Windows exe
pushd release\windows
certutil -hashfile "Klar.exe" SHA256 > "Klar.SHA256.txt" 2>nul
popd

REM Create version file
(
    echo ============================================
    echo   Klar 3.0 - Release Information
    echo ============================================
    echo.
    echo Build Date: %date% %time%
    echo Version: 3.0.0
    echo Build Type: Single-File Executable
    echo.
    echo Components:
    echo   - Browser Engine: PyQt6-WebEngine
    echo   - Search Engine: DOSSNA Algorithm
    echo   - Swedish Domains: 111
    echo   - Keywords Database: 700+ phrases
    echo   - Categories: 12
    echo.
    echo Windows Executable:
    echo   - File: Klar.exe
    echo   - Size: %FILESIZE% bytes
    echo   - Type: Standalone single-file
    echo   - No external files needed
    echo   - All data embedded
    echo.
    echo Platforms:
    echo   - Windows 10/11 (64-bit^)
    echo   - Linux (Ubuntu/Debian/Fedora^)
    echo.
    echo Build Information:
    for /f "tokens=*" %%i in ('python --version') do echo   - %%i
    for /f "tokens=*" %%i in ('python -c "import PyQt6.QtCore; print('PyQt6', PyQt6.QtCore.PYQT_VERSION_STR)"') do echo   - %%i
    echo.
) > "release\VERSION.txt"

REM Create distribution ZIP
echo Creating distribution archive...
if exist "release\Klar-3.0-Windows-Standalone.zip" del /q "release\Klar-3.0-Windows-Standalone.zip"
powershell -command "Compress-Archive -Path 'release\windows\*' -DestinationPath 'release\Klar-3.0-Windows-Standalone.zip'" 2>nul

REM Linux tar.gz
if exist "release\Klar-3.0-Linux.tar.gz" del /q "release\Klar-3.0-Linux.tar.gz"
pushd release\linux
tar -czf "..\Klar-3.0-Linux.tar.gz" * 2>nul
popd

echo OK: Checksums and archives created
timeout /t 1 >nul

REM ============================================
REM COMPLETION
REM ============================================
cls
echo.
echo ========================================
echo   BUILD COMPLETE!
echo ========================================
echo.
echo SINGLE-FILE EXECUTABLE CREATED!
echo.
echo Windows:
echo   Location: release\windows\Klar.exe
echo   Size: %FILESIZE% bytes
echo   Type: Standalone (no external files^)
echo.
echo Package: release\Klar-3.0-Windows-Standalone.zip
echo.
echo Linux:
echo   Source: release\linux\
echo   Package: release\Klar-3.0-Linux.tar.gz
echo.
echo Documentation:
echo   - Windows: release\windows\README.txt
echo   - Linux: release\linux\README.md
echo   - Version: release\VERSION.txt
echo.
echo ========================================
echo   What You Can Distribute
echo ========================================
echo.
echo Option 1: Just the EXE
echo   Send: Klar.exe (single file^)
echo   Users run it - that's all!
echo.
echo Option 2: With README
echo   Send: Klar-3.0-Windows-Standalone.zip
echo   Contains: Klar.exe + README.txt
echo.
echo ========================================
echo.

REM Ask if user wants to test now
choice /C YN /M "Do you want to test the executable now"
if errorlevel 2 goto :end

echo.
echo Launching Klar...
echo (First launch may take 5-10 seconds to unpack^)
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