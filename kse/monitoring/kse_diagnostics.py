"""
Diagnostics - System diagnostics and troubleshooting tools
"""

import logging
from typing import Dict, Any
import sys
import platform
from pathlib import Path

logger = logging.getLogger(__name__)


class Diagnostics:
    """System diagnostics tools"""
    
    def __init__(self):
        """Initialize diagnostics"""
        logger.info("Diagnostics initialized")
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """
        Run full system diagnostic
        
        Returns:
            Diagnostic report
        """
        return {
            'system_info': self.get_system_info(),
            'python_info': self.get_python_info(),
            'dependencies': self.check_dependencies(),
            'filesystem': self.check_filesystem(),
            'configuration': self.check_configuration()
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'architecture': platform.architecture()
        }
    
    def get_python_info(self) -> Dict[str, Any]:
        """Get Python environment info"""
        return {
            'version': sys.version,
            'executable': sys.executable,
            'path': sys.path[:3]  # First 3 paths
        }
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check installed dependencies"""
        dependencies = {}
        
        required = ['flask', 'nltk', 'beautifulsoup4', 'requests', 'psutil']
        
        for package in required:
            try:
                __import__(package)
                dependencies[package] = 'installed'
            except ImportError:
                dependencies[package] = 'missing'
        
        return dependencies
    
    def check_filesystem(self) -> Dict[str, Any]:
        """Check filesystem structure"""
        required_paths = [
            'config',
            'data',
            'data/logs',
            'data/storage',
            'kse',
            'gui'
        ]
        
        status = {}
        for path_str in required_paths:
            path = Path(path_str)
            status[path_str] = {
                'exists': path.exists(),
                'is_dir': path.is_dir() if path.exists() else False
            }
        
        return status
    
    def check_configuration(self) -> Dict[str, Any]:
        """Check configuration files"""
        config_files = [
            'config/kse_default_config.yaml',
            'config/swedish_domains.json',
            'config/swedish_stopwords.txt'
        ]
        
        status = {}
        for config_file in config_files:
            path = Path(config_file)
            status[config_file] = {
                'exists': path.exists(),
                'readable': path.is_file() if path.exists() else False
            }
        
        return status
