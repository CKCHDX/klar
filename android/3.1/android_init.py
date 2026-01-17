"""
Klar Android Initialization Module
Handles startup sequence and dependency initialization
"""

import sys
from pathlib import Path

# ============================================
# INITIALIZATION SEQUENCE
# ============================================

def init_klar_android():
    """Initialize Klar for Android"""
    print("[INIT] Starting Klar 3.1 Android initialization...")
    
    try:
        # Step 1: Configure paths and platform
        print("[INIT] Step 1: Configuring platform...")
        import android_config
        android_config.init_android_environment()
        print("[INIT] ✓ Platform configured")
        
        # Step 2: Initialize logging
        print("[INIT] Step 2: Initializing logging...")
        from android_logger import get_logger, log_platform_info
        logger = get_logger("KlarInit")
        logger.info("Initializing Klar Android")
        log_platform_info()
        print("[INIT] ✓ Logging initialized")
        
        # Step 3: Load engine
        print("[INIT] Step 3: Loading search engine...")
        from klar_engine_android import KlarEngine
        engine = KlarEngine()
        
        if not engine.search_engine:
            logger.error("Failed to initialize search engine")
            raise RuntimeError("Search engine not initialized")
        
        logger.info("Search engine loaded successfully")
        print("[INIT] ✓ Search engine loaded")
        
        # Step 4: Initialize communication bridge
        print("[INIT] Step 4: Initializing communication bridge...")
        from android_bridge import AsyncBridge
        bridge = AsyncBridge(engine)
        logger.info("Communication bridge initialized")
        print("[INIT] ✓ Communication bridge ready")
        
        # Step 5: Log status
        print("[INIT] Step 5: Logging engine status...")
        from android_logger import log_engine_status
        log_engine_status(engine)
        print("[INIT] ✓ Engine status logged")
        
        print("[INIT] ✓ Klar Android initialization complete!")
        logger.info("Klar Android initialization complete")
        
        return {
            "success": True,
            "engine": engine,
            "bridge": bridge,
            "logger": logger
        }
    
    except Exception as e:
        print(f"[INIT] ✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

def get_initialized_klar():
    """Get initialized Klar instance (with caching)"""
    if not hasattr(get_initialized_klar, "_instance"):
        get_initialized_klar._instance = init_klar_android()
    return get_initialized_klar._instance

# ============================================
# DEPENDENCY CHECKS
# ============================================

def check_dependencies():
    """Check if all dependencies are available"""
    dependencies = {
        "android_config": False,
        "android_logger": False,
        "android_bridge": False,
        "klar_engine_android": False,
        "search_engine": False,
        "demographic_detector": False,
        "domain_whitelist": False,
        "loki_system": False
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies

def print_dependency_status():
    """Print dependency status"""
    print("\n[DEPS] Checking dependencies...")
    deps = check_dependencies()
    
    for dep, available in deps.items():
        status = "✓" if available else "✗"
        print(f"[DEPS] {status} {dep}")
    
    all_available = all(deps.values())
    print(f"[DEPS] All dependencies available: {all_available}\n")
    
    return all_available

# ============================================
# STARTUP
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("Klar 3.1 Android Initialization")
    print("="*60)
    
    # Check dependencies
    if not print_dependency_status():
        print("[ERROR] Some dependencies are missing!")
        sys.exit(1)
    
    # Initialize
    result = init_klar_android()
    
    if result["success"]:
        print("\n[SUCCESS] Klar is ready!")
        sys.exit(0)
    else:
        print(f"\n[ERROR] {result['error']}")
        sys.exit(1)
