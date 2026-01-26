"""
kse_constants.py - Global Constants & Configuration Values for KSE

This module defines all global constants, enums, and magic values used throughout
the KSE (Klar Search Engine) application. This is the foundation for all other
modules and should be imported first.

Constants are organized by category:
- Application Metadata
- Directory Paths
- Crawler Settings
- NLP Settings
- Indexing Settings
- Ranking Settings
- Search Settings
- Server Settings
- Status Enums
- Time Constants
- Error Messages

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from enum import Enum
from typing import Final
from pathlib import Path

# ============================================================================
# APPLICATION METADATA
# ============================================================================

APP_NAME: Final[str] = "Klar Search Engine"
APP_VERSION: Final[str] = "0.1.0"
APP_AUTHOR: Final[str] = "CKCHDX / Oscyra Solutions"
APP_REPO: Final[str] = "https://github.com/CKCHDX/klar"
APP_WEBSITE: Final[str] = "https://oscyra.solutions/klar"
APP_LICENSE: Final[str] = "MIT"
APP_ENV: Final[str] = "development"  # development, staging, production

# ============================================================================
# DIRECTORY PATHS
# ============================================================================

BASE_DIR: Final[Path] = Path(__file__).parent.parent.parent  # Root of project
KSE_DIR: Final[Path] = BASE_DIR / "kse"  # Main package directory
CONFIG_DIR: Final[Path] = BASE_DIR / "config"  # Config files
DATA_DIR: Final[Path] = BASE_DIR / "data"  # Runtime data storage
STORAGE_DIR: Final[Path] = DATA_DIR / "storage"  # File-based storage
INDEX_DIR: Final[Path] = STORAGE_DIR / "index"  # Index files
CACHE_DIR: Final[Path] = STORAGE_DIR / "cache"  # Cache files
CRAWL_STATE_DIR: Final[Path] = STORAGE_DIR / "crawl_state"  # Crawl state
SNAPSHOTS_DIR: Final[Path] = STORAGE_DIR / "snapshots"  # Index snapshots
LOGS_DIR: Final[Path] = DATA_DIR / "logs"  # Log files
EXPORTS_DIR: Final[Path] = DATA_DIR / "exports"  # User exports
ASSETS_DIR: Final[Path] = BASE_DIR / "assets"  # GUI assets
ICONS_DIR: Final[Path] = ASSETS_DIR / "icons"  # Icon files
THEMES_DIR: Final[Path] = ASSETS_DIR / "themes"  # Theme files
FONTS_DIR: Final[Path] = ASSETS_DIR / "fonts"  # Font files

# Default config file location
DEFAULT_CONFIG_PATH: Final[Path] = CONFIG_DIR / "kse_default_config.yaml"
DEFAULT_DOMAINS_PATH: Final[Path] = CONFIG_DIR / "swedish_domains.json"
DEFAULT_STOPWORDS_PATH: Final[Path] = CONFIG_DIR / "swedish_stopwords.txt"
DEFAULT_TRUST_SCORES_PATH: Final[Path] = CONFIG_DIR / "trust_scores.json"
DEFAULT_DOMAIN_CATEGORIES_PATH: Final[Path] = CONFIG_DIR / "domain_categories.json"

# ============================================================================
# CRAWLER SETTINGS
# ============================================================================

# HTTP Request
CRAWLER_USER_AGENT: Final[str] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 KlarSearchBot/0.1.0"
)
CRAWLER_DEFAULT_TIMEOUT: Final[int] = 30  # seconds
CRAWLER_MAX_RETRIES: Final[int] = 3
CRAWLER_RETRY_DELAY: Final[int] = 5  # seconds
CRAWLER_CONNECTION_TIMEOUT: Final[int] = 10  # seconds
CRAWLER_READ_TIMEOUT: Final[int] = 20  # seconds

# Crawling Behavior
CRAWLER_MAX_DEPTH: Final[int] = 5  # Max crawl depth per domain
CRAWLER_MAX_PAGES_PER_DOMAIN: Final[int] = 10000  # Max pages per domain
CRAWLER_DELAY_BETWEEN_REQUESTS: Final[float] = 1.0  # seconds (respect robots.txt)
CRAWLER_MAX_CONCURRENT_REQUESTS: Final[int] = 10
CRAWLER_FOLLOW_REDIRECTS: Final[bool] = True
CRAWLER_MAX_REDIRECTS: Final[int] = 5
CRAWLER_FOLLOW_ROBOTS_TXT: Final[bool] = True

# Content Limits
CRAWLER_MAX_PAGE_SIZE: Final[int] = 10 * 1024 * 1024  # 10 MB
CRAWLER_MIN_CONTENT_LENGTH: Final[int] = 100  # characters
CRAWLER_MAX_CONTENT_LENGTH: Final[int] = 5 * 1024 * 1024  # 5 MB

# HTML Parsing
CRAWLER_EXTRACT_LINKS: Final[bool] = True
CRAWLER_EXTRACT_METADATA: Final[bool] = True
CRAWLER_EXTRACT_HEADINGS: Final[bool] = True
CRAWLER_EXTRACT_IMAGES: Final[bool] = True
CRAWLER_IGNORE_URL_FRAGMENTS: Final[bool] = True

# Scheduling
CRAWLER_RECRAWL_INTERVAL: Final[int] = 7 * 24 * 3600  # 7 days in seconds
CRAWLER_FRESH_CONTENT_INTERVAL: Final[int] = 24 * 3600  # 24 hours in seconds
CRAWLER_STALE_CONTENT_INTERVAL: Final[int] = 30 * 24 * 3600  # 30 days in seconds

# ============================================================================
# NLP SETTINGS (Swedish Language Processing)
# ============================================================================

NLP_LANGUAGE: Final[str] = "sv"  # Swedish
NLP_MIN_TOKEN_LENGTH: Final[int] = 2
NLP_MAX_TOKEN_LENGTH: Final[int] = 50
NLP_NORMALIZE_CASE: Final[bool] = True
NLP_REMOVE_ACCENTS: Final[bool] = False  # Swedish has important accents (å, ä, ö)
NLP_REMOVE_PUNCTUATION: Final[bool] = True
NLP_REMOVE_STOPWORDS: Final[bool] = True
NLP_LEMMATIZE: Final[bool] = True
NLP_DETECT_COMPOUNDS: Final[bool] = True  # Important for Swedish

# Entity Recognition
NLP_ENABLE_NER: Final[bool] = True
NLP_NER_TYPES: Final[tuple] = ("PERSON", "ORG", "GPE", "DATE", "MONEY")

# Intent Detection
NLP_ENABLE_INTENT_DETECTION: Final[bool] = True
NLP_INTENT_TYPES: Final[tuple] = (
    "informational",
    "navigational",
    "transactional",
    "local",
)

# ============================================================================
# INDEXING SETTINGS
# ============================================================================

# Indexing Behavior
INDEX_ENABLE_INCREMENTAL: Final[bool] = True
INDEX_BATCH_SIZE: Final[int] = 1000  # Pages per batch
INDEX_OPTIMIZATION_ENABLED: Final[bool] = True

# Text Processing
INDEX_MIN_WORD_LENGTH: Final[int] = 2
INDEX_MAX_WORD_LENGTH: Final[int] = 50
INDEX_SKIP_STOPWORDS: Final[bool] = True

# Metadata
INDEX_EXTRACT_TITLE: Final[bool] = True
INDEX_EXTRACT_DESCRIPTION: Final[bool] = True
INDEX_EXTRACT_KEYWORDS: Final[bool] = True
INDEX_EXTRACT_HEADERS: Final[bool] = True
INDEX_EXTRACT_LINKS: Final[bool] = True
INDEX_EXTRACT_IMAGES: Final[bool] = True
INDEX_EXTRACT_PUBLISH_DATE: Final[bool] = True
INDEX_EXTRACT_AUTHOR: Final[bool] = True

# TF-IDF
TFIDF_ENABLE: Final[bool] = True
TFIDF_SUBLINEAR_TF: Final[bool] = True
TFIDF_USE_IDF: Final[bool] = True
TFIDF_SMOOTH_IDF: Final[bool] = True
TFIDF_MAX_DF: Final[float] = 0.95  # Ignore terms that appear in >95% of docs
TFIDF_MIN_DF: Final[int] = 1  # Ignore terms that appear in <1 doc

# ============================================================================
# RANKING SETTINGS
# ============================================================================

# Ranking Factors (weights sum should = 1.0)
RANKING_WEIGHT_TFIDF: Final[float] = 0.25  # TF-IDF relevance
RANKING_WEIGHT_PAGERANK: Final[float] = 0.20  # PageRank score
RANKING_WEIGHT_DOMAIN_AUTHORITY: Final[float] = 0.15  # Domain trust
RANKING_WEIGHT_RECENCY: Final[float] = 0.10  # Content freshness
RANKING_WEIGHT_KEYWORD_DENSITY: Final[float] = 0.10  # Keyword prominence
RANKING_WEIGHT_LINK_STRUCTURE: Final[float] = 0.10  # Link quality
RANKING_WEIGHT_REGIONAL_RELEVANCE: Final[float] = 0.10  # Regional match

# PageRank
PAGERANK_DAMPING_FACTOR: Final[float] = 0.85
PAGERANK_ITERATIONS: Final[int] = 20
PAGERANK_CONVERGENCE_THRESHOLD: Final[float] = 0.001

# Domain Authority
DOMAIN_AUTHORITY_MAX_SCORE: Final[float] = 100.0
DOMAIN_AUTHORITY_MIN_SCORE: Final[float] = 0.0
DOMAIN_AUTHORITY_DEFAULT_SCORE: Final[float] = 50.0

# Recency
RECENCY_BOOST_HOURS: Final[int] = 24  # Boost if updated within 24h
RECENCY_DECAY_DAYS: Final[int] = 90  # Heavily decay if >90 days old

# ============================================================================
# SEARCH SETTINGS
# ============================================================================

# Search Execution
SEARCH_MAX_RESULTS: Final[int] = 1000
SEARCH_DEFAULT_LIMIT: Final[int] = 10
SEARCH_MAX_LIMIT: Final[int] = 100
SEARCH_DEFAULT_OFFSET: Final[int] = 0
SEARCH_TIMEOUT: Final[int] = 5  # seconds

# Query Processing
SEARCH_MIN_QUERY_LENGTH: Final[int] = 1
SEARCH_MAX_QUERY_LENGTH: Final[int] = 1000
SEARCH_NORMALIZE_QUERY: Final[bool] = True
SEARCH_EXPAND_QUERY: Final[bool] = True
SEARCH_SPELL_CHECK: Final[bool] = True

# Spell Checking
SPELLCHECK_ENABLED: Final[bool] = True
SPELLCHECK_MAX_SUGGESTIONS: Final[int] = 5
SPELLCHECK_THRESHOLD: Final[float] = 0.8

# Autocomplete
AUTOCOMPLETE_ENABLED: Final[bool] = True
AUTOCOMPLETE_MIN_LENGTH: Final[int] = 2
AUTOCOMPLETE_MAX_SUGGESTIONS: Final[int] = 10
AUTOCOMPLETE_THRESHOLD: Final[float] = 0.7

# Result Diversity
DIVERSITY_ENABLED: Final[bool] = True
DIVERSITY_DOMAIN_LIMIT: Final[int] = 2  # Max 2 results per domain

# ============================================================================
# CACHING SETTINGS
# ============================================================================

# Cache Behavior
CACHE_ENABLED: Final[bool] = True
CACHE_MAX_SIZE: Final[int] = 10000  # Max entries
CACHE_TTL_SEARCH: Final[int] = 3600  # 1 hour
CACHE_TTL_QUERY: Final[int] = 1800  # 30 minutes
CACHE_TTL_INDEX: Final[int] = 86400  # 24 hours
CACHE_EVICTION_POLICY: Final[str] = "lru"  # lru, lfu, fifo

# ============================================================================
# SERVER SETTINGS (Flask API)
# ============================================================================

SERVER_HOST: Final[str] = "127.0.0.1"
SERVER_PORT: Final[int] = 5000
SERVER_DEBUG: Final[bool] = False
SERVER_THREADED: Final[bool] = True
SERVER_WORKERS: Final[int] = 4

# API Settings
API_VERSION: Final[str] = "v1"
API_PREFIX: Final[str] = f"/api/{API_VERSION}"
API_TIMEOUT: Final[int] = 30  # seconds
API_MAX_CONTENT_LENGTH: Final[int] = 16 * 1024 * 1024  # 16 MB

# Security
SECURITY_ENABLED: Final[bool] = True
SECURITY_CORS_ENABLED: Final[bool] = True
SECURITY_RATE_LIMIT_ENABLED: Final[bool] = True
SECURITY_RATE_LIMIT_REQUESTS: Final[int] = 100  # requests per window
SECURITY_RATE_LIMIT_WINDOW: Final[int] = 60  # seconds
SECURITY_API_KEY_REQUIRED: Final[bool] = False

# CORS
CORS_ORIGINS: Final[list] = ["*"]  # Allow all for local development
CORS_ALLOW_HEADERS: Final[list] = ["Content-Type", "Authorization"]
CORS_ALLOW_METHODS: Final[list] = ["GET", "POST", "OPTIONS"]

# ============================================================================
# STORAGE SETTINGS (Local File-Based)
# ============================================================================

STORAGE_FORMAT: Final[str] = "pickle"  # pickle or json
STORAGE_COMPRESSION: Final[bool] = False
STORAGE_BACKUP_ENABLED: Final[bool] = True
STORAGE_BACKUP_INTERVAL: Final[int] = 86400  # 24 hours in seconds
STORAGE_MAX_BACKUPS: Final[int] = 7  # Keep last 7 backups
STORAGE_CLEANUP_ENABLED: Final[bool] = True
STORAGE_CLEANUP_INTERVAL: Final[int] = 604800  # 7 days in seconds

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Log Levels
LOG_LEVEL_CONSOLE: Final[str] = "INFO"
LOG_LEVEL_FILE: Final[str] = "DEBUG"

# Log Format
LOG_FORMAT_CONSOLE: Final[str] = (
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOG_FORMAT_FILE: Final[str] = (
    "%(asctime)s - %(name)s - [%(filename)s:%(lineno)d] - "
    "%(levelname)s - %(message)s"
)

# Log Rotation
LOG_ROTATION_SIZE: Final[int] = 10 * 1024 * 1024  # 10 MB
LOG_RETENTION_DAYS: Final[int] = 30

# Log Files
LOG_FILE_MAIN: Final[str] = "kse.log"
LOG_FILE_CRAWLER: Final[str] = "crawler.log"
LOG_FILE_INDEXER: Final[str] = "indexer.log"
LOG_FILE_SEARCH: Final[str] = "search.log"
LOG_FILE_SERVER: Final[str] = "server.log"
LOG_FILE_ERRORS: Final[str] = "errors.log"
LOG_FILE_AUDIT: Final[str] = "audit.log"

# ============================================================================
# TIME CONSTANTS
# ============================================================================

SECOND: Final[int] = 1
MINUTE: Final[int] = 60
HOUR: Final[int] = 3600
DAY: Final[int] = 86400
WEEK: Final[int] = 604800
MONTH: Final[int] = 2592000  # 30 days
YEAR: Final[int] = 31536000  # 365 days

# ============================================================================
# STATUS ENUMS
# ============================================================================


class CrawlerStatus(Enum):
    """Crawler operational status"""
    IDLE = "idle"
    CRAWLING = "crawling"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class IndexerStatus(Enum):
    """Indexer operational status"""
    IDLE = "idle"
    INDEXING = "indexing"
    OPTIMIZING = "optimizing"
    SAVING = "saving"
    LOADING = "loading"
    ERROR = "error"


class ServerStatus(Enum):
    """Server operational status"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class DomainCrawlStatus(Enum):
    """Per-domain crawl status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class PageStatus(Enum):
    """Individual page status"""
    PENDING = "pending"
    CRAWLING = "crawling"
    INDEXED = "indexed"
    FAILED = "failed"
    DUPLICATE = "duplicate"
    BLOCKED = "blocked"


class HealthStatus(Enum):
    """System health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_CONFIG_NOT_FOUND: Final[str] = "Configuration file not found"
