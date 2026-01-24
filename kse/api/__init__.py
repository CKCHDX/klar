"""
API Module

Stage 5: REST API and Web Interface
"""

from .kse_api_server import KSEAPIServer
from .kse_api_routes import register_routes
from .kse_api_models import (
    QueryRequest,
    SearchResponse,
    ResultItem,
    SuggestionResponse,
    CacheStatsResponse,
)

__all__ = [
    'KSEAPIServer',
    'register_routes',
    'QueryRequest',
    'SearchResponse',
    'ResultItem',
    'SuggestionResponse',
    'CacheStatsResponse',
]

__version__ = '5.0.0'
__stage__ = 'Stage 5: API & Web Interface'
