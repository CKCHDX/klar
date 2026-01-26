"""
kse/core/__init__.py - KSE Core Package Initialization

This package contains the core foundation modules for the KSE search engine:

Modules:
- kse_constants: Global constants, enums, and configuration values
- kse_exceptions: Custom exception types with error codes
- kse_config: Configuration management (YAML, env vars)
- kse_logger: Enterprise logging system
- kse_singleton: Singleton pattern for shared resources
- kse_main: Main application class

Quick Start:
    >>> from kse.core import initialize_app, get_logger
    >>> app = initialize_app()
    >>> logger = get_logger('module')
    >>> config = app.config

Public API:
    # Application
    - KSEApplication: Main app class
    - get_app(): Get app singleton
    - initialize_app(): Initialize and return app
    
    # Configuration
    - ConfigManager: Config management
    - get_config(): Get config singleton
    
    # Logging
    - LoggerManager: Logging setup
    - get_logger(): Get logger instance
    
    # Exceptions
    - KSEException: Base exception
    - KSEConfigException, KSEStorageException, etc.
    
    # Singletons
    - Singleton: Base singleton class
    - SingletonMeta: Singleton metaclass
    
    # Constants
    - All constants from kse_constants module

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

# ============================================================================
# VERSION INFO
# ============================================================================

__version__ = "0.1.0"
__author__ = "CKCHDX / Oscyra Solutions"
__license__ = "MIT"

# ============================================================================
# IMPORTS - CONSTANTS (loaded first, no dependencies)
# ============================================================================

from .kse_constants import (
    # Metadata
    APP_NAME,
    APP_VERSION,
    APP_AUTHOR,
    APP_REPO,
    APP_WEBSITE,
    APP_LICENSE,
    APP_ENV,
    # Directories
    BASE_DIR,
    KSE_DIR,
    CONFIG_DIR,
    DATA_DIR,
    STORAGE_DIR,
    LOGS_DIR,
    # Crawler
    CRAWLER_USER_AGENT,
    CRAWLER_DEFAULT_TIMEOUT,
    CRAWLER_MAX_RETRIES,
    CRAWLER_MAX_DEPTH,
    CRAWLER_MAX_PAGES_PER_DOMAIN,
    # NLP
    NLP_LANGUAGE,
    NLP_MIN_TOKEN_LENGTH,
    # Indexing
    INDEX_MIN_WORD_LENGTH,
    INDEX_SKIP_STOPWORDS,
    # Ranking
    RANKING_WEIGHT_TFIDF,
    RANKING_WEIGHT_PAGERANK,
    PAGERANK_DAMPING_FACTOR,
    # Search
    SEARCH_MAX_RESULTS,
    SEARCH_DEFAULT_LIMIT,
    # Server
    SERVER_HOST,
    SERVER_PORT,
    # Status
    CrawlerStatus,
    IndexerStatus,
    ServerStatus,
    DomainCrawlStatus,
    PageStatus,
    HealthStatus,
    # Caching
    CACHE_ENABLED,
    CACHE_TTL_SEARCH,
    # Storage
    STORAGE_FORMAT,
    STORAGE_BACKUP_ENABLED,
)

# ============================================================================
# IMPORTS - EXCEPTIONS
# ============================================================================

from .kse_exceptions import (
    # Base
    KSEException,
    # Config
    KSEConfigException,
    KSEConfigNotFound,
    KSEConfigInvalid,
    KSEConfigValueError,
    # Storage
    KSEStorageException,
    KSEStorageIOError,
    KSEStorageNotFound,
    KSEStorageCorrupted,
    # Crawler
    KSECrawlerException,
    KSECrawlerNetworkError,
    KSECrawlerTimeoutError,
    KSECrawlerHTTPError,
    KSECrawlerRobotsBlocked,
    # Indexing
    KSEIndexException,
    KSEIndexBuildError,
    KSEIndexLoadError,
    KSEIndexSaveError,
    KSEIndexNotFound,
    # Search
    KSESearchException,
    KSESearchQueryError,
    KSESearchExecutionError,
    # NLP
    KSENLPException,
    KSENLPProcessingError,
    # Ranking
    KSERankingException,
    KSERankingCalculationError,
    # Server
    KSEServerException,
    KSEServerStartError,
    KSEServerPortInUse,
    # Validation
    KSEValidationException,
    KSEValidationError,
)

# ============================================================================
# IMPORTS - CONFIGURATION
# ============================================================================

from .kse_config import (
    ConfigManager,
    get_config,
)

# ============================================================================
# IMPORTS - LOGGING
# ============================================================================

from .kse_logger import (
    LoggerManager,
    ColoredFormatter,
    get_logger,
)

# ============================================================================
# IMPORTS - SINGLETON PATTERN
# ============================================================================

from .kse_singleton import (
    SingletonMeta,
    Singleton,
    GlobalSingletons,
    SingletonContext,
    get_logger as singleton_get_logger,
    get_config as singleton_get_config,
)

# ============================================================================
# IMPORTS - MAIN APPLICATION
# ============================================================================

from .kse_main import (
    KSEApplication,
    get_app,
    initialize_app,
)

# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    # Version
    "__version__",
    
    # Constants - Metadata
    "APP_NAME",
    "APP_VERSION",
    "APP_AUTHOR",
    "APP_ENV",
    
    # Constants - Directories
    "BASE_DIR",
    "CONFIG_DIR",
    "DATA_DIR",
    "LOGS_DIR",
    
    # Constants - Settings
    "CRAWLER_USER_AGENT",
    "CRAWLER_DEFAULT_TIMEOUT",
    "NLP_LANGUAGE",
    "SEARCH_DEFAULT_LIMIT",
    "SERVER_HOST",
    "SERVER_PORT",
    
    # Status Enums
    "CrawlerStatus",
    "IndexerStatus",
    "ServerStatus",
    
    # Exceptions
    "KSEException",
    "KSEConfigException",
    "KSEConfigNotFound",
    "KSEStorageException",
    "KSECrawlerException",
    "KSECrawlerNetworkError",
    "KSEIndexException",
    "KSESearchException",
    "KSEServerException",
    "KSEValidationException",
    
    # Configuration
    "ConfigManager",
    "get_config",
    
    # Logging
    "LoggerManager",
    "get_logger",
    
    # Singleton Pattern
    "Singleton",
    "SingletonMeta",
    "SingletonContext",
    
    # Main Application
    "KSEApplication",
    "get_app",
    "initialize_app",
]


# ============================================================================
# CONVENIENCE SETUP
# ============================================================================

def _setup_core():
    """
    Setup core modules on import.
    
    This runs once when the package is imported to ensure all
    core systems are properly initialized.
    """
    import logging as _logging
    
    # Ensure logging is setup at least to WARNING level
    if not _logging.getLogger().handlers:
        _logging.basicConfig(
            level=_logging.WARNING,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


_setup_core()


# ============================================================================
# DOCUMENTATION
# ============================================================================

"""
KSE Core Module Documentation

