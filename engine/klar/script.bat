@echo off
setlocal enabledelayedexpansion

:: -------------------------------
:: Klar Search Engine Build Script
:: -------------------------------

echo ========================================
echo Cleaning previous builds...
echo ========================================

:: Remove previous build, dist folders, and spec file
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist klar.spec del /q klar.spec

:: -------------------------------
echo Building Klar search engine executable...
echo --------------------------------

:: Run PyInstaller with all hidden imports and data
python -m PyInstaller --onefile --windowed ^
  --hidden-import=PyQt5.sip ^
  --hidden-import=PyQt5.QtCore ^
  --hidden-import=PyQt5.QtGui ^
  --hidden-import=PyQt5.QtWidgets ^
  --hidden-import=PyQt5.QtWebEngineWidgets ^
  --hidden-import=PyQt5.QtWebChannel ^
  --exclude-module PySide6 ^
  --add-data "domains.json;." ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  browser.py

:: Check if PyInstaller failed
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: PyInstaller build failed!
    echo Check above output for details.
    echo ========================================
    pause
    exit /b 1
)

:: -------------------------------
echo Organizing dist directory for release...
echo --------------------------------

:: Create windows dist folder if missing
if not exist dist\windows mkdir dist\windows

:: Move executable only if it exists
if exist dist\browser.exe (
    move /Y dist\browser.exe dist\windows\browser.exe
    echo.
    echo ========================================
    echo Build finished successfully!
    echo Windows executable is in dist\windows\browser.exe
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ERROR: browser.exe was not created!
    echo ========================================
)

pause
