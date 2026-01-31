"""
KSE Configuration - Global configuration management for Klar Search Engine
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from kse.core.kse_singleton import Singleton
from kse.core.kse_exceptions import ConfigurationError
from kse.core.kse_logger import get_logger

logger = get_logger(__name__)


class KSEConfig(metaclass=Singleton):
    """Global configuration manager for KSE"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration
        
        Args:
            config_file: Path to YAML configuration file
        """
        self._config: Dict[str, Any] = {}
        
        # Auto-discover config file if not specified
        if config_file is None:
            from kse.core.kse_constants import DEFAULT_CONFIG_DIR
            potential_config = DEFAULT_CONFIG_DIR / "kse_config.yaml"
            if potential_config.exists():
                config_file = potential_config
                logger.info(f"Auto-discovered config file: {config_file}")
        
        self._config_file = config_file
        self._load_defaults()
        
        if config_file and config_file.exists():
            self._load_config_file(config_file)
        
        logger.info("Configuration loaded successfully")
    
    def _load_defaults(self) -> None:
        """Load default configuration values"""
        from kse.core.kse_constants import (
            DEFAULT_BASE_DIR, DEFAULT_DATA_DIR, DEFAULT_CONFIG_DIR,
            DEFAULT_LOG_DIR, DEFAULT_STORAGE_DIR,
            DEFAULT_USER_AGENT, DEFAULT_CRAWL_DELAY, DEFAULT_TIMEOUT,
            DEFAULT_MAX_RETRIES, DEFAULT_CRAWL_DEPTH,
            DEFAULT_RESULTS_PER_PAGE, DEFAULT_SEARCH_TIMEOUT,
            DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT, DEFAULT_API_PREFIX,
            RANKING_WEIGHTS
        )
        
        self._config = {
            # Paths
            "base_dir": str(DEFAULT_BASE_DIR),
            "data_dir": str(DEFAULT_DATA_DIR),
            "config_dir": str(DEFAULT_CONFIG_DIR),
            "log_dir": str(DEFAULT_LOG_DIR),
            "storage_dir": str(DEFAULT_STORAGE_DIR),
            
            # Logging
            "log_level": "INFO",
            "enable_console_logging": True,
            
            # Crawler settings
            "crawler": {
                "user_agent": DEFAULT_USER_AGENT,
                "crawl_delay": DEFAULT_CRAWL_DELAY,
                "timeout": DEFAULT_TIMEOUT,
                "max_retries": DEFAULT_MAX_RETRIES,
                "crawl_depth": DEFAULT_CRAWL_DEPTH,
                "respect_robots_txt": True,
                "max_concurrent_requests": 10,
            },
            
            # Search settings
            "search": {
                "results_per_page": DEFAULT_RESULTS_PER_PAGE,
                "search_timeout": DEFAULT_SEARCH_TIMEOUT,
                "enable_cache": True,
                "cache_ttl": 3600,
            },
            
            # Ranking settings
            "ranking": {
                "weights": RANKING_WEIGHTS,
            },
            
            # Server settings
            "server": {
                "host": DEFAULT_SERVER_HOST,
                "port": DEFAULT_SERVER_PORT,
                "api_prefix": DEFAULT_API_PREFIX,
                "debug": False,
                "enable_cors": True,
                "public_url": None,
            },
            
            # NLP settings
            "nlp": {
                "language": "swedish",
                "enable_lemmatization": True,
                "enable_compound_splitting": True,
                "min_compound_length": 8,
            },
            
            # Storage settings
            "storage": {
                "compression_enabled": True,
                "backup_enabled": True,
                "max_backups": 5,
            },
        }
    
    def _load_config_file(self, config_file: Path) -> None:
        """
        Load configuration from YAML file
        
        Args:
            config_file: Path to YAML configuration file
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
            
            if user_config:
                self._merge_config(self._config, user_config)
            
            logger.info(f"Configuration loaded from {config_file}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file: {e}")
    
    def _merge_config(self, base: Dict, update: Dict) -> None:
        """
        Recursively merge configuration dictionaries
        
        Args:
            base: Base configuration
            update: Configuration updates
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'crawler.timeout')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        # Extract underlying dict from DictToObject if needed
        if hasattr(value, '_data') and hasattr(value, '__class__') and value.__class__.__name__ == 'DictToObject':
            value = value._data
        
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"Configuration updated: {key} = {value}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration
        
        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()
    
    def save(self, config_file: Optional[Path] = None) -> None:
        """
        Save configuration to file
        
        Args:
            config_file: Path to save configuration (defaults to loaded file)
        """
        save_path = config_file or self._config_file
        
        if not save_path:
            raise ConfigurationError("No config file specified for saving")
        
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            raise ConfigurationError(f"Failed to save config file: {e}")


def get_config() -> KSEConfig:
    """
    Get the global configuration instance
    
    Returns:
        KSEConfig instance
    """
    return KSEConfig()


class DictToObject:
    """Helper class to convert dict to object with attribute access"""
    
    def __init__(self, data: Dict[str, Any], parent_manager=None, key_path: str = ""):
        """
        Initialize with dictionary data
        
        Args:
            data: Dictionary to convert to object
            parent_manager: Reference to parent ConfigManager for updates
            key_path: Dot-separated path to this object in the config
        """
        # Set internal attributes first using super().__setattr__ to avoid triggering our custom __setattr__
        super().__setattr__('_data', data)
        super().__setattr__('_parent_manager', parent_manager)
        super().__setattr__('_key_path', key_path)
        
        # Now set regular attributes
        for key, value in data.items():
            if isinstance(value, dict):
                child_path = f"{key_path}.{key}" if key_path else key
                # Use super().__setattr__ to avoid triggering parent_manager.set during initialization
                super().__setattr__(key, DictToObject(value, parent_manager, child_path))
            else:
                # Use super().__setattr__ to avoid triggering parent_manager.set during initialization
                super().__setattr__(key, value)
    
    def __setattr__(self, name: str, value: Any):
        # Handle internal attributes
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        
        # Convert SimpleNamespace to dict for YAML serialization
        from types import SimpleNamespace
        if isinstance(value, SimpleNamespace):
            value = vars(value)
        
        # Update the internal data dict
        if hasattr(self, '_data'):
            self._data[name] = value
        
        # Update the parent manager if available
        if hasattr(self, '_parent_manager') and self._parent_manager and hasattr(self, '_key_path'):
            full_key = f"{self._key_path}.{name}" if self._key_path else name
            self._parent_manager.set(full_key, value)
        
        # Wrap dicts in DictToObject for consistent nested access
        if isinstance(value, dict) and hasattr(self, '_parent_manager') and hasattr(self, '_key_path'):
            child_path = f"{self._key_path}.{name}" if self._key_path else name
            value = DictToObject(value, self._parent_manager if hasattr(self, '_parent_manager') else None, child_path)
        
        # Set the attribute
        super().__setattr__(name, value)
    
    def __repr__(self):
        return f"<DictToObject {self._data}>"


class ConfigManager:
    """
    Configuration manager with attribute-style access
    Provides backward compatibility with GUI code
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to YAML configuration file
        """
        self._kse_config = KSEConfig(config_file)
        self._config_obj = None
    
    @property
    def config(self) -> DictToObject:
        """
        Get configuration as object with attribute access
        
        Returns:
            Configuration object
        """
        # Create config object with reference to this manager for updates
        self._config_obj = DictToObject(self._kse_config.get_all(), parent_manager=self)
        return self._config_obj
    
    def save_config(self, config_file: Optional[Path] = None) -> None:
        """
        Save configuration to file
        
        Args:
            config_file: Path to save configuration (defaults to loaded file)
        """
        self._kse_config.save(config_file)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        return self._kse_config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        self._kse_config.set(key, value)
    
    def set_config_file_path(self, config_file: Path) -> None:
        """
        Set the configuration file path
        
        Args:
            config_file: Path to configuration file
        """
        self._kse_config._config_file = config_file
