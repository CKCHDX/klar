"""
kse_config.py - Configuration Management for KSE

This module handles loading, validating, and providing access to configuration
values from YAML files, environment variables, and defaults.

Features:
- Load YAML configuration files
- Environment variable overrides
- Validation of config values
- Default values fallback
- Hierarchical config structure (section.key notation)
- Type-safe config access
- Hot-reload support (reload config without restart)

Usage:
    >>> from kse.core import ConfigManager
    >>> config = ConfigManager()
    >>> config.load('config/kse_default_config.yaml')
    >>> timeout = config.get('crawler.timeout', default=30)
    >>> config.set('crawler.timeout', 60)
    >>> config.save('config/custom_config.yaml')

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime

from .kse_constants import (
    DEFAULT_CONFIG_PATH,
    LOGS_DIR,
    CONFIG_DIR,
    APP_VERSION,
)
from .kse_exceptions import (
    KSEConfigException,
    KSEConfigNotFound,
    KSEConfigInvalid,
    KSEConfigValueError,
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Centralized configuration management system for KSE.
    
    Handles loading configuration from YAML files with support for:
    - Environment variable overrides
    - Default values
    - Validation
    - Hierarchical access using dot notation
    - Configuration hot-reload
    """
    
    def __init__(self):
        """Initialize configuration manager"""
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        self._loaded: bool = False
        self._last_loaded: Optional[datetime] = None
        logger.debug("ConfigManager initialized")
    
    def load(self, config_path: Union[str, Path]) -> None:
        """
        Load configuration from YAML file.
        
        Supports environment variable overrides using ${VAR_NAME} syntax.
        
        Args:
            config_path: Path to YAML configuration file
            
        Raises:
            KSEConfigNotFound: If config file doesn't exist
            KSEConfigInvalid: If YAML is malformed
            
        Example:
            >>> config.load('config/kse_default_config.yaml')
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            raise KSEConfigNotFound(str(config_path))
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace environment variables
            content = self._substitute_env_vars(content)
            
            # Parse YAML
            self._config = yaml.safe_load(content) or {}
            self._config_path = config_path
            self._loaded = True
            self._last_loaded = datetime.now()
            
            logger.info(
                f"Configuration loaded from {config_path} "
                f"({len(self._config)} sections)"
            )
            
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in config file: {e}")
            raise KSEConfigInvalid(
                str(config_path),
                f"YAML parsing error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise KSEConfigInvalid(str(config_path), str(e))
    
    def _substitute_env_vars(self, content: str) -> str:
        """
        Substitute environment variables in config content.
        
        Supports ${VAR_NAME} and ${VAR_NAME:default_value} syntax.
        
        Args:
            content: Config file content with potential env vars
            
        Returns:
            Content with environment variables substituted
        """
        import re
        
        def replace_env_var(match):
            var_expr = match.group(1)
            
            # Handle ${VAR:default} syntax
            if ':' in var_expr:
                var_name, default_val = var_expr.split(':', 1)
                return os.getenv(var_name.strip(), default_val.strip())
            
            # Handle ${VAR} syntax
            var_name = var_expr.strip()
            if var_name not in os.environ:
                logger.warning(f"Environment variable not found: {var_name}")
                return match.group(0)  # Keep original if not found
            
            return os.getenv(var_name)
        
        # Replace ${VAR_NAME} and ${VAR_NAME:default}
        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replace_env_var, content)
    
    def reload(self) -> None:
        """
        Reload configuration from the same file.
        
        Useful for hot-reloading config without restart.
        
        Raises:
            KSEConfigException: If no config was previously loaded
        """
        if not self._config_path:
            raise KSEConfigException(
                "Cannot reload: no configuration path set",
                error_code="CFG_NO_PATH"
            )
        
        logger.info(f"Reloading configuration from {self._config_path}")
        self.load(self._config_path)
    
    def get(
        self,
        key: str,
        default: Any = None,
        required: bool = False,
    ) -> Any:
        """
        Get configuration value using dot notation.
        
        Supports hierarchical access:
        - 'crawler.timeout' -> config['crawler']['timeout']
        - 'search.max_results' -> config['search']['max_results']
        
        Args:
            key: Configuration key in dot notation
            default: Default value if key not found
            required: If True, raise error if key not found
            
        Returns:
            Configuration value or default
            
        Raises:
            KSEConfigValueError: If required=True and key not found
            
        Example:
            >>> timeout = config.get('crawler.timeout', default=30)
            >>> max_results = config.get('search.max_results', required=True)
        """
        keys = key.split('.')
        value = self._config
        
        # Navigate through nested dict using dot notation
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    if required:
                        logger.error(f"Required config key not found: {key}")
                        raise KSEConfigValueError(
                            key,
                            None,
                            f"Required configuration key '{key}' not found"
                        )
                    logger.debug(f"Config key not found: {key}, using default")
                    return default
            else:
                if required:
                    logger.error(f"Cannot navigate config key: {key}")
                    raise KSEConfigValueError(
                        key,
                        value,
                        f"Cannot access '{k}' in non-dict value"
                    )
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Modifies in-memory config only (not persisted to file).
        
        Args:
            key: Configuration key in dot notation
            value: New value to set
            
        Example:
            >>> config.set('crawler.timeout', 60)
            >>> config.set('search.max_results', 100)
        """
        keys = key.split('.')
        target = self._config
        
        # Navigate/create nested structure
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            elif not isinstance(target[k], dict):
                logger.warning(
                    f"Overwriting non-dict value at '{k}' "
                    f"when setting '{key}'"
                )
                target[k] = {}
            
            target = target[k]
        
        # Set final value
        target[keys[-1]] = value
        logger.debug(f"Config value set: {key} = {value}")
    
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key: Configuration key in dot notation
            
        Returns:
            True if key exists and has non-None value
            
        Example:
            >>> if config.has('crawler.proxy'):
            ...     proxy = config.get('crawler.proxy')
        """
        value = self.get(key, default=object())  # Use sentinel value
        return value is not object()
    
    def save(self, output_path: Union[str, Path]) -> None:
        """
        Save current configuration to YAML file.
        
        Args:
            output_path: Path where config should be saved
            
        Raises:
            KSEConfigException: If save fails
            
        Example:
            >>> config.save('config/custom_config.yaml')
        """
        output_path = Path(output_path)
        
        try:
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write YAML
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self._config,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2,
                )
            
            logger.info(f"Configuration saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise KSEConfigException(
                f"Failed to save configuration: {str(e)}",
                error_code="CFG_SAVE_ERROR",
                details={"path": str(output_path)}
            )
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get entire configuration dictionary.
        
        Returns:
            Complete configuration as dict
            
        Example:
            >>> all_config = config.get_all()
        """
        return self._config.copy()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get all values in a configuration section.
        
        Args:
            section: Section name (e.g., 'crawler', 'search')
            
        Returns:
            Section dictionary or empty dict if not found
            
        Example:
            >>> crawler_config = config.get_section('crawler')
        """
        return self.get(section, default={})
    
    def validate(self) -> bool:
        """
        Validate configuration against requirements.
        
        Checks:
        - Required sections exist
        - Required keys exist
        - Values are in valid ranges
        
        Returns:
            True if configuration is valid
            
        Raises:
            KSEConfigValueError: If validation fails
        """
        required_sections = [
            'crawler',
            'nlp',
            'indexing',
            'ranking',
            'search',
            'server',
            'storage',
        ]
        
        for section in required_sections:
            if not self.has(section):
                logger.warning(f"Missing required config section: {section}")
                # Don't fail validation, just warn
        
        # Validate specific values
        timeout = self.get('crawler.timeout', default=30)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise KSEConfigValueError(
                'crawler.timeout',
                timeout,
                'Must be a positive number'
            )
        
        port = self.get('server.port', default=5000)
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise KSEConfigValueError(
                'server.port',
                port,
                'Must be between 1 and 65535'
            )
        
        logger.info("Configuration validation passed")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary (for API responses).
        
        Returns:
            Configuration as dictionary
        """
        return {
            "config": self._config,
            "loaded": self._loaded,
            "config_path": str(self._config_path) if self._config_path else None,
            "last_loaded": self._last_loaded.isoformat() if self._last_loaded else None,
        }
    
    @property
    def is_loaded(self) -> bool:
        """Check if configuration is loaded"""
        return self._loaded
    
    @property
    def config_path(self) -> Optional[Path]:
        """Get current config file path"""
        return self._config_path
    
    @property
    def last_loaded(self) -> Optional[datetime]:
        """Get timestamp when config was last loaded"""
        return self._last_loaded


# ============================================================================
# SINGLETON INSTANCE (Lazy-loaded)
# ============================================================================

_config_instance: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Get or create singleton ConfigManager instance.
    
    Returns:
        ConfigManager singleton
        
    Example:
        >>> config = get_config()
        >>> timeout = config.get('crawler.timeout')
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
        logger.debug("ConfigManager singleton created")
    return _config_instance


__all__ = [
    "ConfigManager",
    "get_config",
]
