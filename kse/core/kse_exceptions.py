"""
Custom Exception Classes

Defines exception hierarchy for KSE.
"""


class KSEException(Exception):
    """Base exception for all KSE errors."""
    pass


class DatabaseException(KSEException):
    """Raised when database operation fails."""
    pass


class ConnectionException(DatabaseException):
    """Raised when database connection fails."""
    pass


class SchemaException(DatabaseException):
    """Raised when schema operation fails."""
    pass


class CrawlerException(KSEException):
    """Raised when crawler operation fails."""
    pass


class URLException(CrawlerException):
    """Raised when URL processing fails."""
    pass


class HTTPException(CrawlerException):
    """Raised when HTTP request fails."""
    pass


class ParsingException(CrawlerException):
    """Raised when HTML parsing fails."""
    pass


class IndexingException(KSEException):
    """Raised when indexing operation fails."""
    pass


class TokenizationException(IndexingException):
    """Raised when tokenization fails."""
    pass


class SearchException(KSEException):
    """Raised when search operation fails."""
    pass


class QueryException(SearchException):
    """Raised when query processing fails."""
    pass


class RankingException(SearchException):
    """Raised when ranking fails."""
    pass


class ConfigException(KSEException):
    """Raised when configuration is invalid."""
    pass
