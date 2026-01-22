# KLAR-SERVER-ENGINE (KSE) - MASTER IMPLEMENTATION PLAN
## Production-Grade Swedish Search Engine (Naver-Class)

**Version:** 1.0 Production  
**Date:** 2026-01-22  
**Repository:** https://github.com/CKCHDX/klar (branch: `sbdb`)  
**Deployment:** search.oscyra.solutions  
**Status:** 🟢 READY FOR IMPLEMENTATION

---

# EXECUTIVE SUMMARY

Klar-Server-Engine (KSE) is a **production-ready, Swedish-optimized search engine** designed to replace Google for Swedish users. It operates as:

- **🖥️ Server Application** (Windows/Linux executable) - Crawls, indexes, and serves search results
- **💻 Client Application** (Klar Browser executable) - Beautiful UI for user searches
- **🔐 Local-First Architecture** - No tracking, no profiling, complete user control

This is NOT a hobby project. This is **production-grade code for national deployment** in Swedish schools, government, and businesses.

---

# PART 1: ARCHITECTURAL DECISIONS (Made for You)

## 1.1 Technology Stack (Industry Grade - FINAL DECISIONS)

### Backend Server
```
Framework:       Flask 2.3.3 (lightweight, fast, scalable)
Database:        PostgreSQL 15 (enterprise ACID-compliant, full-text search)
Cache Layer:     Redis 7.0 (for frequent searches, session management)
Search Index:    In-memory inverted index + PostgreSQL JSONB
Task Queue:      Celery 5.3 (for background crawling, change detection)
Async Workers:   Gunicorn + gevent (production WSGI server)
```

**Why these choices?**
- ✅ PostgreSQL handles full-text Swedish tokenization natively
- ✅ Redis speeds up 99.9% of repeat searches (< 10ms cache hits)
- ✅ Celery crawls domains in background without blocking searches
- ✅ Gunicorn + gevent handles 1000+ concurrent clients
- ✅ All components are battle-tested at enterprise scale

### Client Application
```
Framework:       PyQt6 6.5.0 (modern, responsive, native feel)
Python Version:  3.10+ (async-compatible, type-hint support)
Communication:   HTTP/1.1 REST API + JSON
Packaging:       PyInstaller for single .exe distribution
```

## 1.2 Database Architecture (PostgreSQL - Enterprise Grade)

### PostgreSQL Schema

