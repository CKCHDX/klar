# Wikipedia Handler Integration - Complete Documentation

## Overview

Wikipedia Handler 1.0 is a **dedicated algorithm** for handling Wikipedia searches in Klar. Wikipedia is NOT treated as a regular domain - it has its own explicit, specialized search logic.

## Architecture

### System Components

```
Klar Search Engine
├── SVEN 3.2 (Query Expansion)
├── Regular Domain Search (Whitelisted domains)
└── Wikipedia Handler 1.0 (SEPARATE ALGORITHM)
    ├── Query Detection
    ├── Topic Normalization
    ├── Direct API Search
    ├── Fallback Search
    └── Infobox Extraction
```

## Key Features

### 1. Query Detection
Automatically detects Wikipedia-suitable queries:
- "vem är X?" (Who is X?)
- "vad är Y?" (What is Y?)
- "var ligger Z?" (Where is Z?)
- Biographical/definition queries
- Encyclopedia topics

### 2. Direct Article Search
Uses Wikipedia API to retrieve direct article URLs:
- Normalizes topic (removes question words, punctuation)
- Queries Wikipedia API with title search
- Handles redirects automatically
- Returns direct article URL

### 3. Fallback Search
If direct search fails:
- Uses Wikipedia search API
- Gets search suggestions
- Returns closest matching article

### 4. Language Negotiation
- **Primary**: Swedish Wikipedia (sv.wikipedia.org)
- **Fallback**: English Wikipedia (en.wikipedia.org)
- Configurable in setup wizard

### 5. Advanced Features
- Infobox data extraction
- Disambiguation page detection
- Multiple search results
- Request retry logic
- Timeout handling
- Search result caching

## Implementation Details

### Files Added/Modified

#### NEW FILES:
- `algorithms/wikipedia_handler.py` - Core Wikipedia Handler algorithm

#### MODIFIED FILES:
- `engine/search_engine.py` - Integrated Wikipedia Handler
- `engine/loki_system.py` - Added handler support for caching
- `engine/setup_wizard.py` - Added Wikipedia configuration step

### Integration Flow

```
User Query
    ↓
[SVEN] Query Analysis
    ↓
[Wikipedia Handler] is_wikipedia_query()
    ├─ YES → Use dedicated algorithm
    │   ├─ normalize_topic()
    │   ├─ search_direct('sv')
    │   ├─ Fallback: search_direct('en')
    │   └─ Return Wikipedia URL
    │
    └─ NO → Continue with regular domain search
        ├─ [Domain Categories] Match domains
        ├─ [Whitelist] Filter allowed domains
        └─ [BM25/TF-IDF] Rank results
```

## API Reference

### WikipediaHandler Class

```python
from algorithms.wikipedia_handler import WikipediaHandler

wh = WikipediaHandler(timeout=5.0, retry_attempts=2)

# Detect if query is suitable for Wikipedia
is_wiki = wh.is_wikipedia_query(query)  # → bool

# Normalize topic for API
topic_clean = wh.normalize_topic("vem är Elon Musk")  # → "Elon Musk"

# Search with automatic language fallback
url = wh.search_with_fallback("Albert Einstein")  # → URL or None

# Search specific language
url_sv = wh.search_direct("Stockholm", lang='sv')  # → URL or None
url_en = wh.search_direct("Stockholm", lang='en')  # → URL or None

# Get multiple search results
results = wh.get_search_results("Python", limit=5)  # → [{'title': ..., 'url': ...}, ...]

# Extract infobox data
info = wh.extract_infobox_data("Marie Curie")  # → {'intro': ..., 'title': ...}

# Check if disambiguation page
is_disambiguation = wh.is_disambiguation_page("Bank")  # → bool

# Clear cache
wh.clear_cache()
```

## Setup Configuration

### Setup Wizard Steps
1. **Welcome** - Introduction
2. **Offline Mode (LOKI)** - Enable/disable local caching
3. **Wikipedia Handler** - Enable/disable dedicated algorithm
   - Select preferred languages (Swedish/English)
4. **Data Directory** - Choose cache location
5. **Summary** - Review configuration

### Configuration File
```json
{
  "offline_mode": true,
  "wikipedia_handler": true,
  "wikipedia_languages": ["sv", "en"],
  "data_path": "/home/user/.klar/klar_data",
  "setup_complete": true
}
```

## LOKI System Updates

