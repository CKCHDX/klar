"""
KSE Search Engine Module

Provides indexing, ranking, and search capabilities for the Klar Search Engine.
"""

from .kse_indexer import KSEIndexer
from .kse_tokenizer import Tokenizer, stem_swedish
from .kse_ranker import KSERanker, TFIDFRanker
from .kse_search import SearchEngine, SearchResult

__version__ = "1.0.0"
__all__ = [
    "KSEIndexer",
    "Tokenizer",
    "stem_swedish",
    "KSERanker",
    "TFIDFRanker",
    "SearchEngine",
    "SearchResult",
]