```sql
-- kse_config: System configuration
CREATE TABLE kse_config (
    id INT PRIMARY KEY,
    setup_date TIMESTAMP,
    initialized BOOLEAN,
    version TEXT,
    crawl_strategy TEXT,
    nlp_version TEXT
);

-- kse_domains: All 2,543 Swedish domains
CREATE TABLE kse_domains (
    domain_id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    category TEXT,  -- government, news, business, education, etc.
    trust_score REAL,  -- 0.0 to 1.0 (gov.se=0.99, blogs=0.60)
    region TEXT,  -- Swedish läns (Jönköpings läns, etc.)
    municipality TEXT,  -- Swedish kommun
    crawl_strategy TEXT,  -- full, shallow, smart
    last_crawl TIMESTAMP,
    next_scheduled_crawl TIMESTAMP,
    status TEXT,  -- active, paused, archived
    pages_count INT DEFAULT 0,
    change_detection_enabled BOOLEAN DEFAULT true
);
CREATE INDEX idx_domains_url ON kse_domains(url);
CREATE INDEX idx_domains_status ON kse_domains(status);
CREATE INDEX idx_domains_last_crawl ON kse_domains(last_crawl);

-- kse_pages: 2.8M+ indexed web pages
CREATE TABLE kse_pages (
    page_id BIGSERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    domain_id INT REFERENCES kse_domains(domain_id),
    title TEXT,
    raw_content TEXT,  -- Full HTML content
    extracted_text TEXT,  -- Plain text extracted from HTML
    tokens JSONB,  -- Pre-processed tokens from Swedish NLP
    metadata JSONB,  -- {author, date, region, language, etc.}
    content_hash TEXT,  -- SHA256 hash for change detection
    trust_score REAL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP,
    indexed BOOLEAN DEFAULT false
);
CREATE INDEX idx_pages_url ON kse_pages(url);
CREATE INDEX idx_pages_domain_id ON kse_pages(domain_id);
CREATE INDEX idx_pages_indexed ON kse_pages(indexed);
CREATE INDEX idx_pages_processed_at ON kse_pages(processed_at);

-- kse_index: Inverted index (word → pages)
CREATE TABLE kse_index (
    word_id SERIAL PRIMARY KEY,
    word TEXT UNIQUE NOT NULL,
    word_lemma TEXT,  -- Normalized form (restauranger → restaurang)
    page_ids BIGINT[],  -- Array of page IDs containing this word
    tf_score REAL,  -- Term frequency
    idf_score REAL,  -- Inverse document frequency
    frequency_count INT,  -- How many pages contain this word
    entity_type TEXT  -- NULL, person, place, date, organization
);
CREATE INDEX idx_index_word ON kse_index(word);
CREATE INDEX idx_index_lemma ON kse_index(word_lemma);
CREATE INDEX idx_index_entity_type ON kse_index(entity_type);

-- kse_search_log: Audit trail for searches
CREATE TABLE kse_search_log (
    search_id BIGSERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    query_intent TEXT,  -- factual_question, local_search, news_search, etc.
    results_count INT,
    response_time_ms INT,
    user_hash TEXT,  -- Anonymized user ID (no personal data)
    client_version TEXT,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    region TEXT  -- Geographic region if detectable
);
CREATE INDEX idx_search_log_query ON kse_search_log(query);
CREATE INDEX idx_search_log_timestamp ON kse_search_log(searched_at);

-- kse_crawl_log: Diagnostics and monitoring
CREATE TABLE kse_crawl_log (
    crawl_id BIGSERIAL PRIMARY KEY,
    domain_id INT REFERENCES kse_domains(domain_id),
    crawl_start TIMESTAMP,
    crawl_end TIMESTAMP,
    pages_found INT,
    pages_errors INT,
    pages_updated INT,
    status TEXT,  -- success, partial, failed
    error_message TEXT
);
CREATE INDEX idx_crawl_log_domain ON kse_crawl_log(domain_id);
CREATE INDEX idx_crawl_log_timestamp ON kse_crawl_log(crawl_start);
```

## 1.3 Swedish NLP Engine (Core Innovation)

Advanced Swedish language processing handles:

```python
class SwedishNLPEngine:
    """Production-grade Swedish NLP"""
    
    def process_query(self, query):
        """
        Transform query into search tokens + intent
        
        Example:
        Input:  "hur gammal är sverige statsminister?"
        Output: {
            "tokens": ["gammal", "sverige", "statsminister"],
            "intent": "factual_question",
            "entities": [("Sverige", "country"), ("statsminister", "position")],
            "query_type": "how_old",
            "confidence": 0.94
        }
        """
        pass
    
    def lemmatize(self, tokens):
        """Swedish word normalization
        restauranger → restaurang
        hus → hus
        badrum → bad + rum (compound)
        """
        pass
    
    def extract_entities(self, tokens):
        """Extract named entities
        ("Stockholm", "city")
        ("Eva Johansson", "person")
        ("2026-01-22", "date")
        """
        pass
    
    def detect_intent(self, query):
        """Detect query intent
        factual_question: "hur gammal är..."
        local_search: "restauranger i stockholm"
        news_search: "senaste nytt", "vad hände"
        definition: "vad är", "vad betyder"
        calculation: "1+1", "omvandla"
        """
        pass
```

### Key Swedish NLP Features

1. **Compound Word Handling**
   - badrum → bad (bath) + rum (room)
   - restaurang → Unique, not compound
   - Stockholm → Unique place name

2. **Smart Lemmatization**
   - restauranger → restaurang
   - hus → hus
   - huset → hus

3. **Swedish Stopword Removal** (65 common words)
   - Remove: och, de, som, här, där, i, på, av
   - Keep: restaurang, stockholm, statsminister

