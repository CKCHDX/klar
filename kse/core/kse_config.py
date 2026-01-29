"""
Configuration Manager for Klar Search Engine
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages configuration for Klar Search Engine
    
    Handles loading, saving, and accessing configuration settings
    for the KSE application.
    """
    
    DEFAULT_CONFIG = {
        'app_name': 'Klar Search Engine',
        'version': '4.0',
        'data_path': 'data',
        'max_workers': 2,
        'base_delay': 1.0,
        'domains_file': 'domains.json',
        'keywords_file': 'keywords_db_hierarchical.json',
        'gui': {
            'width': 1200,
            'height': 700,
            'theme': 'default'
        },
        'search': {
            'max_results': 100,
            'enable_metadata': True,
            'enable_hierarchical': True
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the ConfigManager
        
        Args:
            config_path: Path to the configuration file. If None, uses default location.
        """
        if config_path is None:
            # Use default config path in the application directory
            app_dir = Path(__file__).parent.parent.parent
            config_path = app_dir / 'config' / 'kse_config.json'
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file or create default"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.info("No configuration file found, using defaults")
                self.config = self.DEFAULT_CONFIG.copy()
                self.save_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
            self.config = self.DEFAULT_CONFIG.copy()
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            # Ensure parent directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'gui.width')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'gui.width')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        logger.debug(f"Configuration updated: {key} = {value}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary"""
        return self.config.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        logger.info("Configuration reset to defaults")
