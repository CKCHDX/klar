# LOKI - Offline Search & Local Index System

## Overview

LOKI (Local Offline Knowledge Index) is an advanced offline search system for Klar 3.1 that enables users to search previously visited domains and pages without internet connectivity.

**Status:** Feature Specification (Ready for Implementation)

---

## Features

### 1. First-Run Setup Dialog

When Klar launches for the first time, users see a setup wizard:

```
┌─────────────────────────────────────────┐
│   Klar 3.0 - Første gangs instillinger   │
├─────────────────────────────────────────┤
│                                          │
│  Vil du aktivere offlinsökning (LOKI)?  │
│  Med LOKI kan du söka på tidigare        │
│  besökta sidor även utan internet.       │
│                                          │
│  ☐ Aktivera LOKI offlinökning           │
│                                          │
│  Välj lagringsplats för Klar-data:      │
│  [  ~/Klar-data  ]  [Bläddra...]        │
│                                          │
│  ⓘ Du kan alltid ändra detta senare      │
│                                          │
│  [  Nästa  ]  [  Hoppa över  ]          │
│                                          │
└─────────────────────────────────────────┘
```

### 2. Data Structure

#### Directory Layout
```
klar_data/
├── loki/
│   ├── cache/
│   │   ├── svt.se/
│   │   │   ├── index.db
│   │   │   ├── pages/
│   │   │   │   ├── page_001.json
│   │   │   │   ├── page_002.json
│   │   │   │   └── ...
│   │   │   └── metadata.json
│   │   ├── 1177.se/
│   │   └── ...
│   ├── search_index.db
│   ├── settings.json
│   └── sync_log.json
├── search_history.json
└── user_preferences.json
```

#### Page Cache Format
```json
{
  "url": "https://www.svt.se/nyheter/article123456",
  "title": "Ny teknologi revolutionerar hemmet",
  "description": "Forskare presenterar upptäckt...",
  "domain": "svt.se",
  "content": "full page text content...",
  "keywords": ["teknologi", "hemmet", "forskning"],
  "timestamp": "2025-12-08T14:00:00Z",
  "size_bytes": 45230,
  "status_code": 200,
  "language": "sv"
}
```

### 3. Offline Search Algorithm

#### Index Structure (SQLite)
```sql
CREATE TABLE pages (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE,
    title TEXT,
    domain TEXT,
    timestamp DATETIME,
    cached_size INTEGER
);

CREATE TABLE keywords (
    id INTEGER PRIMARY KEY,
    page_id INTEGER,
    keyword TEXT,
    frequency INTEGER,
    FOREIGN KEY(page_id) REFERENCES pages(id)
);

CREATE TABLE search_history (
    id INTEGER PRIMARY KEY,
    query TEXT,
    timestamp DATETIME,
    results_count INTEGER
);
```

#### Offline Search Flow
```python
def offline_search(query: str) -> List[Dict]:
    """
    1. Check network status
    2. If offline, use LOKI cache
    3. Apply SVEN expansion to offline query
    4. Query SQLite index with expanded terms
    5. Score results by relevance & recency
    6. Return cached results
    """
    
    # Expand query with SVEN
    expanded_terms = sven.expand_query(query)
    
    # Search local SQLite index
    results = []
    for term in expanded_terms:
        db_results = sqlite_search(term)
        results.extend(db_results)
    
    # Score by relevance & recency
    scored = score_results(results, query, expanded_terms)
    
    # Mark as from offline cache
    for result in scored:
        result['source'] = 'offline_cache'
        result['cached_timestamp'] = result['timestamp']
    
    return scored
```

### 4. Automatic Caching

When LOKI is enabled, every page visited online is automatically cached:

```python
def on_page_loaded(page_data: Dict):
    """Automatically cache page when loaded"""
    
    if loki_enabled and is_whitelisted_domain(page_data['domain']):
        # Extract metadata
        metadata = extract_metadata(page_data)
        
        # Save to cache
        save_to_cache(metadata)
        
        # Update search index
        update_search_index(metadata)
        
        # Log sync
        sync_log.append({
            'url': page_data['url'],
            'timestamp': datetime.now(),
            'action': 'cached',
            'size': len(page_data['content'])
        })
        
        # Update statistics
        update_statistics()
```

### 5. Storage Management

#### Disk Space Management
```python
class LOKIStorageManager:
    MAX_CACHE_SIZE_MB = 500  # Configurable
    MAX_PAGES_PER_DOMAIN = 1000
    CACHE_RETENTION_DAYS = 90
    
    def manage_storage():
        """Automatically manage cache size"""
        
        # Check total size
        if get_cache_size() > MAX_CACHE_SIZE_MB:
            # Remove oldest pages first (LRU)
            remove_oldest_pages()
        
        # Check per-domain limits
        for domain in get_cached_domains():
            if get_domain_page_count(domain) > MAX_PAGES_PER_DOMAIN:
                remove_oldest_domain_pages(domain)
        
        # Remove expired entries
        if is_older_than(CACHE_RETENTION_DAYS):
            delete_page()
```

### 6. UI Integration

