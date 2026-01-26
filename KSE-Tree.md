# 🚀 KSE PROJECT TREE - SIMPLIFIED SERVER-SIDE FOCUSED (LOCAL STORAGE)

**Date Created:** January 25, 2026  
**Focus:** Server-side development with full PyQt6 GUI  
**Storage:** Local file-based (no PostgreSQL)  
**Target Phases:** 1-4 (Setup → Control Center)  

---

## 📁 COMPLETE SIMPLIFIED PROJECT STRUCTURE

```
kse/
│
├─ 📄 README.md                              [Project overview & quick start]
├─ 📄 LICENSE                                [MIT License]
├─ 📄 requirements.txt                       [Python dependencies]
├─ 📄 .gitignore                             [Git ignore rules]
├─ 📄 setup.py                               [Package installation]
│
│
├─ 🗂️  kse/                                   [CORE KSE ENGINE]
│   │
│   ├─ 🗂️  core/                             [Core engine modules]
│   │   ├─ __init__.py
│   │   ├─ kse_main.py                       [Entry point - Main application]
│   │   ├─ kse_config.py                     [Global configuration management]
│   │   ├─ kse_logger.py                     [Enterprise logging system]
│   │   ├─ kse_exceptions.py                 [Custom exception types]
│   │   ├─ kse_constants.py                  [Global constants & enums]
│   │   └─ kse_singleton.py                  [Singleton pattern for shared resources]
│   │
│   ├─ 🗂️  storage/                          [Local file-based storage layer]
│   │   ├─ __init__.py
│   │   ├─ kse_storage_manager.py            [File I/O orchestration]
│   │   ├─ kse_domain_manager.py             [Domain list management]
│   │   ├─ kse_index_storage.py              [Index save/load operations]
│   │   ├─ kse_cache_storage.py              [Cache file operations]
│   │   ├─ kse_data_serializer.py            [JSON/pickle serialization]
│   │   ├─ kse_backup_manager.py             [Backup & restore operations]
│   │   ├─ kse_storage_optimizer.py          [Storage optimization & cleanup]
│   │   └─ kse_storage_monitor.py            [Monitor storage usage]
│   │
│   ├─ 🗂️  crawler/                          [Web crawling engine]
│   │   ├─ __init__.py
│   │   ├─ kse_crawler_core.py               [Main crawler orchestrator]
│   │   ├─ kse_url_processor.py              [URL normalization & dedup]
│   │   ├─ kse_url_queue.py                  [Smart URL queue management]
│   │   ├─ kse_http_client.py                [HTTP requests with retry logic]
│   │   ├─ kse_html_extractor.py             [HTML parsing & content extraction]
│   │   ├─ kse_robots_parser.py              [robots.txt compliance]
│   │   ├─ kse_link_extractor.py             [Link discovery & validation]
│   │   ├─ kse_pagination_handler.py         [Pagination detection & navigation]
│   │   ├─ kse_change_detection.py           [Hash-based change detection]
│   │   ├─ kse_crawler_scheduler.py          [Crawl scheduling & recrawl]
│   │   ├─ kse_crawler_stats.py              [Crawling statistics]
│   │   └─ kse_crawler_resilience.py         [Error recovery & retry logic]
│   │
│   ├─ 🗂️  nlp/                              [Swedish Natural Language Processing]
│   │   ├─ __init__.py
│   │   ├─ kse_nlp_core.py                   [Main NLP coordinator]
│   │   ├─ kse_tokenizer.py                  [Swedish tokenization & normalization]
│   │   ├─ kse_lemmatizer.py                 [Swedish lemmatization engine]
│   │   ├─ kse_compound_handler.py           [Swedish compound word handler]
│   │   ├─ kse_stopwords.py                  [Swedish stopword management]
│   │   ├─ kse_entity_extractor.py           [Named entity recognition (NER)]
│   │   ├─ kse_intent_detector.py            [Query intent classification]
│   │   ├─ kse_query_expander.py             [Query expansion & synonyms]
│   │   ├─ kse_sentiment_analyzer.py         [Sentiment analysis]
│   │   └─ kse_language_detector.py          [Language detection]
│   │
│   ├─ 🗂️  indexing/                         [Indexing pipeline]
│   │   ├─ __init__.py
│   │   ├─ kse_indexer_pipeline.py           [Main indexing orchestrator]
│   │   ├─ kse_inverted_index.py             [Inverted index structure]
│   │   ├─ kse_tf_idf_calculator.py          [TF-IDF computation]
│   │   ├─ kse_page_processor.py             [Page parsing & prep]
│   │   ├─ kse_metadata_extractor.py         [Metadata extraction]
│   │   ├─ kse_index_builder.py              [Index building & optimization]
│   │   ├─ kse_index_statistics.py           [Index statistics]
│   │   └─ kse_incremental_indexing.py       [Incremental update logic]
│   │
│   ├─ 🗂️  ranking/                          [Search ranking engine]
│   │   ├─ __init__.py
│   │   ├─ kse_ranking_core.py               [Main ranking orchestrator]
│   │   ├─ kse_tf_idf_ranker.py              [Factor 1: TF-IDF scoring]
│   │   ├─ kse_pagerank.py                   [Factor 2: PageRank algorithm]
│   │   ├─ kse_domain_authority.py           [Factor 3: Domain trust scoring]
│   │   ├─ kse_recency_scorer.py             [Factor 4: Content recency]
│   │   ├─ kse_keyword_density.py            [Factor 5: Keyword density]
│   │   ├─ kse_link_structure.py             [Factor 6: Link structure analysis]
│   │   ├─ kse_regional_relevance.py         [Factor 7: Regional relevance]
│   │   ├─ kse_personalization.py            [User signal personalization]
│   │   ├─ kse_diversity_ranker.py           [Result diversity algorithm]
│   │   └─ kse_ranking_stats.py              [Ranking statistics & diagnostics]
│   │
│   ├─ 🗂️  search/                           [Search engine]
│   │   ├─ __init__.py
│   │   ├─ kse_search_pipeline.py            [Main search orchestrator]
│   │   ├─ kse_query_preprocessor.py         [Query preprocessing]
│   │   ├─ kse_search_executor.py            [Search execution]
│   │   ├─ kse_result_processor.py           [Result processing & formatting]
│   │   ├─ kse_search_cache.py               [In-memory cache layer]
│   │   ├─ kse_search_history.py             [Search history logging]
│   │   ├─ kse_search_analytics.py           [Search analytics]
│   │   ├─ kse_spell_checker.py              [Swedish spell checking]
│   │   └─ kse_autocomplete.py               [Search autocomplete]
│   │
│   ├─ 🗂️  server/                           [Flask REST API server]
│   │   ├─ __init__.py
│   │   ├─ kse_server.py                     [Main Flask application]
│   │   ├─ kse_server_config.py              [Server configuration]
│   │   ├─ kse_server_middleware.py          [Middleware & decorators]
│   │   ├─ kse_server_security.py            [Security (auth, rate-limit, CORS)]
│   │   ├─ kse_routes_search.py              [Search API endpoints]
│   │   ├─ kse_routes_admin.py               [Admin API endpoints]
│   │   ├─ kse_routes_health.py              [Health check endpoints]
│   │   ├─ kse_routes_stats.py               [Statistics API endpoints]
│   │   ├─ kse_request_validator.py          [Request validation]
│   │   ├─ kse_response_formatter.py         [Response formatting]
│   │   ├─ kse_error_handler.py              [Error handling middleware]
│   │   └─ kse_api_documentation.py          [API docs (Swagger)]
│   │
│   ├─ 🗂️  monitoring/                       [System monitoring]
│   │   ├─ __init__.py
│   │   ├─ kse_monitoring_core.py            [Main monitoring system]
│   │   ├─ kse_health_checker.py             [System health checks]
│   │   ├─ kse_metrics_collector.py          [Metrics collection]
│   │   ├─ kse_performance_profiler.py       [Performance profiling]
│   │   ├─ kse_alerts.py                     [Alert system]
│   │   ├─ kse_audit_logger.py               [Audit trail logging]
│   │   └─ kse_diagnostics.py                [System diagnostics]
│   │
│   ├─ 🗂️  cache/                            [In-memory caching layer]
│   │   ├─ __init__.py
│   │   ├─ kse_cache_manager.py              [Cache orchestration]
│   │   ├─ kse_memory_cache.py               [In-memory cache]
│   │   ├─ kse_cache_policy.py               [Cache eviction policies]
│   │   └─ kse_cache_stats.py                [Cache statistics]
│   │
│   └─ 🗂️  utils/                            [Utility functions]
│       ├─ __init__.py
│       ├─ kse_string_utils.py               [String utilities]
│       ├─ kse_date_utils.py                 [Date/time utilities]
│       ├─ kse_file_utils.py                 [File handling]
│       ├─ kse_network_utils.py              [Network utilities]
│       ├─ kse_hash_utils.py                 [Hashing & checksums]
│       └─ kse_encoding_utils.py             [Encoding utilities]
│
│
├─ 🗂️  gui/                                  [PyQt6 GUI application (SERVER-SIDE)]
│   │
│   ├─ __init__.py
│   ├─ kse_gui_main.py                       [Main GUI entry point]
│   ├─ kse_gui_config.py                     [GUI configuration & styling]
│   ├─ kse_gui_dark_theme.py                 [Dark theme stylesheet]
│   ├─ kse_gui_styles.py                     [Reusable GUI styles]
│   │
│   ├─ 🗂️  setup_wizard/                     [Phase 1-3: Interactive Setup Wizard]
│   │   ├─ __init__.py
│   │   ├─ setup_wizard_main.py              [Wizard main window orchestrator]
│   │   ├─ phase_1_storage_config.py         [Phase 1: Storage path & domain selection]
│   │   ├─ phase_2_crawl_control.py          [Phase 2: Crawl control & progress]
│   │   ├─ phase_3_server_bootstrap.py       [Phase 3: Server bootstrap & verification]
│   │   ├─ wizard_progress_widget.py         [Progress bar & status display]
│   │   ├─ wizard_log_viewer.py              [Live log viewer with scrolling]
│   │   └─ wizard_validation.py              [Form validation]
│   │
│   ├─ 🗂️  control_center/                   [Phase 4: Control Center (5 operational modules)]
│   │   ├─ __init__.py
│   │   ├─ control_center_main.py            [Control center main window]
│   │   ├─ control_center_config.py          [CC configuration & theme]
│   │   ├─ control_center_navigation.py      [Tab/module navigation]
│   │   ├─ control_center_api_client.py      [Flask API client for live data]
│   │   │
│   │   ├─ 🗂️  modules/
│   │   │   ├─ __init__.py
│   │   │   │
│   │   │   ├─ pcc_primary_control.py        [PRIMARY CONTROL CENTER]
│   │   │   │   ├─ System overview dashboard
│   │   │   │   ├─ Status tiles (CPU, RAM, Disk, Index)
│   │   │   │   ├─ Event timeline (last 50 events)
│   │   │   │   └─ Quick action buttons
│   │   │   │
│   │   │   ├─ mcs_main_control_server.py    [MAIN CONTROL SERVER]
│   │   │   │   ├─ Server start/stop/restart controls
│   │   │   │   ├─ Live performance metrics (QPS, latency)
│   │   │   │   ├─ Port configuration
│   │   │   │   ├─ Runtime parameter adjustment
│   │   │   │   └─ Index snapshot management
│   │   │   │
│   │   │   ├─ scs_system_status.py          [SYSTEM CONTROL STATUS]
│   │   │   │   ├─ Real-time component health
│   │   │   │   ├─ Metrics dashboard
│   │   │   │   ├─ Storage statistics
│   │   │   │   ├─ Index status & size
│   │   │   │   └─ Alert/warning display
│   │   │   │
│   │   │   ├─ acc_auxiliary_control.py      [AUXILIARY CONTROL CENTER]
│   │   │   │   ├─ Index rebuild button
│   │   │   │   ├─ Data cleanup & optimization
│   │   │   │   ├─ Consistency checker
│   │   │   │   ├─ Log rotation
│   │   │   │   ├─ Snapshot management UI
│   │   │   │   └─ Diagnostics tool
│   │   │   │
│   │   │   └─ scc_secondary_control.py      [SECONDARY CONTROL CENTER]
│   │   │       ├─ Search analytics & graphs
│   │   │       ├─ Crawler analytics
│   │   │       ├─ Query trending/trending tab
│   │   │       ├─ Domain statistics table
│   │   │       ├─ Experiment controls
│   │   │       └─ Per-domain statistics view
│   │   │
│   │   ├─ 🗂️  widgets/                     [Reusable PyQt6 widgets]
│   │   │   ├─ __init__.py
│   │   │   ├─ status_tile.py               [Status display tile widget]
│   │   │   ├─ chart_widget.py              [Live charts (line, bar, pie)]
│   │   │   ├─ gauge_widget.py              [Circular gauge display]
│   │   │   ├─ metric_card.py               [Metric display card]
│   │   │   ├─ log_viewer.py                [Scrollable log viewer]
│   │   │   ├─ table_widget.py              [Enhanced sortable table]
│   │   │   ├─ timeline_widget.py           [Event timeline display]
│   │   │   ├─ progress_widget.py           [Progress bar indicator]
│   │   │   ├─ notification_widget.py       [Alert/notification display]
│   │   │   └─ status_indicator.py          [Live status indicator (green/yellow/red)]
│   │   │
│   │   └─ 🗂️  dialogs/                     [Dialog windows]
│   │       ├─ __init__.py
│   │       ├─ domain_selection_dialog.py   [Multi-select domain picker]
│   │       ├─ settings_dialog.py           [Settings/preferences window]
│   │       ├─ export_dialog.py             [Data export dialog]
│   │       ├─ import_dialog.py             [Data import dialog]
│   │       ├─ confirmation_dialog.py       [Confirmation prompts]
│   │       ├─ about_dialog.py              [About/help dialog]
│   │       └─ error_dialog.py              [Error display dialog]
│   │
│   └─ 🗂️  components/                      [GUI components]
│       ├─ __init__.py
│       ├─ menubar.py                       [Application menu bar]
│       ├─ statusbar.py                     [Status bar with live updates]
│       ├─ toolbar.py                       [Toolbar with quick actions]
│       └─ sidebar.py                       [Navigation sidebar]
│
│
├─ 🗂️  config/                              [Configuration files (editable by users)]
│   ├─ swedish_domains.json                 [All 2,543 Swedish domains list]
│   ├─ domain_categories.json               [Domain categorization]
│   ├─ trust_scores.json                    [Domain trust scores]
│   ├─ kse_default_config.yaml              [Default application configuration]
│   ├─ swedish_stopwords.txt                [Swedish stopwords]
│   └─ regex_patterns.json                  [Regex patterns for parsing]
│
│
├─ 🗂️  data/                                [Runtime data storage (auto-generated)]
│   ├─ 🗂️  storage/
│   │   ├─ 🗂️  index/
│   │   │   ├─ inverted_index.pkl           [Main inverted index (binary)]
│   │   │   ├─ metadata_index.pkl           [Page metadata index]
│   │   │   ├─ url_index.pkl                [URL deduplication index]
│   │   │   ├─ domain_index.pkl             [Domain-specific index]
│   │   │   ├─ tfidf_cache.pkl              [TF-IDF cache]
│   │   │   ├─ pagerank_cache.pkl           [PageRank cache]
│   │   │   └─ index_metadata.json          [Index statistics & timestamps]
│   │   │
│   │   ├─ 🗂️  cache/
│   │   │   ├─ search_cache.pkl             [Search result cache]
│   │   │   ├─ query_cache.pkl              [Preprocessed queries]
│   │   │   └─ cache_manifest.json          [Cache metadata]
│   │   │
│   │   ├─ 🗂️  crawl_state/
│   │   │   ├─ domain_status.json           [Per-domain crawl status]
│   │   │   ├─ url_queue.pkl                [Pending URLs queue]
│   │   │   ├─ visited_urls.pkl             [Visited URL set]
│   │   │   └─ crawl_state.json             [Global crawl state]
│   │   │
│   │   └─ 🗂️  snapshots/
│   │       ├─ index_snapshot_[timestamp].pkl  [Index snapshots]
│   │       └─ snapshot_manifest.json          [Snapshot metadata]
│   │
│   ├─ 🗂️  logs/
│   │   ├─ kse.log                          [Main application log]
│   │   ├─ crawler.log                      [Crawler operations log]
│   │   ├─ indexer.log                      [Indexing operations log]
│   │   ├─ search.log                       [Search queries log]
│   │   ├─ server.log                       [Server operations log]
│   │   ├─ errors.log                       [Error log]
│   │   └─ audit.log                        [Audit trail (admin actions)]
│   │
│   └─ 🗂️  exports/
│       └─ [User exports - CSV, JSON reports]
│
│
├─ 🗂️  scripts/                             [Standalone utility scripts]
│   ├─ init_kse.py                          [Initialize KSE local instance]
│   ├─ populate_domains.py                  [Populate domain list from JSON]
│   ├─ start_gui.py                         [Start GUI application]
│   ├─ start_server.py                      [Start Flask server (headless)]
│   ├─ start_crawler.py                     [Start crawler in background]
│   ├─ backup_data.py                       [Backup all local data]
│   ├─ restore_data.py                      [Restore from backup]
│   ├─ rebuild_index.py                     [Rebuild entire index]
│   ├─ export_statistics.py                 [Export statistics report]
│   ├─ health_check.py                      [Check system health]
│   ├─ performance_test.py                  [Test performance]
│   └─ cleanup_cache.py                     [Clean old cache files]
│
│
└─ 🗂️  assets/                              [GUI assets & resources]
    ├─ 🗂️  icons/
    │   ├─ app_icon.ico                     [Application icon]
    │   ├─ kse_logo.png                     [KSE logo]
    │   ├─ favicon.ico                      [Favicon]
    │   ├─ status_green.png                 [Status indicator - OK]
    │   ├─ status_yellow.png                [Status indicator - Warning]
    │   ├─ status_red.png                   [Status indicator - Error]
    │   ├─ play.png                         [Play button icon]
    │   ├─ stop.png                         [Stop button icon]
    │   ├─ refresh.png                      [Refresh icon]
    │   ├─ settings.png                     [Settings icon]
    │   ├─ export.png                       [Export icon]
    │   ├─ import.png                       [Import icon]
    │   └─ help.png                         [Help icon]
    │
    ├─ 🗂️  themes/
    │   ├─ dark.qss                         [Dark theme stylesheet]
    │   ├─ light.qss                        [Light theme stylesheet]
    │   └─ theme_config.json                [Theme configuration]
    │
    ├─ 🗂️  fonts/
    │   ├─ Segoe-UI-Regular.ttf              [Regular font]
    │   └─ Courier-New.ttf                  [Monospace font]
    │
    └─ 🗂️  images/
        ├─ splash_screen.png                [Splash screen on startup]
        ├─ welcome_banner.png               [Welcome image]
        └─ tutorial_images/                 [Tutorial screenshots]

```