4. **Entity Extraction**
   - People: Eva Johansson, Magdalena Andersson
   - Places: Stockholm, Göteborg, Jönköping
   - Dates: 2026-01-22, nästa vecka
   - Organizations: Sveriges riksbank, Stockholm stad

5. **Intent Detection**
   - "vad är 1+1?" → calculation
   - "hur gammal är statsminister?" → factual_question
   - "senaste nytt i jönköping" → news + location
   - "restauranger stockholm" → local_search

## 1.4 Search Algorithm (Naver-Level Quality)

### Multi-Factor Ranking

```
FINAL_SCORE = (
    (TF-IDF_SCORE × 0.35) +           # Word relevance
    (PAGERANK_SCORE × 0.20) +          # Authority/links
    (DOMAIN_TRUST × 0.15) +            # Domain reputation
    (RECENCY_SCORE × 0.10) +           # Page age (recent = higher)
    (REGION_RELEVANCE × 0.10) +        # Geographic match
    (ENTITY_MATCH × 0.10)              # Named entity matches
) × QUALITY_MULTIPLIER
```

### Ranking Factors

1. **TF-IDF (35%)**
   - How relevant is this page to the query?
   - Weight: term frequency × inverse document frequency

2. **PageRank (20%)**
   - How authoritative is this page?
   - Based on incoming links from other trusted pages

3. **Domain Trust (15%)**
   - gov.se → 0.99 (highest trust)
   - news sites → 0.95
   - educational → 0.90
   - blogs → 0.60

4. **Recency (10%)**
   - Recent news ranked higher for timely queries
   - Old archived pages ranked lower

5. **Region Relevance (10%)**
   - User searching "Stockholm" → Stockholm results boosted
   - User searching "Jönköping" → Jönköping results boosted

6. **Entity Match (10%)**
   - Query mentions "Eva Johansson" → pages about Eva ranked higher
   - Query mentions "Stockholm" → Stockholm pages ranked higher

## 1.5 Change Detection (Automatic Updates)

```
CHANGE DETECTION CYCLE (Every 24 hours):

1. Hash all 2,543 domains
2. Compare with previous hash
3. Identify 0.5% that changed
4. Add changed domains to recrawl queue
5. Recrawl ONLY those domains (background thread)
6. Update index incrementally
7. Continue serving searches (ZERO DOWNTIME)

Efficiency:
- 99.5% of domains = no recrawl (save bandwidth)
- 0.5% changed = selective recrawl only
- Result: ~70% bandwidth savings vs daily full crawl
```

---

# PART 2: THREE-PHASE ARCHITECTURE

## Phase 1: Setup Wizard (One-Time, ~8 hours)

```
python run_v3.py
  ↓
PHASE 1 Opens Setup Wizard with 5 steps:

[Step 1/5: Initialize Database]
  • Create ./kse_sbdb_data/ directory
  • Initialize PostgreSQL schema
  • Load configuration templates

[Step 2/5: Discover Domains]
  • Load 2,543 hardcoded Swedish .se domains
  • Categorize by type (government, news, business, etc.)
  • Sort by trust score

[Step 3/5: Domain Curation]
  • USER SELECTS which domains to crawl
  • Can filter by category, trust score
  • Can select specific domains or all
  • Example: Select only gov.se + news sites (100% trust)
  • Example: Select all 2,543 domains (comprehensive)

[Step 4/5: Configure Crawl Settings]
  • Crawl depth: Full vs Shallow vs Smart
  • Change detection: Enabled/Disabled
  • Recrawl frequency: 24h, 7d, 30d, manual
  • Content extraction: Full text vs headers only
  • Swedish NLP: Apply lemmatization? Yes/No

[Step 5/5: Initial Crawl & Index]
  • Start crawling selected domains
  • Progress bar: 0% → 100% (6-8 hours)
  • Real-time stats: pages crawled, bandwidth used, speed
  • When complete: Database ready, move to Phase 2

Database after Phase 1:
  • 2,843,000+ pages indexed
  • 1,247,833 unique Swedish words
  • 4.2 GB PostgreSQL database
  • All pages tokenized and lemmatized
  • Inverted index built and ready
```

