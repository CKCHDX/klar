# Stage 4: Search Pipeline

## Quick Overview

Stage 4 implements the complete search pipeline that transforms user queries into ranked, cached results.

**Components:**
- **Query Parser:** Normalizes and parses queries
- **Ranking Engine:** Scores results using multiple factors
- **Search Executor:** Executes searches against indexed data
- **Result Cache:** Improves performance for repeated queries

## Quick Start

### Basic Search

```python
from kse.search import QueryParser, SearchExecutor
from kse.database import Repository

# Initialize
db = Repository("path/to/index.db")
executor = SearchExecutor(db)

# Search
results = executor.search("python programming")

# Results
for result in results.results:
    print(f"{result.title} ({result.score:.2f})")
    print(f"  {result.url}")
```

### With Caching

```python
from kse.search import SearchCache

cache = SearchCache(max_entries=1000)

def search_with_cache(query: str):
    # Check cache
    cached = cache.get(query)
    if cached:
        return cached
    
    # Execute search
    results = executor.search(query)
    
    # Cache results
    cache.put(query, results)
    
    return results

# First search: executes
results1 = search_with_cache("machine learning")

# Second search: from cache
results2 = search_with_cache("machine learning")
```

### Query Syntax

```python
from kse.search import QueryParser

parser = QueryParser()

# Simple search
q1 = parser.parse("python")

# Phrase search
q2 = parser.parse('"machine learning" python')

# Boolean operators
q3 = parser.parse("python AND NOT java")

# Filters
q4 = parser.parse("cybersecurity site:github.com from:2024-01-01")

# Exclusions
q5 = parser.parse("python -java -csharp")
```

### Ranking Strategies

```python
from kse.search import Ranker, RankingStrategy

ranker = Ranker()

# Different strategies
ranked_rel = ranker.rank(results, RankingStrategy.RELEVANCE)
ranked_pop = ranker.rank(results, RankingStrategy.POPULARITY)
ranked_rec = ranker.rank(results, RankingStrategy.RECENCY)
ranked_hyb = ranker.rank(results, RankingStrategy.HYBRID)  # Default

# Custom weights
ranker.set_weights({
    'relevance': 0.60,
    'popularity': 0.25,
    'recency': 0.15,
})
```

## Architecture

### Data Flow

```
User Query
    ↓
[Query Parser]
  ├─ Normalize
  ├─ Extract terms/phrases
  ├─ Parse filters
    ↓
[Search Executor]
  ├─ Search database
  ├─ Apply filters
  ├─ Combine results
    ↓
[Ranking Engine]
  ├─ Calculate relevance
  ├─ Calculate popularity
  ├─ Calculate recency
  ├─ Combine scores
    ↓
[Result Cache]
  ├─ Store result set
  ├─ Track statistics
    ↓
[Ranked Results]
```

## Components in Detail

### 1. Query Parser

**File:** `kse/search/kse_search_query.py`

**Features:**
- Query normalization (lowercase, remove extra spaces)
- Term extraction
- Phrase detection ("quoted strings")
- Boolean operators (AND, OR, NOT)
- Filter parsing (site:, domain:, from:, to:, lang:)
- Query type classification
- Validation

**Usage:**
```python
from kse.search import QueryParser, QueryType

parser = QueryParser(min_term_length=2, max_terms=10)
query = parser.parse("machine learning site:github.com")

assert query.query_type == QueryType.ADVANCED
assert "machine" in query.terms
assert "learning" in query.terms
assert query.domain_filter == "github.com"
```

### 2. Ranking Engine

**File:** `kse/search/kse_search_ranking.py`

**Features:**
- TF-IDF relevance scoring
- Domain authority scoring
- Page freshness/recency scoring
- Multiple ranking strategies
- Customizable weights
- Result boosting/penalizing

**Scoring Components:**

| Component | Weight | Source |
|-----------|--------|--------|
| Relevance | 50% | TF-IDF from Stage 3 |
| Popularity | 30% | Domain authority |
| Recency | 20% | Page age |

**Usage:**
```python
from kse.search import Ranker, RankingStrategy

ranker = Ranker(strategy=RankingStrategy.HYBRID)

# Default weights
scores = ranker.rank(results)

# Custom weights
ranker.set_weights({
    'relevance': 0.70,
    'popularity': 0.20,
    'recency': 0.10,
})
scores = ranker.rank(results)
```

### 3. Search Executor

**File:** `kse/search/kse_search_executor.py`

**Features:**
- Query execution against database
- Multi-term search
- Phrase matching
- Exclusion filtering
- Domain filtering
- Date range filtering
- Result pagination
- Search suggestions
- Related searches

**Usage:**
```python
from kse.search import SearchExecutor
from kse.database import Repository

db = Repository("index.db")
executor = SearchExecutor(db)

# Execute search
results = executor.search(
    query_string="python programming",
    limit=10,        # 10 results per page
    offset=0,        # Start at first result
    strategy="hybrid",
)

# Check for more
if results.has_more:
    next_results = executor.search(
        "python programming",
        offset=results.limit,  # Next page
    )

# Suggestions
suggestions = executor.get_suggestions("python pro", limit=5)

# Related
related = executor.get_related_searches(page_id=123)
```

