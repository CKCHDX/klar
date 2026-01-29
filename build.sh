#!/bin/bash

# Klar 3.1 - Build Script for Linux/macOS
# This script builds a standalone executable for Linux/macOS

set -e  # Exit on error

clear

echo ""
echo "========================================"
echo "Klar 3.1 - Build System (Linux/macOS)"
echo "========================================"
echo ""
echo "This will create a standalone executable"
echo "with all dependencies embedded."
echo ""
read -p "Press Enter to continue..."

# ============================================
# STEP 1: CHECK PYTHON
# ============================================

echo ""
echo "[1/7] Checking Python..."
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

PYTHON_VER=$($PYTHON_CMD --version)
echo "OK: $PYTHON_VER found"
sleep 1

# ============================================
# STEP 2: SETUP VIRTUAL ENVIRONMENT
# ============================================

echo ""
echo "[2/7] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate
echo "OK: Virtual environment ready"
sleep 1

# ============================================
# STEP 3: CHECK FILE INTEGRITY
# ============================================

echo ""
echo "[3/7] Checking file integrity..."
ERROR_COUNT=0

if [ ! -f "klar_browser.py" ]; then
    echo "ERROR: Missing klar_browser.py"
    ((ERROR_COUNT++))
fi

if [ ! -f "keywords_db.json" ]; then
    echo "ERROR: Missing keywords_db.json"
    ((ERROR_COUNT++))
fi

if [ ! -f "domains.json" ]; then
    echo "ERROR: Missing domains.json"
    ((ERROR_COUNT++))
fi

if [ ! -f "klar.ico" ]; then
    echo "ERROR: Missing klar.ico"
    ((ERROR_COUNT++))
fi

if [ $ERROR_COUNT -gt 0 ]; then
    echo ""
    echo "FAILED: $ERROR_COUNT files missing"
    exit 1
fi

# Validate JSON files
python -c "import json; json.load(open('keywords_db.json', encoding='utf-8'))" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: keywords_db.json has syntax errors"
    exit 1
fi

python -c "import json; json.load(open('domains.json', encoding='utf-8'))" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: domains.json has syntax errors"
    exit 1
fi

python -m py_compile klar_browser.py 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: klar_browser.py has syntax errors"
    exit 1
fi

echo "OK: All files validated"
sleep 1

# ============================================
# STEP 4: INSTALL DEPENDENCIES
# ============================================

echo ""
echo "[4/7] Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install PyQt6 PyQt6-WebEngine requests beautifulsoup4 lxml pyinstaller > /dev/null 2>&1
echo "OK: Dependencies installed"
sleep 1

# ============================================
# STEP 5: CLEAN OLD BUILDS
# ============================================

echo ""
echo "[5/7] Cleaning old builds..."
rm -rf dist build release Klar.spec 2>/dev/null
echo "OK: Build directories cleaned"
sleep 1

# ============================================
# STEP 6: BUILD WITH PYINSTALLER
# ============================================

echo ""
echo "[6/7] Building single-file executable..."
echo "This may take 3-7 minutes, please wait..."
echo ""

# Build with PyInstaller
python -m PyInstaller \
    --onefile \
    --windowed \
    --icon=klar.ico \
    --add-data "keywords_db.json:." \
    --add-data "domains.json:." \
    --add-data "klar.ico:." \
    --add-data "engine:engine" \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=PyQt6.QtWidgets \
    --hidden-import=PyQt6.QtWebEngineWidgets \
    --hidden-import=PyQt6.QtWebEngineCore \
    --hidden-import=PyQt6.sip \
    --hidden-import=requests \
    --hidden-import=bs4 \
    --hidden-import=lxml \
    --hidden-import=engine.domain_whitelist \
    --hidden-import=engine.demographic_detector \
    --hidden-import=engine.loki_system \
    --hidden-import=engine.setup_wizard \
    --exclude-module PySide6 \
    --name=Klar \
    klar_browser.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed"
    echo "Check the output above for errors"
    exit 1
fi

if [ ! -f "dist/Klar" ]; then
    echo ""
    echo "ERROR: Klar executable was not created"
    exit 1
fi

echo ""
echo "OK: Single-file executable built successfully"
sleep 2

# ============================================
# STEP 7: CREATE RELEASE STRUCTURE
# ============================================

echo ""
echo "[7/7] Creating release packages..."

mkdir -p release/linux

echo "Packaging Linux release..."
cp dist/Klar release/linux/Klar
chmod +x release/linux/Klar

FILESIZE=$(stat -f%z "release/linux/Klar" 2>/dev/null || stat -c%s "release/linux/Klar")
FILESIZE_MB=$((FILESIZE / 1024 / 1024))

echo "Building complete! Klar executable is ready."
sleep 1

# ============================================
# COMPLETION
# ============================================

clear

echo ""
echo "========================================"
echo "BUILD COMPLETE!"
echo "========================================"
echo ""
echo "SINGLE-FILE EXECUTABLE CREATED!"
echo ""
echo "Linux/macOS:"
echo "Location: release/linux/Klar"
echo "Size: ${FILESIZE_MB}MB"
echo "Type: Standalone (no external files)"
echo ""
echo "========================================"
echo "What You Can Distribute"
echo "========================================"
echo ""
echo "Just send: release/linux/Klar"
echo "Users run it - that's all!"
echo ""
echo "========================================"
echo ""

# Ask if user wants to test now
read -p "Do you want to test the executable now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Launching Klar..."
    echo "(First launch may take 5-10 seconds to unpack)"
    echo ""
    
    ./release/linux/Klar &
    sleep 5
fi

echo ""
echo "Build script completed successfully!"
echo ""
echo "The file release/linux/Klar is completely standalone."
echo "No other files needed - just distribute this single file!"
echo ""