## Phase 2: Control Center (Server Management)

```
PHASE 2: Control Center with 3 buttons

┌─────────────────────────────────────┐
│ Klar-Server-Engine Control Center    │
│                                     │
│ Database: PostgreSQL ✓ Connected    │
│ Status: Ready (Not Running)         │
│ Index Size: 4.2 GB                  │
│ Pages: 2,843,000                    │
│                                     │
│  ┌────────────────────────────────┐ │
│  │ [▶ START SERVER]                │ │
│  │ Bind to 127.0.0.1:8080          │ │
│  └────────────────────────────────┘ │
│                                     │
│  ┌────────────────────────────────┐ │
│  │ [🔄 RE-INITIALIZE SETUP]        │ │
│  │ Return to Phase 1               │ │
│  └────────────────────────────────┘ │
│                                     │
│  ┌────────────────────────────────┐ │
│  │ [🔍 SCAN FOR CORRUPTION]        │ │
│  │ Run diagnostic checks           │ │
│  └────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘

What each button does:

[START SERVER]
  → Flask server starts on http://127.0.0.1:8080
  → Database loads into memory
  → Gunicorn workers spawn (4 workers for 4 CPU cores)
  → Change detection monitor starts (background thread)
  → API endpoints ready for client requests
  → Move to Phase 3

[RE-INITIALIZE SETUP]
  → Return to Phase 1 Setup Wizard
  → Let user change domain selection
  → Recrawl with new settings
  → Rebuild index

[SCAN FOR CORRUPTION]
  → Check database integrity
  → Verify all pages referenced in index exist
  → Detect orphaned entries
  → Test search performance
  → Report: HEALTHY, WARNINGS, or CORRUPTED
```

## Phase 3: Runtime Dashboard (Live Monitoring)

```
PHASE 3: Runtime Dashboard - Server Active

┌─────────────────────────────────────────────────┐
│ Klar-Server-Engine - ACTIVE ● 2d 14h 32m 47s    │
├─────────────────────────────────────────────────┤
│                                                 │
│ ⏱️  PERFORMANCE                                  │
│ • Uptime: 2 days 14 hours 32 minutes 47 sec    │
│ • Avg Search Speed: 0.347 seconds (target <0.5s)│
│ • P50: 0.12s (50% faster), P95: 1.23s         │
│ • Queries Served Today: 47,293                 │
│ • Active Connections: 34 clients               │
│ • Peak Today: 156 concurrent                   │
│                                                 │
│ 📊 INDEX STATISTICS                             │
│ • Total Domains: 2,543 (all Swedish .se)       │
│ • Selected Domains: 2,543 (100% crawled)       │
│ • Indexed Pages: 2,843,000                     │
│ • Unique Keywords: 1,247,833                   │
│ • Index Size: 4.2 GB                           │
│ • Last Reindex: 2d 6h ago (full rebuild)       │
│ • Last Update: 3h 12m ago (incremental crawl)  │
│                                                 │
│ 🧠 ALGORITHM STATUS                             │
│ • Ranking: TF-IDF + PageRank + Trust + Region  │
│ • Swedish NLP: Active (lemmatization enabled)  │
│ • Entity Extraction: Enabled (people/places)   │
│ • Intent Detection: Active                     │
│ • Change Detection: Monitoring 2,543 domains   │
│                                                 │
│ 🔄 CRAWL MONITOR                                │
│ • Last Change Detection: 3h ago                │
│ • Domains Changed: 5                           │
│ • Currently Recrawling: dn.se, sverigesradio.se│
│ • Recrawl Success Rate: 99.2%                  │
│ • Errors This Month: 12                        │
│                                                 │
│ [⏹ STOP] [⚙️ SETTINGS] [📋 LOGS] [🔧 DIAG]    │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

# PART 3: API SPECIFICATION

## POST /api/search
**Client searches for something**

```json
Request:
{
  "query": "restauranger stockholm",
  "limit": 10,
  "offset": 0
}