### 4. Result Cache

**File:** `kse/search/kse_search_cache.py`

**Features:**
- In-memory result caching
- Automatic expiration (TTL)
- LRU eviction
- Hit/miss tracking
- Cache statistics
- Top queries tracking

**Usage:**
```python
from kse.search import SearchCache

cache = SearchCache(
    max_entries=1000,
    default_ttl_seconds=3600,  # 1 hour
)

# Cache result
cache.put("query", result_set, ttl_seconds=3600)

# Retrieve
result = cache.get("query")

# Statistics
stats = cache.get_statistics()
print(f"Hit rate: {stats['hit_rate_percent']:.1f}%")

# Top queries
top = cache.get_top_queries(limit=10)
```

## Query Syntax Reference

### Basic Queries

```
python                      # Single term
python programming          # Multiple terms (AND)
"machine learning"          # Phrase (exact match)
```

### Boolean Operators

```
python AND java             # Both terms required
python OR java              # Either term
python NOT java             # Exclude term
-java                       # Exclude (shorthand)
```

### Filters

```
site:github.com             # Specific site
domain:wikipedia.org        # Specific domain
from:2024-01-01             # After date
to:2024-12-31               # Before date
lang:sv                     # Swedish
```

### Complex Examples

```
python site:github.com -malware
"machine learning" (tensorflow OR pytorch)
cybersecurity from:2024-01-01 lang:en
python AND (django OR flask) -celery
```

## Ranking Strategies

### Relevance
Ranks by TF-IDF score only. Best when query terms are most important.
```python
ranked = ranker.rank(results, RankingStrategy.RELEVANCE)
```

### Popularity
Ranks by domain authority and link count. Best for finding authoritative sources.
```python
ranked = ranker.rank(results, RankingStrategy.POPULARITY)
```

### Recency
Ranks by page age. Best for time-sensitive queries.
```python
ranked = ranker.rank(results, RankingStrategy.RECENCY)
```

### Hybrid (Default)
Combines all factors with weights:
```
score = 0.50 × relevance + 0.30 × popularity + 0.20 × recency
```

## Testing

### Run All Tests

```bash
pytest tests/test_search_modules.py -v
```

### Run Specific Tests

```bash
# Query parser tests
pytest tests/test_search_modules.py::TestQueryParser -v

# Ranking tests
pytest tests/test_search_modules.py::TestRanker -v

# Cache tests
pytest tests/test_search_modules.py::TestSearchCache -v
```

## Performance

### Typical Metrics

- **Query parsing:** < 1ms
- **Search execution:** 10-50ms (depends on index size)
- **Result ranking:** < 5ms
- **Cache hit:** < 1ms
- **Cache miss:** 15-50ms (search + ranking)

### Optimization Tips

1. **Increase cache size** for frequently searched queries
2. **Tune ranking weights** for your use case
3. **Use filters** to narrow search scope
4. **Batch searches** when possible
5. **Monitor cache hit rate** and adjust TTL

## Example Integration

```python
from kse.search import (
    QueryParser,
    Ranker,
    SearchExecutor,
    SearchCache,
)
from kse.database import Repository

class KlarSearchEngine:
    """Complete search engine combining all Stage 4 components."""
    
    def __init__(self, db_path: str):
        self.db = Repository(db_path)
        self.cache = SearchCache(max_entries=5000)
        self.executor = SearchExecutor(
            db_repository=self.db,
            query_parser=QueryParser(),
            ranker=Ranker(),
        )
    
    def search(self, query: str, limit: int = 10) -> dict:
        """Execute search with caching."""
        # Check cache
        cached = self.cache.get(query)
        if cached:
            return {
                'results': cached.results,
                'total': cached.total_results,
                'from_cache': True,
            }
        
        # Execute search
        results = self.executor.search(query, limit=limit)
        
        # Cache
        if results.total_results > 0:
            self.cache.put(query, results)
        
        return {
            'results': results.results,
            'total': results.total_results,
            'time_ms': results.execution_time_ms,
            'from_cache': False,
        }
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return self.cache.get_statistics()

# Usage
engine = KlarSearchEngine("data/index.db")

# Search
result = engine.search("python programming", limit=20)
print(f"Found {result['total']} results")
for res in result['results'][:5]:
    print(f"  {res.title}")

# Stats
stats = engine.get_stats()
print(f"Cache hit rate: {stats['hit_rate_percent']:.1f}%")
```

## Next Steps

→ **Stage 5:** API & Web Interface
- REST API endpoints
- Web search interface
- Result snippets
- Search analytics

## References

- [Full Documentation](./STAGE_4_SEARCH_PIPELINE.md)
- [Demo Script](../examples/stage4_search_demo.py)
- [Test Suite](../tests/test_search_modules.py)