---

## 🎯 KEY CHANGES FROM ORIGINAL STRUCTURE

### ✅ REMOVED (Not needed for server-side MVP)
- ❌ `/tests` - Tests will be added gradually
- ❌ `/docs` - Documentation will be created separately
- ❌ `/docker` - Docker support deferred
- ❌ `/ci_cd` - GitHub workflows deferred
- ❌ `/benchmarks` - Performance benchmarks deferred
- ❌ `/build` - Build artifacts deferred (created at end)
- ❌ `/dist` - Distribution deferred
- ❌ Database migrations folder (using local storage)
- ❌ `pyproject.toml`, `tox.ini`, `mypy.ini`, `pylintrc`, `black.toml`

### ✅ MODIFIED (Adapted for local storage)
- **`kse/core/database/`** → **`kse/storage/`** (file-based, not SQL)
  - Removed: `kse_database_connection.py`, `kse_database_schema.py`, `kse_database_migrations.py`
  - Added: `kse_storage_manager.py`, `kse_data_serializer.py`, `kse_storage_optimizer.py`

- **`kse/server/`** - No Redis needed
  - Removed: `kse_redis_client.py`
  - Added: In-memory cache via `kse/cache/`

- **`kse/cache/`** - In-memory only
  - Removed: Redis configuration
  - Added: Simple memory-based cache with eviction policies

