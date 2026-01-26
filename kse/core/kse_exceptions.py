"""
kse_exceptions.py - Custom Exception Types for KSE

This module defines all custom exception types used throughout the KSE application.
These exceptions provide fine-grained error handling and meaningful error messages.

Exception Hierarchy:
- KSEException (base)
  ├── KSEConfigException
  ├── KSEStorageException
  ├── KSECrawlerException
  ├── KSEIndexException
  ├── KSESearchException
  ├── KSEServerException
  ├── KSENLPException
  ├── KSERankingException
  ├── KSECacheException
  └── KSEValidationException

Usage:
    try:
        config_manager.load('config.yaml')
    except KSEConfigException as e:
        logger.error(f"Configuration error: {e}")

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from typing import Optional, Any, Dict


# ============================================================================
# BASE EXCEPTION
# ============================================================================


class KSEException(Exception):
    """
    Base exception class for all KSE-specific exceptions.
    
    All custom exceptions in the KSE system inherit from this class,
    allowing for broad exception catching while still being specific
    about KSE errors vs other errors.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """
        Initialize KSE exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (e.g., "CFG_MISSING")
            details: Additional context information
            cause: Original exception that caused this (for chaining)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN"
        self.details = details or {}
        self.cause = cause
    
    def __str__(self) -> str:
        """Return formatted exception string"""
        if self.error_code and self.error_code != "UNKNOWN":
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# ============================================================================
# CONFIGURATION EXCEPTIONS
# ============================================================================


class KSEConfigException(KSEException):
    """Raised when configuration loading or validation fails"""
    pass


class KSEConfigNotFound(KSEConfigException):
    """Raised when configuration file cannot be found"""
    
    def __init__(self, config_path: str, **kwargs):
        super().__init__(
            f"Configuration file not found: {config_path}",
            error_code="CFG_NOT_FOUND",
            details={"config_path": config_path},
            **kwargs
        )


class KSEConfigInvalid(KSEConfigException):
    """Raised when configuration file is invalid (malformed YAML, etc)"""
    
    def __init__(self, config_path: str, reason: str, **kwargs):
        super().__init__(
            f"Configuration file is invalid: {reason}",
            error_code="CFG_INVALID",
            details={"config_path": config_path, "reason": reason},
            **kwargs
        )


class KSEConfigValueError(KSEConfigException):
    """Raised when a configuration value is invalid"""
    
    def __init__(self, key: str, value: Any, reason: str, **kwargs):
        super().__init__(
            f"Invalid configuration value for '{key}': {reason}",
            error_code="CFG_VALUE_ERROR",
            details={"key": key, "value": value, "reason": reason},
            **kwargs
        )


# ============================================================================
# STORAGE EXCEPTIONS
# ============================================================================


class KSEStorageException(KSEException):
    """Base exception for storage-related errors"""
    pass


class KSEStorageIOError(KSEStorageException):
    """Raised when file I/O operation fails"""
    
    def __init__(self, operation: str, path: str, reason: str, **kwargs):
        super().__init__(
            f"Storage I/O error during {operation} on {path}: {reason}",
            error_code="STORAGE_IO_ERROR",
            details={"operation": operation, "path": path, "reason": reason},
            **kwargs
        )


class KSEStorageNotFound(KSEStorageException):
    """Raised when requested storage file/directory not found"""
    
    def __init__(self, path: str, **kwargs):
        super().__init__(
            f"Storage resource not found: {path}",
            error_code="STORAGE_NOT_FOUND",
            details={"path": path},
            **kwargs
        )


class KSEStorageCorrupted(KSEStorageException):
    """Raised when storage file is corrupted"""
    
    def __init__(self, path: str, reason: str, **kwargs):
        super().__init__(
            f"Storage file corrupted: {path} - {reason}",
            error_code="STORAGE_CORRUPTED",
            details={"path": path, "reason": reason},
            **kwargs
        )


class KSEStorageQuotaExceeded(KSEStorageException):
    """Raised when storage quota exceeded"""
    
    def __init__(self, quota: int, used: int, **kwargs):
        super().__init__(
            f"Storage quota exceeded: {used} bytes used of {quota} bytes available",
            error_code="STORAGE_QUOTA_EXCEEDED",
            details={"quota": quota, "used": used},
            **kwargs
        )


# ============================================================================
# CRAWLER EXCEPTIONS
# ============================================================================


class KSECrawlerException(KSEException):
    """Base exception for crawler errors"""
    pass


class KSECrawlerNetworkError(KSECrawlerException):
    """Raised when network error occurs during crawling"""
    
    def __init__(self, url: str, reason: str, **kwargs):
        super().__init__(
            f"Network error crawling {url}: {reason}",
            error_code="CRAWLER_NETWORK_ERROR",
            details={"url": url, "reason": reason},
            **kwargs
        )


class KSECrawlerTimeoutError(KSECrawlerException):
    """Raised when crawl request times out"""
    
    def __init__(self, url: str, timeout: int, **kwargs):
        super().__init__(
            f"Crawl timeout for {url} after {timeout}s",
            error_code="CRAWLER_TIMEOUT",
            details={"url": url, "timeout": timeout},
            **kwargs
        )


class KSECrawlerHTTPError(KSECrawlerException):
    """Raised when HTTP error response received"""
    
    def __init__(self, url: str, status_code: int, **kwargs):
        super().__init__(
            f"HTTP {status_code} error crawling {url}",
            error_code="CRAWLER_HTTP_ERROR",
            details={"url": url, "status_code": status_code},
            **kwargs
        )


class KSECrawlerRobotsBlocked(KSECrawlerException):
    """Raised when URL blocked by robots.txt"""
    
    def __init__(self, url: str, **kwargs):
        super().__init__(
            f"URL blocked by robots.txt: {url}",
            error_code="CRAWLER_ROBOTS_BLOCKED",
            details={"url": url},
            **kwargs
        )


class KSECrawlerInvalidURL(KSECrawlerException):
    """Raised when URL is invalid"""
    
    def __init__(self, url: str, reason: str, **kwargs):
        super().__init__(
            f"Invalid URL: {url} - {reason}",
            error_code="CRAWLER_INVALID_URL",
            details={"url": url, "reason": reason},
            **kwargs
        )


# ============================================================================
# INDEXING EXCEPTIONS
# ============================================================================


class KSEIndexException(KSEException):
    """Base exception for indexing errors"""
    pass


class KSEIndexBuildError(KSEIndexException):
    """Raised when index building fails"""
    
    def __init__(self, reason: str, **kwargs):
        super().__init__(
            f"Index build failed: {reason}",
            error_code="INDEX_BUILD_ERROR",
            details={"reason": reason},
            **kwargs
        )


class KSEIndexLoadError(KSEIndexException):
    """Raised when index loading fails"""
    
    def __init__(self, path: str, reason: str, **kwargs):
        super().__init__(
            f"Failed to load index from {path}: {reason}",
            error_code="INDEX_LOAD_ERROR",
            details={"path": path, "reason": reason},
            **kwargs
        )


class KSEIndexSaveError(KSEIndexException):
    """Raised when index saving fails"""
    
    def __init__(self, path: str, reason: str, **kwargs):
        super().__init__(
            f"Failed to save index to {path}: {reason}",
            error_code="INDEX_SAVE_ERROR",
            details={"path": path, "reason": reason},
            **kwargs
        )


class KSEIndexNotFound(KSEIndexException):
    """Raised when index not found"""
    
    def __init__(self, **kwargs):
        super().__init__(
            "Search index not found. Please run crawler first.",
            error_code="INDEX_NOT_FOUND",
            **kwargs
        )


# ============================================================================
# SEARCH EXCEPTIONS
# ============================================================================


class KSESearchException(KSEException):
    """Base exception for search errors"""
    pass


class KSESearchQueryError(KSESearchException):
    """Raised when search query is invalid"""
    
    def __init__(self, query: str, reason: str, **kwargs):
        super().__init__(
            f"Invalid search query: {reason}",
            error_code="SEARCH_QUERY_ERROR",
            details={"query": query, "reason": reason},
            **kwargs
        )


class KSESearchExecutionError(KSESearchException):
    """Raised when search execution fails"""
    
    def __init__(self, reason: str, **kwargs):
        super().__init__(
            f"Search execution failed: {reason}",
            error_code="SEARCH_EXECUTION_ERROR",
            details={"reason": reason},
            **kwargs
        )


class KSESearchTimeoutError(KSESearchException):
    """Raised when search times out"""
    
    def __init__(self, query: str, timeout: int, **kwargs):
        super().__init__(
            f"Search timeout for '{query}' after {timeout}s",
            error_code="SEARCH_TIMEOUT",
            details={"query": query, "timeout": timeout},
            **kwargs
        )


# ============================================================================
# NLP EXCEPTIONS
# ============================================================================


class KSENLPException(KSEException):
    """Base exception for NLP errors"""
    pass


class KSENLPProcessingError(KSENLPException):
    """Raised when NLP processing fails"""
    
    def __init__(self, operation: str, text: str, reason: str, **kwargs):
        super().__init__(
            f"NLP {operation} failed: {reason}",
            error_code="NLP_PROCESSING_ERROR",
            details={"operation": operation, "reason": reason},
            **kwargs
        )


class KSENLPModelNotFound(KSENLPException):
    """Raised when NLP model not found"""
    
    def __init__(self, model_name: str, **kwargs):
        super().__init__(
            f"NLP model not found: {model_name}",
            error_code="NLP_MODEL_NOT_FOUND",
            details={"model_name": model_name},
            **kwargs
        )


# ============================================================================
# RANKING EXCEPTIONS
# ============================================================================


class KSERankingException(KSEException):
    """Base exception for ranking errors"""
    pass


class KSERankingCalculationError(KSERankingException):
    """Raised when ranking calculation fails"""
    
    def __init__(self, factor: str, reason: str, **kwargs):
        super().__init__(
            f"Ranking calculation failed for factor '{factor}': {reason}",
            error_code="RANKING_CALC_ERROR",
            details={"factor": factor, "reason": reason},
            **kwargs
        )


# ============================================================================
# SERVER EXCEPTIONS
# ============================================================================


class KSEServerException(KSEException):
    """Base exception for server errors"""
    pass


class KSEServerStartError(KSEServerException):
    """Raised when server startup fails"""
    
    def __init__(self, reason: str, **kwargs):
        super().__init__(
            f"Server startup failed: {reason}",
            error_code="SERVER_START_ERROR",
            details={"reason": reason},
            **kwargs
        )


class KSEServerPortInUse(KSEServerException):
    """Raised when server port is already in use"""
    
    def __init__(self, port: int, **kwargs):
        super().__init__(
            f"Server port {port} is already in use",
            error_code="SERVER_PORT_IN_USE",
            details={"port": port},
            **kwargs
        )


class KSEServerNotRunning(KSEServerException):
    """Raised when operation requires running server but it's not"""
    
    def __init__(self, **kwargs):
        super().__init__(
            "Server is not running",
            error_code="SERVER_NOT_RUNNING",
            **kwargs
        )


