"""
KSE Core Module

Core functionality for Klar Swedish Engine.
Includes exceptions, constants, configuration, and logging.
"""

from kse.core.kse_exceptions import (
    KSEException,
    DatabaseException,
    ConnectionException,
    SchemaException,
    CrawlerException,
    URLException,
    HTTPException,
    ParsingException,
    IndexingException,
    TokenizationException,
    SearchException,
    QueryException,
    RankingException,
    ConfigException,
)
from kse.core.kse_constants import (
    DEFAULT_TIMEOUT,
    MAX_CONTENT_SIZE,
    MIN_DOMAIN_COUNT,
    TARGET_PAGE_COUNT,
    TARGET_INDEX_SIZE_GB,
    SEARCH_LATENCY_TARGET_MS,
    UPTIME_TARGET_PERCENT,
    DEFAULT_USER_AGENT,
    SWEDISH_LANGUAGE_CODE,
)
from kse.core.kse_logger import KSELogger

__all__ = [
    # Exceptions
    "KSEException",
    "DatabaseException",
    "ConnectionException",
    "SchemaException",
    "CrawlerException",
    "URLException",
    "HTTPException",
    "ParsingException",
    "IndexingException",
    "TokenizationException",
    "SearchException",
    "QueryException",
    "RankingException",
    "ConfigException",
    # Constants
    "DEFAULT_TIMEOUT",
    "MAX_CONTENT_SIZE",
    "MIN_DOMAIN_COUNT",
    "TARGET_PAGE_COUNT",
    "TARGET_INDEX_SIZE_GB",
    "SEARCH_LATENCY_TARGET_MS",
    "UPTIME_TARGET_PERCENT",
    "DEFAULT_USER_AGENT",
    "SWEDISH_LANGUAGE_CODE",
    # Logging
    "KSELogger",
]