The kse.core package provides the foundation for the entire KSE search engine.

QUICK START:

    1. Initialize application:
        >>> from kse.core import initialize_app
        >>> app = initialize_app()
    
    2. Access configuration:
        >>> config = app.config
        >>> timeout = config.get('crawler.timeout', default=30)
    
    3. Get a logger:
        >>> logger = app.get_logger('my_module')
        >>> logger.info("Event logged")

COMPONENTS:

    kse_constants.py
        - Global constants and enums
        - Directory paths
        - Default configuration values
        - Status enums
        
    kse_exceptions.py
        - Custom exception types
        - Exception hierarchy
        - Error codes and messages
        
    kse_config.py
        - Configuration file loading (YAML)
        - Environment variable support
        - Config validation
        - Dot-notation access
        
    kse_logger.py
        - Centralized logging setup
        - Multiple log outputs
        - Colored console output
        - Log rotation
        
    kse_singleton.py
        - Singleton metaclass
        - Thread-safe singleton creation
        - Global singleton registry
        
    kse_main.py
        - Main application class
        - Lifecycle management
        - Component registration

ARCHITECTURE:

    KSEApplication (Singleton)
    ├── ConfigManager (manages configuration)
    ├── LoggerManager (sets up logging)
    └── Registered Components (lazy-loaded):
        ├── StorageManager
        ├── CrawlerEngine
        ├── IndexingEngine
        ├── SearchEngine
        └── APIServer

TYPICAL USAGE FLOW:

    1. Import and initialize:
        >>> from kse.core import initialize_app
        >>> app = initialize_app('config/kse_default_config.yaml')
    
    2. Register components:
        >>> from kse.storage import StorageManager
        >>> storage = StorageManager(app.config.get('storage.path'))
        >>> app.register_component('storage', storage)
    
    3. Use components:
        >>> storage = app.get_component('storage')
        >>> storage.save_data('key', data)
    
    4. Shutdown gracefully:
        >>> app.shutdown()

TESTING:

    Use SingletonContext for isolated tests:
        >>> from kse.core import SingletonContext, initialize_app
        >>> with SingletonContext():
        ...     app = initialize_app()
        ...     # Test with fresh app instance

ERROR HANDLING:

    All KSE exceptions inherit from KSEException:
        >>> from kse.core import KSEException
        >>> try:
        ...     app.config.load('missing_file.yaml')
        ... except KSEException as e:
        ...     print(f"Error: {e.error_code} - {e.message}")

CONFIGURATION:

    Configuration is loaded from YAML files with support for:
        - Hierarchical keys: config.get('section.subsection.key')
        - Environment variables: config.get('db.password', env_var='DB_PASS')
        - Default values: config.get('timeout', default=30)
        - Validation: config.validate()

LOGGING:

    Get loggers for different modules:
        >>> logger_crawler = get_logger('crawler')
        >>> logger_search = get_logger('search')
    
    Set log levels:
        >>> LoggerManager.set_level('DEBUG')  # All modules
        >>> LoggerManager.set_level('ERROR', 'crawler')  # Specific module
    
    Log audit events:
        >>> LoggerManager.log_audit(
        ...     action='rebuild_index',
        ...     user='admin',
        ...     status='success'
        ... )
"""