# ============================================================================
# CACHE EXCEPTIONS
# ============================================================================


class KSECacheException(KSEException):
    """Base exception for cache errors"""
    pass


class KSECacheKeyError(KSECacheException):
    """Raised when cache key not found"""
    
    def __init__(self, key: str, **kwargs):
        super().__init__(
            f"Cache key not found: {key}",
            error_code="CACHE_KEY_NOT_FOUND",
            details={"key": key},
            **kwargs
        )


class KSECacheEvictionError(KSECacheException):
    """Raised when cache eviction fails"""
    
    def __init__(self, reason: str, **kwargs):
        super().__init__(
            f"Cache eviction failed: {reason}",
            error_code="CACHE_EVICTION_ERROR",
            details={"reason": reason},
            **kwargs
        )


# ============================================================================
# VALIDATION EXCEPTIONS
# ============================================================================


class KSEValidationException(KSEException):
    """Base exception for validation errors"""
    pass


class KSEValidationError(KSEValidationException):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, reason: str, **kwargs):
        super().__init__(
            f"Validation failed for field '{field}': {reason}",
            error_code="VALIDATION_ERROR",
            details={"field": field, "reason": reason},
            **kwargs
        )


class KSEDomainError(KSEValidationException):
    """Raised when domain validation fails"""
    
    def __init__(self, domain: str, reason: str, **kwargs):
        super().__init__(
            f"Invalid domain '{domain}': {reason}",
            error_code="DOMAIN_ERROR",
            details={"domain": domain, "reason": reason},
            **kwargs
        )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Base
    "KSEException",
    # Config
    "KSEConfigException",
    "KSEConfigNotFound",
    "KSEConfigInvalid",
    "KSEConfigValueError",
    # Storage
    "KSEStorageException",
    "KSEStorageIOError",
    "KSEStorageNotFound",
    "KSEStorageCorrupted",
    "KSEStorageQuotaExceeded",
    # Crawler
    "KSECrawlerException",
    "KSECrawlerNetworkError",
    "KSECrawlerTimeoutError",
    "KSECrawlerHTTPError",
    "KSECrawlerRobotsBlocked",
    "KSECrawlerInvalidURL",
    # Indexing
    "KSEIndexException",
    "KSEIndexBuildError",
    "KSEIndexLoadError",
    "KSEIndexSaveError",
    "KSEIndexNotFound",
    # Search
    "KSESearchException",
    "KSESearchQueryError",
    "KSESearchExecutionError",
    "KSESearchTimeoutError",
    # NLP
    "KSENLPException",
    "KSENLPProcessingError",
    "KSENLPModelNotFound",
    # Ranking
    "KSERankingException",
    "KSERankingCalculationError",
    # Server
    "KSEServerException",
    "KSEServerStartError",
    "KSEServerPortInUse",
    "KSEServerNotRunning",
    # Cache
    "KSECacheException",
    "KSECacheKeyError",
    "KSECacheEvictionError",
    # Validation
    "KSEValidationException",
    "KSEValidationError",
    "KSEDomainError",
]
