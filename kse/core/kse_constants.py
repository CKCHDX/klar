"""
KSE Constants - Global constants and enums for Klar Search Engine
"""
from enum import Enum
from pathlib import Path


class CrawlStatus(Enum):
    """Status of a domain crawl"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class SearchMode(Enum):
    """Search execution modes"""
    STANDARD = "standard"
    ADVANCED = "advanced"
    AUTOCOMPLETE = "autocomplete"


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ComponentStatus(Enum):
    """Component health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# File paths
DEFAULT_BASE_DIR = Path.cwd()
DEFAULT_DATA_DIR = DEFAULT_BASE_DIR / "data"
DEFAULT_CONFIG_DIR = DEFAULT_BASE_DIR / "config"
DEFAULT_LOG_DIR = DEFAULT_DATA_DIR / "logs"
DEFAULT_STORAGE_DIR = DEFAULT_DATA_DIR / "storage"

# Storage paths
INDEX_DIR = DEFAULT_STORAGE_DIR / "index"
CACHE_DIR = DEFAULT_STORAGE_DIR / "cache"
CRAWL_STATE_DIR = DEFAULT_STORAGE_DIR / "crawl_state"
SNAPSHOTS_DIR = DEFAULT_STORAGE_DIR / "snapshots"

# Config files
DOMAINS_FILE = DEFAULT_CONFIG_DIR / "swedish_domains.json"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "kse_default_config.yaml"
STOPWORDS_FILE = DEFAULT_CONFIG_DIR / "swedish_stopwords.txt"

# Index files
INVERTED_INDEX_FILE = INDEX_DIR / "inverted_index.pkl"
METADATA_INDEX_FILE = INDEX_DIR / "metadata_index.pkl"
URL_INDEX_FILE = INDEX_DIR / "url_index.pkl"
TFIDF_CACHE_FILE = INDEX_DIR / "tfidf_cache.pkl"
PAGERANK_CACHE_FILE = INDEX_DIR / "pagerank_cache.pkl"

# Crawl state files
DOMAIN_STATUS_FILE = CRAWL_STATE_DIR / "domain_status.json"
URL_QUEUE_FILE = CRAWL_STATE_DIR / "url_queue.pkl"
VISITED_URLS_FILE = CRAWL_STATE_DIR / "visited_urls.pkl"

# Cache files
SEARCH_CACHE_FILE = CACHE_DIR / "search_cache.pkl"
QUERY_CACHE_FILE = CACHE_DIR / "query_cache.pkl"

# Crawler constants
DEFAULT_USER_AGENT = "KlarBot/3.0 (+https://oscyra.solutions/klar)"
DEFAULT_CRAWL_DELAY = 1.0  # seconds between requests
DEFAULT_TIMEOUT = 10  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_CRAWL_DEPTH = 50  # maximum links to follow per domain

# Search constants
DEFAULT_RESULTS_PER_PAGE = 10
MAX_RESULTS_PER_PAGE = 100
DEFAULT_SEARCH_TIMEOUT = 0.5  # 500ms target
CACHE_TTL = 3600  # 1 hour in seconds

# Ranking weights (must sum to 1.0)
RANKING_WEIGHTS = {
    "tf_idf": 0.25,
    "pagerank": 0.20,
    "domain_authority": 0.15,
    "recency": 0.15,
    "keyword_density": 0.10,
    "link_structure": 0.10,
    "regional_relevance": 0.05,
}

# Server constants
DEFAULT_SERVER_HOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 5000
DEFAULT_API_PREFIX = "/api"

# Monitoring constants
HEALTH_CHECK_INTERVAL = 60  # seconds
METRICS_COLLECTION_INTERVAL = 30  # seconds

# Swedish language constants
SWEDISH_STOPWORDS_COUNT = 133  # approximate
SWEDISH_COMPOUND_MIN_LENGTH = 8  # minimum length for compound word splitting

# Version
VERSION = "3.0.0"
