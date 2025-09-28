#!/bin/bash
set -e

echo "Cleaning previous builds..."
rm -rf build dist klar.spec

echo "Building Klar search engine executable..."

SEP=";"
if [[ "$OSTYPE" == "darwin"* || "$OSTYPE" == "linux-gnu"* ]]; then
  SEP=":"
fi

pyinstaller --onefile --windowed \
  --hidden-import=PyQt5.sip \
  --hidden-import=PyQt5.QtCore \
  --hidden-import=PyQt5.QtGui \
  --hidden-import=PyQt5.QtWidgets \
  --hidden-import=PyQt5.QtWebEngineWidgets \
  --hidden-import=PyQt5.QtWebChannel \
  --add-data "domains.json${SEP}." \
  --add-data "templates${SEP}templates" \
  --add-data "static${SEP}static" \
  browser.py

echo "Build finished. Executable is in dist/browser <=no format"
echo "Convert. To make this as windows executable please run script.bat"