Response (200 OK):
{
  "success": true,
  "query": "restauranger stockholm",
  "query_intent": "local_search",
  "results": [
    {
      "rank": 1,
      "title": "Bästa restaurangerna i Stockholm",
      "url": "https://sverigesradio.se/artikel/stockholm-restauranger",
      "snippet": "Upptäck de mest populära restaurangerna i Stockholm...",
      "score": 0.905,
      "domain": "sverigesradio.se",
      "trust_score": 0.95,
      "region": "Stockholm",
      "date_published": "2026-01-20",
      "source_category": "news"
    }
  ],
  "total_results": 2847,
  "response_time_ms": 347,
  "timestamp": "2026-01-22T15:30:45Z"
}
```

## GET /api/status
**Check server status**

```json
Response:
{
  "status": "active",
  "uptime_seconds": 86400,
  "database": "postgresql",
  "database_size_mb": 4200,
  "pages_indexed": 2843000,
  "queries_served_today": 47293,
  "avg_search_time_ms": 347,
  "active_connections": 34
}
```

## GET /api/stats
**Get detailed statistics**

```json
Response:
{
  "domains_total": 2543,
  "domains_indexed": 2543,
  "pages_total": 2843000,
  "unique_keywords": 1247833,
  "index_size_mb": 4200,
  "last_full_crawl": "2026-01-22T10:00:00Z",
  "last_change_detection": "2026-01-22T14:30:00Z",
  "domains_changed_recently": 5,
  "crawl_success_rate": 0.992,
  "swedish_nlp_version": "Swedish-Advanced-v2"
}
```

---

# PART 4: PRODUCTION QUALITY STANDARDS

## Code Quality (NO COMPROMISES)

```
✅ COMPLETENESS
  • Every function fully implemented (no TODOs)
  • Every function has docstring + type hints
  • Every class has __init__, __repr__, __str__
  • Error handling for all external calls

✅ SECURITY
  • Input validation on all endpoints
  • SQL injection prevention (parameterized queries)
  • XSS prevention (HTML escaping)
  • Rate limiting on API (100 req/min per client)
  • CORS headers properly configured

✅ PERFORMANCE
  • Search < 500ms for 99% of queries (target)
  • Database queries indexed
  • Redis cache for top 10,000 queries
  • Lazy loading for large datasets
  • Connection pooling (PostgreSQL)

✅ RELIABILITY
  • Zero crashes in 72-hour load test
  • Graceful degradation if Redis down
  • Automatic reconnection to PostgreSQL
  • Transaction logging
  • Backup/restore procedures

✅ MONITORING
  • Detailed logging (search, crawler, errors)
  • Corruption detection on startup
  • Performance metrics dashboard
  • Health checks every 60 seconds
  • Alert system for critical issues
```

## Testing Requirements

```
Unit Tests (95%+ coverage):
  • test_nlp.py - Swedish NLP engine
  • test_crawler.py - Web crawler
  • test_search.py - Search algorithm
  • test_index.py - Index operations
  • test_database.py - PostgreSQL operations
  • test_api.py - API endpoints
  • test_gui.py - GUI components

Integration Tests:
  • Full search flow: query → result
  • Database: insert → retrieve
  • API: request → response
  • Client-server communication

Performance Tests:
  • Search speed benchmark (< 500ms)
  • Concurrent clients test (1000+)
  • Memory profiling
  • Database load test (10M+ queries)

Security Tests:
  • SQL injection attempts
  • XSS payload testing
  • Rate limiting verification
  • Input validation tests
