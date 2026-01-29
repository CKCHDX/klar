#!/usr/bin/env python3
"""
Start GUI - Entry point for launching the Klar Search Engine GUI
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = ['tkinter']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"ERROR: Missing required dependencies: {', '.join(missing)}")
        print("\nPlease install missing dependencies:")
        print("  - tkinter is usually included with Python")
        print("  - On Linux: sudo apt-get install python3-tk")
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
        return 1
    print("✓ All dependencies installed")
    print()
    
    # Launch GUI
    print("Launching KSE GUI...")
    print()
    
    try:
        from gui.kse_gui_main import main as gui_main
        return gui_main()
    except ImportError as e:
        print(f"ERROR: Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
