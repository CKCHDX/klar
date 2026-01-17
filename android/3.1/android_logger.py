"""
Klar Android Logging Module
Centralized logging for both Android and Desktop
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

try:
    from android_config import get_logs_dir, is_android
except ImportError:
    # Fallback if module not available
    def get_logs_dir():
        return Path.home() / "Klar-logs"
    def is_android():
        try:
            import android
            return True
        except:
            return False

# ============================================
# LOGGER SETUP
# ============================================

class AndroidLogger:
    """Centralized logger for Klar Android"""
    
    def __init__(self, name="Klar"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Create formatters
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(name)s: %(message)s'
        )
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler (always)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        try:\n            logs_dir = get_logs_dir()
            log_file = logs_dir / f\"klar_{datetime.now().strftime('%Y%m%d')}.log\"
            file_handler = logging.FileHandler(str(log_file))
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f\"Could not setup file logging: {e}\")\n    \n    def debug(self, msg, *args, **kwargs):\n        self.logger.debug(msg, *args, **kwargs)\n    \n    def info(self, msg, *args, **kwargs):\n        self.logger.info(msg, *args, **kwargs)\n    \n    def warning(self, msg, *args, **kwargs):\n        self.logger.warning(msg, *args, **kwargs)\n    \n    def error(self, msg, *args, **kwargs):\n        self.logger.error(msg, *args, **kwargs)\n    \n    def critical(self, msg, *args, **kwargs):\n        self.logger.critical(msg, *args, **kwargs)\n\n# ============================================\n# GLOBAL LOGGER INSTANCE\n# ============================================\n\n_logger = AndroidLogger()\n\ndef get_logger(name=None):\n    \"\"\"Get logger instance\"\"\"\n    if name:\n        return logging.getLogger(name)\n    return _logger\n\ndef log_platform_info():\n    \"\"\"Log platform information\"\"\"\n    try:\n        from android_config import get_platform_info\n        info = get_platform_info()\n        _logger.info(f\"Platform: Android\" if info[\"is_android\"] else \"Platform: Desktop\")\n        _logger.info(f\"Python: {info['python_version']}\")\n        _logger.debug(f\"App data dir: {info['app_data_dir']}\")\n    except Exception as e:\n        _logger.warning(f\"Could not log platform info: {e}\")\n\ndef log_engine_status(engine):\n    \"\"\"Log engine initialization status\"\"\"\n    try:\n        import json\n        status = json.loads(engine.get_status())\n        _logger.info(f\"Engine version: {status.get('version')}\")\n        _logger.info(f\"Engine initialized: {status.get('initialized')}\")\n        _logger.info(f\"LOKI enabled: {status.get('loki_enabled')}\")\n        _logger.info(f\"Whitelist available: {status.get('has_whitelist')}\")\n    except Exception as e:\n        _logger.error(f\"Could not log engine status: {e}\")\n\n# ============================================\n# INITIALIZATION\n# ============================================\n\n# Log startup\nif is_android():\n    _logger.info(\"=\" * 50)\n    _logger.info(\"Klar 3.1 Android Logger Initialized\")\n    _logger.info(\"=\" * 50)\nelse:\n    _logger.info(\"=\" * 50)\n    _logger.info(\"Klar 3.1 Desktop Logger Initialized\")\n    _logger.info(\"=\" * 50)\n\nlog_platform_info()\n"