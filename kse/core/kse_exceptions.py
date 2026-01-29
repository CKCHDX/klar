"""
KSE Exceptions - Custom exception types for Klar Search Engine
"""


class KSEException(Exception):
    """Base exception for all KSE errors"""
    pass


class ConfigurationError(KSEException):
    """Raised when configuration is invalid or missing"""
    pass


class StorageError(KSEException):
    """Raised when storage operations fail"""
    pass


class CrawlerError(KSEException):
    """Raised when crawler encounters errors"""
    pass


class IndexingError(KSEException):
    """Raised when indexing operations fail"""
    pass


class SearchError(KSEException):
    """Raised when search operations fail"""
    pass


class RankingError(KSEException):
    """Raised when ranking operations fail"""
    pass


class NLPError(KSEException):
    """Raised when NLP processing fails"""
    pass


class ServerError(KSEException):
    """Raised when server operations fail"""
    pass


class ValidationError(KSEException):
    """Raised when input validation fails"""
    pass


class TimeoutError(KSEException):
    """Raised when operations timeout"""
    pass


class ResourceNotFoundError(KSEException):
    """Raised when required resources are not found"""
    pass


class DomainNotAllowedError(CrawlerError):
    """Raised when attempting to crawl disallowed domain"""
    pass


class RobotsBlockedError(CrawlerError):
    """Raised when robots.txt blocks access"""
    pass


class HTTPError(CrawlerError):
    """Raised when HTTP request fails"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class IndexNotFoundError(ResourceNotFoundError):
    """Raised when search index is not found"""
    pass


class CacheError(StorageError):
    """Raised when cache operations fail"""
    pass


class SerializationError(StorageError):
    """Raised when serialization/deserialization fails"""
    pass