#### Settings Panel
```
Inställningar > Offline-sökning (LOKI)

┌──────────────────────────────────────┐
│  Offline-sökning (LOKI)              │
├──────────────────────────────────────┤
│                                      │
│  ☑ Aktiverad                         │
│                                      │
│  Lagringsplats:                      │
│  ~/Klar-data/loki  [Ändra...]       │
│                                      │
│  Cachad data:                        │
│  347 MB av 500 MB [████████░░]      │
│                                      │
│  Cachade domäner: 23                │
│  Cachade sidor: 847                 │
│  Senaste uppdatering: 2 timmar sen  │
│                                      │
│  [  Rensa cache  ]  [Statistik]      │
│                                      │
└──────────────────────────────────────┘
```

#### Search Results - Mixed Online/Offline
```
Sökning: "ont i halsen"
Resultat: 8 (5 online, 3 offline)

┌─ Från online (SVT.se) ─────────────┐
│ 1. Öm hals - Vanliga orsaker        │
│    Hälsovårdsinformation från 1177  │
│    ✓ Verifierad  ⚡ Snabb            │
├─────────────────────────────────────┤
│ 2. Halsbränna eller öm hals?        │
│    Apotek tips från Apoteket        │
├─────────────────────────────────────┤
┌─ Från offline cache ─────────────────┐
│ 3. Hemmedel mot öm hals [15 dec]   │
│    Sparad från 1177.se              │
│    💾 Offline  ℹ Cachad             │
├─────────────────────────────────────┤
│ 4. Antibiotika behandling [10 dec]  │
│    Sparad från SVT                  │
└─────────────────────────────────────┘
```

### 7. Synchronization

#### When Connection Restored
```python
def on_connection_restored():
    """Sync offline searches when connection returns"""
    
    # Get all queries made offline
    offline_queries = sync_log.get_offline_queries()
    
    for query in offline_queries:
        # Re-run with online search
        online_results = online_search(query)
        
        # Merge and update cache
        merged = merge_results(offline_results, online_results)
        
        # Update timestamps
        for result in merged:
            result['last_verified'] = datetime.now()
        
        # Log sync
        sync_log.append({
            'query': query,
            'action': 'resync_online',
            'timestamp': datetime.now()
        })
```

### 8. Privacy & Security

- **Local-only storage:** All cached data stays on user's device
- **Encryption option:** Optional AES-256 encryption for sensitive cache
- **User control:** Users can:
  - Clear specific domains
  - Clear all cache
  - Exclude sensitive searches from cache
  - Auto-delete after X days
- **No tracking:** LOKI doesn't send cache data anywhere

### 9. Implementation Phases

#### Phase 1 (Current)
- ✅ SVEN query expansion
- ✅ Domain whitelist bypass
- ✅ Demographic detection
- ⏳ LOKI specification (this document)

#### Phase 2 (Next)
- SQLite search index creation
- Automatic page caching
- Offline search implementation
- First-run setup wizard

#### Phase 3 (Advanced)
- Encryption support
- Compression of cached pages
- Sync across devices (optional)
- Advanced analytics

---

## API Reference

### LOKI Core Methods

```python
class LOKI:
    def __init__(self, storage_path: str)
    def cache_page(self, page_data: Dict) -> bool
    def offline_search(self, query: str) -> List[Dict]
    def get_cache_stats(self) -> Dict
    def clear_domain_cache(self, domain: str) -> bool
    def clear_all_cache(self) -> bool
    def get_cached_domains(self) -> List[str]
    def get_cached_pages(self, domain: str) -> List[Dict]
    def export_cache(self, format: str = 'json') -> bytes
```

---

## Configuration

```json
{
  "loki": {
    "enabled": true,
    "storage_path": "~/Klar-data/loki",
    "max_cache_size_mb": 500,
    "max_pages_per_domain": 1000,
    "retention_days": 90,
    "encryption": false,
    "auto_cleanup": true,
    "cache_images": false,
    "compression": true
  }
}
```

---

## Performance Metrics

### Expected Performance
- **Offline search:** < 200ms for 1000 cached pages
- **Memory usage:** ~50-100MB for index
- **Cache write:** ~100ms per page
- **Cache read:** ~10ms per page

### Scalability
- **Max pages:** 50,000+ (with 500MB cache)
- **Max domains:** 500+
- **Search terms:** 100,000+ indexed keywords

---

## Testing Checklist

- [ ] First-run setup wizard works
- [ ] Pages cache automatically when LOKI enabled
- [ ] Offline search returns cached pages
- [ ] Mixed online/offline results display correctly
- [ ] Cache statistics accurate
- [ ] Storage management enforces limits
- [ ] Cache clear functions work
- [ ] Sync works when connection restored
- [ ] Performance meets targets
- [ ] Privacy preserved (local storage only)

---

## Future Enhancements

1. **Full-text search indexing** - Index page content, not just titles
2. **Smart prefetching** - Predict and cache likely next pages
3. **Device sync** - Sync cache across user's devices (encrypted)
4. **Analytics** - Understand which pages are most useful offline
5. **Collaborative cache** - Optional community-shared cache index
6. **Voice search** - Offline voice search in cache

---

**Status:** Ready for Phase 2 implementation
**Next Steps:** Build SQLite caching layer and first-run wizard