### ✅ KEPT (Essential for MVP)
- ✅ `kse/core/` - Core engine
- ✅ `kse/crawler/` - Crawling engine
- ✅ `kse/nlp/` - Swedish NLP
- ✅ `kse/indexing/` - Indexing pipeline
- ✅ `kse/ranking/` - Ranking engine
- ✅ `kse/search/` - Search pipeline
- ✅ `kse/server/` - Flask API (for GUI communication)
- ✅ `kse/monitoring/` - Monitoring & metrics
- ✅ `gui/` - Full PyQt6 GUI (Setup Wizard + Control Center)
- ✅ `config/` - Configuration files
- ✅ `data/` - Runtime data storage
- ✅ `scripts/` - Utility scripts
- ✅ `assets/` - GUI assets & icons

---

## 📊 FILE COUNT ESTIMATE

**By component:**

```
kse/core/              ~7 files
kse/storage/           ~8 files (was database)
kse/crawler/           ~13 files
kse/nlp/               ~10 files
kse/indexing/          ~9 files
kse/ranking/           ~11 files
kse/search/            ~9 files
kse/server/            ~12 files
kse/monitoring/        ~7 files
kse/cache/             ~4 files
kse/utils/             ~7 files

gui/setup_wizard/      ~7 files
gui/control_center/    ~25 files (5 modules + 10 widgets + 8 dialogs)
gui/components/        ~4 files

config/                ~6 files
scripts/               ~12 files
assets/                ~20+ icon files + 2 themes

ROOT                   ~7 files (README, LICENSE, setup.py, etc)

TOTAL: ~178 files (core engine + GUI)
```

