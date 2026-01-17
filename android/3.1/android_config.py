"""
Klar Android Configuration Module
Handles platform detection, paths, and environment setup
"""

import sys
import os
from pathlib import Path

# ============================================
# PLATFORM DETECTION
# ============================================
def is_android():
    """Detect if running on Android"""
    try:
        import android
        return True
    except ImportError:
        return False

def is_desktop():
    """Detect if running on desktop"""
    return not is_android()

# ============================================
# PLATFORM-SPECIFIC PATHS
# ============================================
def get_app_data_dir():
    """Get app-specific data directory"""
    if is_android():
        try:
            from android.app import PythonActivity
            context = PythonActivity.mActivity
            return Path(context.getFilesDir().toString())
        except:
            return Path.home() / "Klar-Android"
    else:
        return Path.home() / "Klar-data"

def get_engine_path():
    """Get path to engine directory"""
    base = Path(__file__).parent
    engine_dir = base / "engine"
    return engine_dir if engine_dir.exists() else base

def get_cache_dir():
    """Get cache directory"""
    data_dir = get_app_data_dir()
    cache_dir = data_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_logs_dir():
    """Get logs directory"""
    data_dir = get_app_data_dir()
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def get_storage_dir():
    """Get external storage directory (Android specific)"""
    if is_android():
        try:
            from android.app import PythonActivity
            from android.content import Context
            context = PythonActivity.mActivity
            storage = context.getExternalFilesDir(None)
            return Path(storage.toString()) if storage else get_app_data_dir()
        except:
            return get_app_data_dir()
    else:
        return get_app_data_dir()

# ============================================
# ENVIRONMENT SETUP
# ============================================
def setup_paths():
    """Setup Python paths for module imports"""
    engine_path = get_engine_path()
    base_path = Path(__file__).parent
    
    if str(engine_path) not in sys.path:
        sys.path.insert(0, str(engine_path))
    if str(base_path) not in sys.path:
        sys.path.insert(0, str(base_path))

def get_platform_info():
    """Get detailed platform information"""
    return {
        "is_android": is_android(),
        "is_desktop": is_desktop(),
        "app_data_dir": str(get_app_data_dir()),
        "engine_path": str(get_engine_path()),
        "cache_dir": str(get_cache_dir()),
        "logs_dir": str(get_logs_dir()),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "platform": sys.platform
    }

# ============================================
# INITIALIZATION
# ============================================
def init_android_environment():
    """Initialize Android-specific environment"""
    if is_android():
        # Setup directories
        get_cache_dir()
        get_logs_dir()
        get_storage_dir()
        
        # Setup paths
        setup_paths()
        
        print("[INFO] Android environment initialized")
    else:
        setup_paths()
        print("[INFO] Desktop environment initialized")

# Auto-initialize on import
init_android_environment()