### Handlers Configuration
```json
{
  "wikipedia": {
    "enabled": true,
    "cache_articles": true,
    "languages": ["sv", "en"],
    "timeout": 5.0,
    "retry_attempts": 2
  },
  "custom_handlers": {}
}
```

### Cache Separation
Wikipedia articles cached separately:
```
~/.klar/klar_data/loki/cache/
├── wikipedia/        # Wikipedia articles
│   └── sv.wikipedia.org/
│   └── en.wikipedia.org/
├── regular/          # Regular domain pages
│   └── example.com/
└── ...
```

### New LOKI Methods
```python
from engine.loki_system import LOKISystem

loki = LOKISystem("/path/to/data")

# Cache with handler type
loki.cache_page(page_data, handler_type='wikipedia')

# Search with handler filter
results = loki.offline_search(query, handler_filter='wikipedia')

# Clear specific handler cache
loki.clear_handler_cache('wikipedia')

# Get handler statistics
stats = loki.get_cache_stats()  # Includes handler breakdown
```

## Search Engine Integration

### SearchEngine Changes
```python
from engine.search_engine import SearchEngine
from algorithms.wikipedia_handler import WikipediaHandler

se = SearchEngine()
# Wikipedia Handler automatically initialized

results = se.search("vem är Greta Thunberg")
# Returns:
# {
#   'results': [...],
#   'wikipedia_prioritized': True,
#   'wikipedia_algorithm': 'Dedicated WikipediaHandler 1.0'
# }
```

## Query Examples

### Wikipedia Queries
```
"vem är Albert Einstein" → sv.wikipedia.org/wiki/Albert_Einstein
"what is photosynthesis" → en.wikipedia.org/wiki/Photosynthesis
"var ligger Tokyo" → sv.wikipedia.org/wiki/Tokyo
"vad är DNA" → sv.wikipedia.org/wiki/DNA
"Python programspråk" → sv.wikipedia.org/wiki/Python_(programsp%C3%A5k)
```

### Regular Domain Queries
```
"pizza restaurant Stockholm" → Domain search (regular algorithm)
"weather forecast" → Domain search (regular algorithm)
"news today" → Domain search (regular algorithm)
```

## Error Handling

### Graceful Degradation
1. **Direct search fails** → Try fallback search
2. **Fallback fails (Swedish)** → Try English Wikipedia
3. **Both fail** → Return Wikipedia homepage as fallback
4. **Wikipedia not whitelisted** → Continue with regular domain search

## Performance

### Optimizations
- **Precomputed index** in SVEN (BM25/TF-IDF)
- **Request retry logic** with exponential backoff
- **Search result caching** (1 hour TTL)
- **Parallel domain search** while Wikipedia loads
- **Lazy loading** of infobox data (on demand)

### Timeouts
- API timeout: 5 seconds
- Search timeout: 15 seconds total
- Retry attempts: 2

## Testing

### Test Cases
```python
# Test Wikipedia detection
assert wh.is_wikipedia_query("vem är X") == True
assert wh.is_wikipedia_query("random search") == False

# Test topic normalization
assert wh.normalize_topic("vem är Elon Musk") == "Elon Musk"
assert wh.normalize_topic("What is AI?") == "Ai"

# Test direct search
url = wh.search_direct("Stockholm", lang='sv')
assert 'sv.wikipedia.org' in url

# Test fallback
url = wh.search_with_fallback("UnknownTopic123")
assert url is None or 'wikipedia.org' in url
```

## Future Enhancements

1. **Additional handlers**
   - Reddit Handler (for discussions)
   - Stack Overflow Handler (for programming Q&A)
   - GitHub Handler (for code repositories)

2. **Wikipedia improvements**
   - Language auto-detection from query
   - Category-based article suggestions
   - Related articles recommendation
   - Offline Wikipedia mirror support

3. **Caching enhancements**
   - Handler-specific cache policies
   - Intelligent cache size management
   - Cross-handler search optimization

## Commits

- `922cfa36` - Wikipedia Handler 1.0 created
- `cac89701` - Search Engine integration
- `4a513ab1` - LOKI System handler support
- `5434790c` - Setup Wizard configuration

## Security & Privacy

- Wikipedia API calls use standard requests library
- No personal data collected
- Cache stored locally only
- All searches via whitelisted domains only
- HTTPS connections enforced

## License

Part of Klar - Swedish search engine