---

## 🚀 HOW TO USE THIS STRUCTURE

### Step 1: Create Directory Structure
```bash
# Create all folders
mkdir -p kse/core kse/storage kse/crawler kse/nlp
mkdir -p kse/indexing kse/ranking kse/search kse/server
mkdir -p kse/monitoring kse/cache kse/utils
mkdir -p gui/setup_wizard gui/control_center/modules gui/control_center/widgets
mkdir -p gui/control_center/dialogs gui/components
mkdir -p config data/storage/index data/storage/cache
mkdir -p data/storage/crawl_state data/storage/snapshots
mkdir -p data/logs data/exports scripts assets/icons
mkdir -p assets/themes assets/fonts assets/images
```

### Step 2: Create `__init__.py` files
```bash
# Create __init__.py in every folder
for dir in $(find . -type d -not -path './.git*'); do
  touch "$dir/__init__.py"
done
```

### Step 3: Create Root Files
```
README.md
LICENSE (MIT)
requirements.txt
setup.py
.gitignore
```

### Step 4: Start Development Phase by Phase
- **Week 1-2:** Create `kse/storage/` layer + config loading
- **Week 2-3:** Create `kse/crawler/` + domain loading
- **Week 3-4:** Create `kse/nlp/` + `kse/indexing/` + `kse/ranking/`
- **Week 4-5:** Create `kse/search/` + `kse/server/` Flask routes
- **Week 5-6:** Create `gui/setup_wizard/` (Phases 1-3)
- **Week 6-7:** Create `gui/control_center/` (Phase 4 - 5 modules)

