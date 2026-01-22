"""
Klar Search Engine (KSE) - Core Package
Swedish-optimized search engine for Sweden
Version: 1.0.0 (Production)
"""

__version__ = "1.0.0"
__author__ = "Alex Jonsson (CKCHDX)"
__license__ = "MIT"
__description__ = "Enterprise-grade Swedish search engine"

from .kse_nlp import SwedishNLP
from .kse_crawler import WebCrawler
from .kse_index import InvertedIndex
from .kse_search import SearchEngine
from .kse_ranking import RankingEngine
from .kse_database import PostgreSQLManager
from .kse_cache import CacheManager

__all__ = [
    "SwedishNLP",
    "WebCrawler",
    "InvertedIndex",
    "SearchEngine",
    "RankingEngine",
    "PostgreSQLManager",
    "CacheManager",
]
