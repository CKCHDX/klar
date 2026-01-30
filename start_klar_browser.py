#!/usr/bin/env python3
"""
Start Klar Browser Client
Simple launcher script for the Klar Browser client application
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Launch Klar Browser"""
    print("="*60)
    print("Klar Browser - KSE Search Client")
    print("="*60)
    
    # Check for environment variable
    server_url = os.getenv("KSE_SERVER_URL")
    if server_url:
        print(f"Using server URL from environment: {server_url}")
    else:
        print("Using default or configured server URL")
        print("To connect to a remote server, set KSE_SERVER_URL environment variable:")
        print("  export KSE_SERVER_URL=http://YOUR_SERVER_IP:5000")
    
    print("\nStarting Klar Browser...")
    print("-"*60)
    
    # Import and run
    try:
        from klar_browser import main as browser_main
        browser_main()
    except ImportError as e:
        print(f"\nError: Failed to import Klar Browser: {e}")
        print("\nMake sure you have installed the requirements:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\nError starting Klar Browser: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