---

## 💾 STORAGE ARCHITECTURE (Local File-Based)

### Index Storage
```
data/storage/index/
├─ inverted_index.pkl          [Main searchable index]
├─ metadata_index.pkl          [Page titles, descriptions, URLs]
├─ tfidf_cache.pkl             [Pre-computed TF-IDF scores]
├─ pagerank_cache.pkl          [Pre-computed PageRank scores]
└─ index_metadata.json         [Index creation time, page count, size]
```

### Crawl State
```
data/storage/crawl_state/
├─ domain_status.json          [Per-domain: last crawl, status, error count]
├─ url_queue.pkl               [URLs waiting to be crawled]
├─ visited_urls.pkl            [Set of already-crawled URLs]
└─ crawl_state.json            [Global state: total pages, last crawl time]
```

### Cache
```
data/storage/cache/
├─ search_cache.pkl            [Recent search results]
├─ query_cache.pkl             [Preprocessed queries]
└─ cache_manifest.json         [Cache stats & TTL]
```

---

## 🎯 DEVELOPMENT WORKFLOW

### For Each Module
1. **Create the file** (e.g., `kse_storage_manager.py`)
2. **Add type hints & docstrings** 
3. **Implement core logic**
4. **Add error handling & logging**
5. **Test manually** 
6. **Commit to GitHub** (after testing)