ERROR_CONFIG_INVALID: Final[str] = "Configuration file is invalid"
ERROR_STORAGE_ERROR: Final[str] = "Storage operation failed"
ERROR_CRAWLER_ERROR: Final[str] = "Crawler encountered an error"
ERROR_INDEXER_ERROR: Final[str] = "Indexer encountered an error"
ERROR_SEARCH_ERROR: Final[str] = "Search operation failed"
ERROR_SERVER_ERROR: Final[str] = "Server encountered an error"
ERROR_INVALID_REQUEST: Final[str] = "Invalid request"
ERROR_NOT_FOUND: Final[str] = "Resource not found"
ERROR_UNAUTHORIZED: Final[str] = "Unauthorized access"
ERROR_INTERNAL: Final[str] = "Internal server error"

# ============================================================================
# DEFAULT VALUES
# ============================================================================

DEFAULT_PAGE_SIZE: Final[int] = 10
DEFAULT_SORT_BY: Final[str] = "relevance"  # relevance, date, domain
DEFAULT_SORT_ORDER: Final[str] = "desc"  # asc, desc

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURE_SPELL_CHECK: Final[bool] = True
FEATURE_AUTOCOMPLETE: Final[bool] = True
FEATURE_QUERY_EXPANSION: Final[bool] = True
FEATURE_RESULT_DIVERSITY: Final[bool] = True
FEATURE_REGIONAL_RELEVANCE: Final[bool] = True
FEATURE_ANALYTICS: Final[bool] = True
FEATURE_SEARCH_HISTORY: Final[bool] = True

