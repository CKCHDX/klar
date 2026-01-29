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


# Alias for backward compatibility with GUI code
ConfigManager = KSEConfig