### Example: Creating `kse/storage/kse_storage_manager.py`
```python
"""
Storage Manager - File I/O orchestration for KSE
Handles all read/write operations for index, cache, and crawl state
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import pickle
import logging

logger = logging.getLogger(__name__)

class StorageManager:
    """Main storage orchestration layer"""
    
    def __init__(self, base_path: Path):
        """Initialize storage manager with base directory"""
        self.base_path = Path(base_path)
        self._ensure_directories()
        logger.info(f"Storage initialized at {self.base_path}")
    
    def _ensure_directories(self):
        """Create all required directories"""
        (self.base_path / "storage" / "index").mkdir(parents=True, exist_ok=True)
        (self.base_path / "storage" / "cache").mkdir(parents=True, exist_ok=True)
        # ... etc
        logger.debug("All storage directories verified")
    
    def save_index(self, index_data: Dict[str, Any]) -> None:
        """Save inverted index to disk"""
        try:
            path = self.base_path / "storage" / "index" / "inverted_index.pkl"
            with open(path, 'wb') as f:
                pickle.dump(index_data, f)
            logger.info(f"Index saved: {len(index_data)} entries")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    # ... more methods
```

---

## ⚙️ KEY MODULES TO BUILD FIRST

### Priority 1: Storage Foundation (Week 1)
1. `kse/core/kse_config.py` - Configuration management
2. `kse/core/kse_logger.py` - Logging system
3. `kse/storage/kse_storage_manager.py` - File I/O
4. `kse/storage/kse_domain_manager.py` - Load domain list

