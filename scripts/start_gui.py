#!/usr/bin/env python3
"""
KSE GUI Launcher
Startup script to launch the KSE GUI application
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing = []
    
    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6")
    
    try:
        import yaml
    except ImportError:
        missing.append("PyYAML")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    if missing:
        print("ERROR: Missing required dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with: pip install", " ".join(missing))
        return False
    
    return True


def main():
    """Main entry point"""
    print("=" * 60)
    print("🔍 Klar Search Engine - GUI Application")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ All dependencies installed")
    print()
    
    # Launch GUI
    print("Launching KSE GUI...")
    print()
    
    try:
        from gui.kse_gui_main import main as gui_main
        sys.exit(gui_main())
    except Exception as e:
        print(f"ERROR: Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
