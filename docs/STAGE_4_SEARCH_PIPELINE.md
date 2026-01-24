# Stage 4: Search Pipeline

## Overview

Stage 4 implements the complete search pipeline that processes user queries and returns ranked results. This is the main interface for query execution.

**Components:**
- Query Parser (`kse_search_query.py`)
- Ranking Engine (`kse_search_ranking.py`)
- Search Executor (`kse_search_executor.py`)
- Result Cache (`kse_search_cache.py`)

## Query Parser

### Purpose
Normalizes and parses search queries to extract meaningful components.

### Key Classes

#### `QueryType` Enum
```python
class QueryType(Enum):
    SIMPLE = "simple"         # Single term: "python"
    PHRASE = "phrase"         # Quoted: "machine learning"
    BOOLEAN = "boolean"       # Operators: "python AND java"
    ADVANCED = "advanced"     # Filters: "site:wikipedia.org"
    MIXED = "mixed"           # Combination
```

#### `SearchQuery` Dataclass
Represents a parsed query:
```python
@dataclass
class SearchQuery:
    original_query: str
    query_type: QueryType
    terms: List[str]              # Keywords: ["python", "programming"]
    phrases: List[str]            # Exact phrases: ["machine learning"]
    exclude_terms: List[str]      # Negated: ["java"]
    domain_filter: Optional[str]  # site:wikipedia.org
    date_from: Optional[str]      # Results after date
    date_to: Optional[str]        # Results before date
    language_filter: Optional[str]
```

#### `QueryParser` Class
```python
parser = QueryParser(
    min_term_length=2,    # Skip very short terms
    max_terms=10,         # Limit number of terms
)

# Parse query
query = parser.parse("python site:wikipedia.org -java")

# Validate
if parser.validate_query(query):
    # Process...

# Get suggestions
suggestions = parser.suggest_correction(query_string)
```

### Supported Filters

| Filter | Format | Example |
|--------|--------|----------|
| Site | `site:domain.com` | `site:wikipedia.org` |
| Domain | `domain:domain.com` | `domain:github.com` |
| Date From | `from:YYYY-MM-DD` | `from:2024-01-01` |
| Date To | `to:YYYY-MM-DD` | `to:2024-12-31` |
| Language | `lang:xx` | `lang:sv` |

### Examples

```python
# Simple query
q1 = parser.parse("python")
# terms: ["python"], type: SIMPLE

# Phrase search
q2 = parser.parse('"machine learning" AI')
# phrases: ["machine learning"], terms: ["ai"], type: MIXED

# Boolean operators
q3 = parser.parse("python AND NOT java")
# terms: ["python"], exclude_terms: ["java"], type: BOOLEAN

# Advanced with filters
q4 = parser.parse("cybersecurity site:github.com from:2024-01-01")
# terms: ["cybersecurity"], domain_filter: "github.com", date_from: "2024-01-01"
```

## Ranking Engine

### Purpose
Ranks search results using multiple scoring factors.

### Key Classes

#### `RankingStrategy` Enum
```python
class RankingStrategy(Enum):
    RELEVANCE = "relevance"    # TF-IDF based ranking
    POPULARITY = "popularity"  # Domain authority
    RECENCY = "recency"        # Page freshness
    HYBRID = "hybrid"          # Weighted combination
```

#### `RankingScore` Dataclass
```python
@dataclass
class RankingScore:
    page_id: int
    url: str
    relevance_score: float    # 0-1 TF-IDF
    popularity_score: float   # 0-1 Authority/PageRank
    recency_score: float      # 0-1 Freshness
    final_score: float        # 0-1 Combined
```

#### `Ranker` Class
```python
ranker = Ranker(
    strategy=RankingStrategy.HYBRID,
    weights={                 # Default weights
        'relevance': 0.50,
        'popularity': 0.30,
        'recency': 0.20,
    }
)

# Rank results
scores = ranker.rank(results, RankingStrategy.HYBRID)

# Modify weights
ranker.set_weights({
    'relevance': 0.60,
    'popularity': 0.20,
    'recency': 0.20,
})

# Boost/penalize results
scores[0] = ranker.boost_result(scores[0], boost_factor=1.5)
```

### Scoring Components

#### Relevance Score
- **Source:** TF-IDF from Stage 3
- **Range:** 0-1
- **Calculation:** Normalized TF-IDF score

#### Popularity Score
- **Source:** Domain authority + inbound links
- **Range:** 0-1
- **Calculation:** 70% domain authority + 30% link count

```python
# Domain Authority Table
DOMAIN_AUTHORITY = {
    'sv.wikipedia.org': 0.95,   # Very high
    'governo.se': 0.90,         # Government
    'svt.se': 0.85,             # Major media
    'dn.se': 0.80,              # News
    'example.com': 0.50,        # Default
}
```

#### Recency Score
- **Source:** Page creation/update date
- **Range:** 0-1
- **Calculation:** Linear decay over 365 days
  - 0 days old: 1.0 (new)
  - 180 days old: 0.5
  - 365 days old: 0.1

### Ranking Formulas

**Hybrid (Default):**
```
final_score = 0.50 * relevance + 0.30 * popularity + 0.20 * recency
```

**Example:**
- Relevance: 0.85
- Popularity: 0.70
- Recency: 0.60
- **Final:** 0.50×0.85 + 0.30×0.70 + 0.20×0.60 = 0.745

## Search Executor

### Purpose
Executes queries against indexed data and returns ranked results.

### Key Classes

#### `SearchResult` Dataclass
```python
@dataclass
class SearchResult:
    page_id: int
    url: str
    title: str
    description: str
    domain: str
    score: float              # Final ranking score
    keywords: List[str]       # Top keywords from page
    snippet: Optional[str]    # Query-relevant excerpt
    relevance: float          # TF-IDF relevance
```

#### `ResultSet` Dataclass
```python
@dataclass
class ResultSet:
    query: str
    total_results: int        # Total matching
    returned_results: int     # Returned in this page
    results: List[SearchResult]
    execution_time_ms: float  # Query time
    ranking_strategy: str
    offset: int               # Pagination offset
    limit: int                # Results per page
    
    @property
    def has_more(self) -> bool:
        """Check if more results available."""
```

#### `SearchExecutor` Class
```python
executor = SearchExecutor(
    db_repository=db,                    # Database
    query_parser=QueryParser(),          # Custom parser (optional)
    ranker=Ranker(),                     # Custom ranker (optional)
)

# Execute search
results = executor.search(
    query_string="python programming",
    limit=10,                    # Results per page
    offset=0,                    # Start at result 0
    strategy="hybrid",           # Ranking strategy
)

# Get suggestions
suggestions = executor.get_suggestions("python pro", limit=5)
# Returns: ["python programming", "python projects", ...]

# Get related searches
related = executor.get_related_searches(page_id=123, limit=5)
# Returns: Top keywords from page
```

### Search Flow

```
User Query String
        ↓
    Parse Query (QueryParser)
        ↓
    Execute Search (Database)
      ├─ Search terms
      ├─ Search phrases
      ├─ Apply exclusions
      ├─ Apply filters
        ↓
    Rank Results (Ranker)
      ├─ Calculate scores
      ├─ Sort by score
        ↓
    Apply Pagination
        ↓
    Fetch Page Details (Database)
        ↓
    Return ResultSet
```

### Example Usage

```python
# Simple search
results = executor.search("machine learning")
for result in results.results:
    print(f"{result.title} ({result.score:.2f})")
    print(f"  {result.url}")

# Advanced search
results = executor.search(
    query_string="cybersecurity python -java site:github.com",
    limit=20,
    strategy="relevance",
)

print(f"Found {results.total_results} results in {results.execution_time_ms:.2f}ms")

# Pagination
if results.has_more:
    next_results = executor.search(
        query_string="machine learning",
        offset=results.limit,  # Get next page
    )
```

## Result Cache

### Purpose
Caches search results to improve performance for repeated queries.

### Key Classes

#### `CacheEntry` Dataclass
```python
@dataclass
class CacheEntry:
    query_hash: str           # MD5 hash of query
    query_string: str
    result_set: ResultSet
    created_at: datetime      # When cached
    accessed_at: datetime     # Last access
    hit_count: int            # Number of hits
    ttl_seconds: int          # Time to live
    
    @property
    def is_expired(self) -> bool:
        """Check if entry is expired."""
```

#### `SearchCache` Class
```python
cache = SearchCache(
    max_entries=1000,          # Maximum cache size
    default_ttl_seconds=3600,  # 1 hour TTL
)

# Cache result
cache.put("python programming", result_set, ttl_seconds=3600)

# Retrieve from cache
cached = cache.get("python programming")

# Clear specific entry
cache.clear("python programming")

# Clear entire cache
cache.clear()

# Cleanup expired entries
expired_count = cache.cleanup_expired()

# Get statistics
stats = cache.get_statistics()
print(f"Cache hits: {stats['hits']}")
print(f"Hit rate: {stats['hit_rate_percent']:.1f}%")

# Get top queries
top = cache.get_top_queries(limit=10)
for query, hits in top:
    print(f"{query}: {hits} hits")
```

### Statistics
```python
stats = cache.get_statistics()
{
    'entries': 45,                # Current cached queries
    'max_entries': 1000,
    'hits': 234,                  # Cache hits
    'misses': 89,                 # Cache misses
    'hit_rate_percent': 72.4,     # Hit rate %
    'puts': 89,                   # Items cached
    'evictions': 5,               # Items evicted
    'total_requests': 323,
}
```

### Cache Strategy

- **Max entries:** 1000 (default)
- **TTL:** 3600 seconds (1 hour default)
- **Eviction:** LRU (least recently used)
- **Hash:** MD5 of normalized query

## Integration Example

```python
from kse.search import (
    QueryParser,
    Ranker,
    SearchExecutor,
    SearchCache,
)
from kse.database import Repository

class KSESearchEngine:
    """Complete search engine."""
    
    def __init__(self, db_path: str):
        self.db = Repository(db_path)
        self.cache = SearchCache(max_entries=1000)
        self.executor = SearchExecutor(
            db_repository=self.db,
            query_parser=QueryParser(),
            ranker=Ranker(),
        )
    
    def search(self, query: str, limit: int = 10) -> ResultSet:
        """Execute search with caching."""
        # Check cache
        cached = self.cache.get(query)
        if cached:
            return cached
        
        # Execute search
        results = self.executor.search(query, limit=limit)
        
        # Cache results
        if results.total_results > 0:
            self.cache.put(query, results)
        
        return results
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return self.cache.get_statistics()
```

## Testing

Run tests:
```bash
pytest tests/test_search_modules.py -v
```

Tests cover:
- Query parsing (simple, phrase, boolean, filters)
- Query normalization and validation
- Result ranking (relevance, popularity, recency, hybrid)
- Ranking strategies comparison
- Cache put/get operations
- Cache expiration and cleanup
- Cache statistics
- Result pagination

## Next Steps: Stage 5

Stage 5 will implement:
- API endpoints for search
- Web interface
- Performance optimization
- Result snippets extraction
- Search analytics