### Priority 2: Crawler (Week 2)
5. `kse/crawler/kse_crawler_core.py` - Main crawling loop
6. `kse/crawler/kse_http_client.py` - HTTP requests
7. `kse/crawler/kse_html_extractor.py` - Parse HTML

### Priority 3: Indexing & Search (Week 3-4)
8. `kse/indexing/kse_indexer_pipeline.py` - Index building
9. `kse/ranking/kse_ranking_core.py` - Ranking engine
10. `kse/search/kse_search_pipeline.py` - Search execution

### Priority 4: Server & GUI (Week 5-7)
11. `kse/server/kse_server.py` - Flask API
12. `gui/setup_wizard/setup_wizard_main.py` - Setup UI
13. `gui/control_center/control_center_main.py` - Control UI

---

## 📝 REQUIREMENTS.TXT PREVIEW

```
# Core Dependencies
Flask==2.3.0
PyQt6==6.6.0
requests==2.31.0
beautifulsoup4==4.12.0
lxml==4.9.0

# NLP & Language Processing
nltk==3.8.1
spacy==3.5.0
textblob==0.17.0

# Data Processing
numpy==1.24.0
pandas==1.5.0
scikit-learn==1.2.0

# Utilities
python-dotenv==1.0.0
PyYAML==6.0
psutil==5.9.0
```

---

## 🔧 SETUP WIZARD PHASES (GUI)

### Phase 1: Storage Configuration
- Select storage location (default: `./data`)
- Select domains to crawl
- Set crawl depth & speed

### Phase 2: Crawl Control
- Start crawling
- Real-time progress display
- Stop/pause/resume

### Phase 3: Server Bootstrap
- Start Flask server
- Verify API health
- Show connection info

### Phase 4: Control Center
- 5 operational modules (PCC, MCS, SCS, ACC, SCC)
- Live monitoring & control

---

## ✨ FINAL NOTES

This structure is:
- ✅ **Simplified** - No SQL, Docker, tests, docs initially
- ✅ **Server-focused** - All backend logic separated from GUI
- ✅ **Modular** - Each component independent and testable
- ✅ **Scalable** - Can add features phase by phase
- ✅ **Local storage** - Everything in files, no database server
- ✅ **GUI-integrated** - Full PyQt6 interface for control

**Next step:** Create this folder structure and start building Priority 1 modules!

---

**Generated:** January 25, 2026  
**Status:** Ready for implementation
```

Now let me create an additional file showing the exact file list for easy reference:
