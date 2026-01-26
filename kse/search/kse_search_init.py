"""
kse/search/__init__.py - Search Engine API

Components:
  - SearchCore: Main search orchestrator
  - QueryParser: Query parsing & expansion
  - ResultFilter: Result filtering & deduplication
  - Pagination: Result pagination
  - SnippetGenerator: Snippet generation
  - SearchAnalytics: Analytics tracking

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from .kse_search_core import SearchCore, KSESearchException
from .kse_query_parser import QueryParser
from .kse_result_filter import ResultFilter
from .kse_pagination import Pagination
from .kse_snippet_generator import SnippetGenerator
from .kse_search_analytics import SearchAnalytics

__all__ = [
    # Core
    "SearchCore",
    
    # Processing
    "QueryParser",
    "ResultFilter",
    "Pagination",
    "SnippetGenerator",
    
    # Analytics
    "SearchAnalytics",
    
    # Exceptions
    "KSESearchException",
]

__version__ = "1.0.0"
__author__ = "Klar Development Team"


# Quick start examples
"""
QUICK START - Search Layer

1. Search:
    from kse.search import SearchCore
    from kse.indexing import IndexerPipeline
    from kse.ranking import RankingCore
    from kse.cache import CacheManager
    
    index = IndexerPipeline(...)
    ranker = RankingCore(cache)
    cache = CacheManager()
    
    search = SearchCore(index, ranker, cache)
    results = search.search("svenska universitet")

2. Query parsing:
    from kse.search import QueryParser
    
    parser = QueryParser()
    parsed = parser.parse("svenska universitet")
    expansions = parser.expand_query("svenska")

3. Result filtering:
    from kse.search import ResultFilter
    
    filter = ResultFilter()
    filtered = filter.deduplicate(results)
    diversified = filter.diversify(filtered)

4. Pagination:
    from kse.search import Pagination
    
    paginator = Pagination(page_size=10)
    page = paginator.paginate(results, page=1)

5. Snippet generation:
    from kse.search import SnippetGenerator
    
    generator = SnippetGenerator()
    snippet = generator.generate(document, ["svenska"])

6. Search analytics:
    from kse.search import SearchAnalytics
    
    analytics = SearchAnalytics()
    analytics.track_search(query, result_count, time)
    print(analytics.get_summary())

SEARCH PIPELINE:

Input: User Query
    ↓
Query Parsing (Phase 8)
├─ Tokenization
├─ Stopword removal
├─ Query expansion
└─ Operator extraction
    ↓
Document Retrieval (Phase 6)
├─ Index search
├─ Term matching
└─ Initial filtering
    ↓
Result Ranking (Phase 7)
├─ TF-IDF scoring
├─ PageRank
├─ Authority scoring
├─ Recency scoring
├─ Keyword density
├─ Link structure
└─ Regional relevance
    ↓
Result Filtering (Phase 8)
├─ Deduplication
├─ Spam removal
├─ Diversity filtering
└─ Quality scoring
    ↓
Pagination (Phase 8)
├─ Page calculation
├─ Offset management
└─ Page metadata
    ↓
Snippet Generation (Phase 8)
├─ Text extraction
├─ Query highlighting
└─ Truncation
    ↓
Analytics Tracking (Phase 8)
├─ Query recording
├─ Performance metrics
├─ Popular queries
└─ User stats
    ↓
Output: Ranked Results
    ├─ URL
    ├─ Title
    ├─ Snippet
    ├─ Score
    └─ Metadata

EXAMPLE SEARCH FLOW:

Query: "svenska universitet"
    ↓
Parse Query
├─ Tokens: ["svenska", "universitet"]
├─ Expanded: ["svenska högskolom", "swedish university"]
└─ Operators: {}
    ↓
Find Documents (from index)
└─ 15,432 matching documents
    ↓
Rank Results (7 factors)
├─ TF-IDF:      Score each document
├─ PageRank:    Apply link authority
├─ Authority:   .se domains boost
├─ Recency:     Recent content boost
├─ Density:     Keyword optimization
├─ Links:       Link structure score
└─ Regional:    Swedish priority
    ↓
Filter Results
├─ Deduplicat: 1 per domain → 2,345 docs
├─ Spam:       Remove known spam → 2,340 docs
└─ Diversify:  Max 2 per domain → 2,340 docs
    ↓
Paginate Results (10 per page)
└─ Page 1 of 234 pages
    ↓
Generate Snippets
└─ Extract best text section + query highlight
    ↓
Track Analytics
└─ Recorded: 1 search, 10 results, 0.042s

Output: 10 ranked results with snippets

ARCHITECTURE:

kse/search/
├── kse_search_core.py              Main search orchestrator
├── kse_query_parser.py             Query parsing & expansion
├── kse_result_filter.py            Result filtering
├── kse_pagination.py               Result pagination
├── kse_snippet_generator.py        Snippet generation
├── kse_search_analytics.py         Analytics tracking
└── __init__.py                     Public API

INTEGRATION:

- Phase 6 (indexing): Search in index
- Phase 7 (ranking): Rank results
- Phase 3 (cache): Cache results
- Phase 9 (server): HTTP API
- Phase 10 (gui): Web UI

PERFORMANCE TARGETS:

- Query execution: < 100ms (cached)
- Result ranking: < 50ms
- Page generation: < 20ms
- Total latency: < 170ms for cold search

FEATURES:

Query Processing:
  - Query parsing & normalization
  - Stopword removal
  - Query expansion (synonyms)
  - Search operators (site:, -)
  - Exact phrase matching
  - Boolean operators

Result Management:
  - Domain deduplication
  - Spam filtering
  - Diversity optimization
  - Quality scoring
  - Ranking integration

Result Presentation:
  - Pagination support
  - Snippet generation
  - Query highlighting
  - Metadata extraction
  - Result formatting

Analytics:
  - Query tracking
  - Performance metrics
  - Popular queries
  - Search trends
  - User insights
"""
