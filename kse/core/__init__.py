"""
KSE Core Module

Core functionality for Klar Swedish Engine.
"""

from kse.core.kse_exceptions import (
    KSEException,
    DatabaseException,
    CrawlerException,
    IndexingException,
    SearchException,
)
from kse.core.kse_constants import (
    DEFAULT_TIMEOUT,
    MAX_CONTENT_SIZE,
    MIN_DOMAIN_COUNT,
    TARGET_PAGE_COUNT,
    TARGET_INDEX_SIZE_GB,
)

__all__ = [
    "KSEException",
    "DatabaseException",
    "CrawlerException",
    "IndexingException",
    "SearchException",
    "DEFAULT_TIMEOUT",
    "MAX_CONTENT_SIZE",
    "MIN_DOMAIN_COUNT",
    "TARGET_PAGE_COUNT",
    "TARGET_INDEX_SIZE_GB",
]