# ============================================================================
# SWEDISH-SPECIFIC SETTINGS
# ============================================================================

SWEDISH_COMPOUND_SEPARATOR: Final[str] = " "
SWEDISH_COMMON_PREFIXES: Final[list] = ["för-", "ut-", "in-", "på-", "av-"]
SWEDISH_COMMON_SUFFIXES: Final[list] = ["-ing", "-tion", "-itet", "-lig"]

# Swedish domain TLD
SWEDISH_TLD: Final[str] = ".se"
SWEDISH_LANGUAGE_CODE: Final[str] = "sv-SE"

# ============================================================================
# VERSION INFO
# ============================================================================

VERSION_MAJOR: Final[int] = 0
VERSION_MINOR: Final[int] = 1
VERSION_PATCH: Final[int] = 0
VERSION_BUILD: Final[str] = "20260126"

__all__ = [
    # Metadata
    "APP_NAME",
    "APP_VERSION",
    "APP_AUTHOR",
    # Directory Paths
    "BASE_DIR",
    "KSE_DIR",
    "CONFIG_DIR",
    "DATA_DIR",
    "LOGS_DIR",
    # Crawler
    "CRAWLER_USER_AGENT",
    "CRAWLER_DEFAULT_TIMEOUT",
    "CRAWLER_MAX_RETRIES",
    # NLP
    "NLP_LANGUAGE",
    "NLP_MIN_TOKEN_LENGTH",
    # Indexing
    "INDEX_MIN_WORD_LENGTH",
    "INDEX_SKIP_STOPWORDS",
    # Ranking
    "RANKING_WEIGHT_TFIDF",
    "PAGERANK_DAMPING_FACTOR",
    # Search
    "SEARCH_MAX_RESULTS",
    "SEARCH_DEFAULT_LIMIT",
    # Caching
    "CACHE_ENABLED",
    "CACHE_TTL_SEARCH",
    # Server
    "SERVER_HOST",
    "SERVER_PORT",
    # Status Enums
    "CrawlerStatus",
    "IndexerStatus",
    "ServerStatus",
    "DomainCrawlStatus",
    "PageStatus",
    "HealthStatus",
    # Feature Flags
    "FEATURE_SPELL_CHECK",
    "FEATURE_AUTOCOMPLETE",
]
