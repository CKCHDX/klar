#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic script to check if data files are bundled in PyInstaller EXE
Run this AFTER building the EXE to verify what's included
"""

import os
import sys
from pathlib import Path

print("="*60)
print("Klar Data Files Diagnostic")
print("="*60)
print()

# Check if running from PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    bundle_dir = Path(sys._MEIPASS)
    print("✓ Running from PyInstaller bundle")
    print(f"Bundle directory: {bundle_dir}")
else:
    # Running normally
    bundle_dir = Path(__file__).parent
    print("✓ Running from source (not bundled)")
    print(f"Source directory: {bundle_dir}")

print()
print("="*60)
print("Checking for data files...")
print("="*60)
print()

# List of files that should be bundled
required_files = [
    'domains.json',
    'keywords_db.json',
    'engine/search_engine.py',
    'engine/loki_system.py',
    'engine/__init__.py',
    'algorithms/wikipedia_handler.py',
    'algorithms/__init__.py',
]

all_ok = True

for file_path in required_files:
    full_path = bundle_dir / file_path
    exists = full_path.exists()
    status = "✓" if exists else "✗"
    
    if exists:
        size = full_path.stat().st_size
        print(f"{status} {file_path:40s} ({size:,} bytes)")
    else:
        print(f"{status} {file_path:40s} MISSING!")
        all_ok = False

print()
print("="*60)
print("Full directory listing:")
print("="*60)
print()

# Show everything in bundle directory
for item in sorted(bundle_dir.rglob('*')):
    if item.is_file():
        rel_path = item.relative_to(bundle_dir)
        size = item.stat().st_size
        print(f"  {rel_path} ({size:,} bytes)")

print()
print("="*60)

if all_ok:
    print("✓ All required files found!")
else:
    print("✗ Some files are MISSING!")
    print("  The EXE will not work correctly.")
    print("  Rebuild with release.bat")

print("="*60)
print()

input("Press Enter to exit...")
