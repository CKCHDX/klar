"""
Control Center Configuration
Module definitions, settings, and API endpoints for KSE Control Center
"""

from typing import Dict, Any, List
from pathlib import Path
import json
import logging
from gui.kse_gui_config import GUIConfig

logger = logging.getLogger(__name__)


class ControlCenterConfig:
    """Control Center configuration and settings"""
    
    # Window settings
    WINDOW_TITLE = "KSE Control Center"
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    MIN_WIDTH = 1200
    MIN_HEIGHT = 700
    
    # API configuration
    # Note: Using HTTP for localhost development. For production/remote servers,
    # update to HTTPS to ensure encrypted communication.
    API_BASE_URL = "http://localhost:5000"
    API_TIMEOUT = 30  # seconds
    API_RETRY_COUNT = 3
    API_RETRY_DELAY = 1.0  # seconds (exponential backoff base)
    
    # Update intervals (milliseconds)
    UPDATE_INTERVALS = {
        'status_bar': 2000,      # 2 seconds
        'pcc': 5000,             # 5 seconds - Performance & Control
        'mcs': 5000,             # 5 seconds - Monitoring & Cache
        'scs': 10000,            # 10 seconds - Statistics & Charts
        'acc': 30000,            # 30 seconds - Analytics & Config
        'scc': 15000,            # 15 seconds - System & Crawler Control
    }
    
    # Module definitions
    MODULES = {
        'pcc': {
            'id': 'pcc',
            'name': 'Performance & Control',
            'title': 'Performance & Control Center',
            'icon': 'performance',
            'description': 'Real-time performance metrics and search testing',
            'tooltip': 'Monitor system performance and test search queries',
            'shortcut': 'Ctrl+1',
            'color': GUIConfig.COLORS['primary'],
        },
        'mcs': {
            'id': 'mcs',
            'name': 'Monitoring & Cache',
            'title': 'Monitoring & Cache Status',
            'icon': 'monitoring',
            'description': 'System monitoring and cache management',
            'tooltip': 'View system health and manage search cache',
            'shortcut': 'Ctrl+2',
            'color': GUIConfig.COLORS['success'],
        },
        'scs': {
            'id': 'scs',
            'name': 'Statistics & Charts',
            'title': 'Statistics & Charts Dashboard',
            'icon': 'statistics',
            'description': 'Comprehensive statistics and visualizations',
            'tooltip': 'View detailed statistics and performance charts',
            'shortcut': 'Ctrl+3',
            'color': GUIConfig.COLORS['info'],
        },
        'acc': {
            'id': 'acc',
            'name': 'Analytics & Config',
            'title': 'Analytics & Configuration',
            'icon': 'analytics',
            'description': 'Search analytics and system configuration',
            'tooltip': 'Analyze search patterns and configure system',
            'shortcut': 'Ctrl+4',
            'color': GUIConfig.COLORS['warning'],
        },
        'scc': {
            'id': 'scc',
            'name': 'System & Crawler',
            'title': 'System & Crawler Control',
            'icon': 'crawler',
            'description': 'System management and crawler operations',
            'tooltip': 'Manage system resources and control crawlers',
            'shortcut': 'Ctrl+5',
            'color': GUIConfig.COLORS['secondary'],
        },
    }
    
    # API endpoints
    API_ENDPOINTS = {
        'health': '/api/health',
        'stats': '/api/stats',
        'search': '/api/search',
        'history': '/api/history',
        'cache_stats': '/api/cache/stats',
        'cache_clear': '/api/cache/clear',
        'ranking_weights': '/api/ranking/weights',
        'monitoring_status': '/api/monitoring/status',
    }
    
    # Status states
    STATUS_STATES = {
        'connected': {
            'label': 'Connected',
            'color': GUIConfig.COLORS['success'],
            'icon': 'check',
        },
        'disconnected': {
            'label': 'Disconnected',
            'color': GUIConfig.COLORS['error'],
            'icon': 'error',
        },
        'connecting': {
            'label': 'Connecting...',
            'color': GUIConfig.COLORS['warning'],
            'icon': 'sync',
        },
        'error': {
            'label': 'Error',
            'color': GUIConfig.COLORS['error'],
            'icon': 'warning',
        },
    }
    
    # Health status colors
    HEALTH_COLORS = {
        'healthy': GUIConfig.COLORS['success'],
        'degraded': GUIConfig.COLORS['warning'],
        'unhealthy': GUIConfig.COLORS['error'],
        'unknown': GUIConfig.COLORS['text_secondary'],
    }
    
    # Configuration file path
    CONFIG_FILE = Path.home() / '.kse' / 'control_center_config.json'
    
    @classmethod
    def get_module_config(cls, module_id: str) -> Dict[str, Any]:
        """Get configuration for a specific module"""
        return cls.MODULES.get(module_id, {})
    
    @classmethod
    def get_module_list(cls) -> List[str]:
        """Get list of module IDs"""
        return list(cls.MODULES.keys())
    
    @classmethod
    def get_api_endpoint(cls, endpoint_name: str) -> str:
        """Get full API endpoint URL"""
        endpoint = cls.API_ENDPOINTS.get(endpoint_name, '')
        return f"{cls.API_BASE_URL}{endpoint}"
    
    @classmethod
    def get_update_interval(cls, module_id: str) -> int:
        """Get update interval for a module"""
        return cls.UPDATE_INTERVALS.get(module_id, 5000)
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load user configuration from file"""
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        return {}
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]):
        """Save user configuration to file"""
        try:
            cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    @classmethod
    def get_default_window_state(cls) -> Dict[str, Any]:
        """Get default window state"""
        return {
            'width': cls.WINDOW_WIDTH,
            'height': cls.WINDOW_HEIGHT,
            'maximized': False,
            'active_module': 'pcc',
        }
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """Get color for a status"""
        state = cls.STATUS_STATES.get(status.lower(), cls.STATUS_STATES['error'])
        return state['color']
    
    @classmethod
    def get_health_color(cls, health: str) -> str:
        """Get color for a health status"""
        return cls.HEALTH_COLORS.get(health.lower(), cls.HEALTH_COLORS['unknown'])