```

---

# PART 5: FILE STRUCTURE

```
klar/ (GitHub repo - branch: sbdb)
│
├── run_v3.py                    ← MAIN ENTRY POINT
│   ├─ Phase 1: Setup Wizard GUI
│   ├─ Phase 2: Control Center GUI
│   ├─ Phase 3: Runtime Dashboard
│   └─ Server startup/shutdown
│
├── kse_server.py                ← Flask Backend
│   ├─ Flask app + endpoints
│   ├─ Request/response handling
│   └─ Error handling
│
├── kse_nlp.py                   ← Swedish NLP
│   ├─ Tokenization
│   ├─ Lemmatization
│   ├─ Entity extraction
│   └─ Intent detection
│
├── kse_crawler.py               ← Web Crawler
│   ├─ HTML parsing
│   ├─ Change detection
│   └─ Progress tracking
│
├── kse_index.py                 ← Index Management
│   ├─ Inverted index building
│   ├─ Search operations
│   └─ Index maintenance
│
├── kse_search.py                ← Search Algorithm
│   ├─ Query processing
│   ├─ Ranking algorithm
│   └─ Result formatting
│
├── kse_database.py              ← Database Layer
│   ├─ PostgreSQL connection
│   ├─ Query builder
│   ├─ Transactions
│   └─ Migrations
│
├── kse_gui.py                   ← PyQt6 GUI
│   ├─ Phase 1 widgets
│   ├─ Phase 2 widgets
│   └─ Phase 3 widgets
│
├── klar_browser_client.py       ← Client App
│   ├─ Server connection
│   ├─ Search UI
│   └─ Results display
│
├── config/
│   ├── swedish_domains.json     (2,543 .se domains)
│   ├── swedish_stopwords.txt
│   └── config_template.json
│
├── database/
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_indexes.sql
│   │   └── 003_materialized_views.sql
│   └── backup/
│
├── tests/
│   ├── test_nlp.py
│   ├── test_crawler.py
│   ├── test_search.py
│   ├── test_api.py
│   ├── test_database.py
│   └── conftest.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── SETUP.md
│   ├── DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
│
├── requirements.txt
├── README.md
├── LICENSE (AGPL v3)
└── .gitignore
```

---

# PART 6: DEPLOYMENT CHECKLIST

## Pre-Launch (This Week)

```
Database:
  □ PostgreSQL schema created (001-003 migrations)
  □ Indexes created for fast queries
  □ Full-text search working in Swedish
  □ Backup/restore procedures tested
  □ Connection pooling configured

Backend:
  □ Flask server runs on 127.0.0.1:8080
  □ All API endpoints implemented
  □ Error handling for all cases
  □ Logging configured (search, crawler, errors)
  □ Security: input validation, rate limiting, CORS

NLP & Search:
  □ Swedish tokenization working
  □ Lemmatization correct
  □ Entity extraction functional
  □ Intent detection accurate
  □ Search algorithm ranking correctly

Crawler:
  □ Crawls 2,543 domains successfully
  □ Change detection working
  □ Recrawl logic functional
  □ Error recovery implemented
  □ Progress tracking visible

Client:
  □ Connects to server (127.0.0.1:8080)
  □ Search UI responsive
  □ Results display correctly
  □ No backend URLs exposed
  □ Works on Windows 10/11 + Linux

Testing:
  □ 95%+ code coverage
  □ All unit tests passing
  □ Integration tests pass
  □ Performance tests pass (< 500ms)
  □ Security tests pass

Documentation:
  □ README complete
  □ Architecture documented
  □ API documented
  □ Setup guide written
  □ Troubleshooting guide ready

Production:
  □ Code reviewed
  □ Security audit passed
  □ 72-hour stability test passed
  □ Exe compiled (PyInstaller)
  □ Ready for deployment
```

---

# SUCCESS CRITERIA FOR LAUNCH

```
✅ FUNCTIONAL
  □ Search returns results in < 500ms
  □ All 2,543 domains indexed
  □ Swedish NLP working perfectly
  □ Change detection automatic
  □ Client-server communication stable

✅ QUALITY
  □ 95%+ test coverage
  □ Zero crashes in 72h load test
  □ Zero data corruption
  □ 99%+ uptime

✅ PRODUCTION
  □ Code review complete
  □ Security audit passed
  □ Documentation complete
  □ Admin guide for national deployment

✅ USER EXPERIENCE
  □ Search results better than Google (Swedish users)
  □ Works for 10-100 year-olds
  □ Natural language queries supported
  □ Zero technical backend exposure
```

---

**STATUS:** 🟢 READY FOR IMPLEMENTATION  
**NEXT STEP:** Begin production code development (Part 7 in next document)
