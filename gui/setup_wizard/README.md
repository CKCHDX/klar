# KSE Setup Wizard - Implementation Documentation

## Overview

The KSE Setup Wizard is a three-phase PyQt6-based GUI that guides users through the initial setup of the Klar Search Engine. Each phase is implemented as a separate `QWizardPage` with comprehensive functionality.

## Files Created

### 1. `phase_1_storage_config.py` (15.0 KB)
**Purpose**: Storage configuration and domain selection

**Key Features**:
- Storage path selection with file browser
- Domain list loaded from `config/swedish_domains.json`
- Multi-select domain list with icons by category (📰 news, 🏛️ government, 🎓 education, 📚 reference)
- Crawl depth configuration (1-5 pages)
- Crawl speed settings (slow/medium/fast)
- Robots.txt respect checkbox
- Real-time form validation
- Select All/Deselect All buttons

**Main Class**: `Phase1StorageConfig(QWizardPage)`

**Key Methods**:
- `_load_domains()`: Load domains from JSON configuration
- `_validate_storage_path()`: Validate and create storage directory
- `get_configuration()`: Export configuration for next phases
- `isComplete()`: Validate page completion
- `validatePage()`: Final validation before moving to next phase

**Signals**:
- `config_changed`: Emitted when configuration changes

---

### 2. `phase_2_crawl_control.py` (21.9 KB)
**Purpose**: Real-time web crawling with progress monitoring

**Key Features**:
- Start/Pause/Stop crawling controls
- Real-time progress bar (domains crawled)
- Live statistics dashboard:
  - Pages indexed
  - Errors count
  - Crawling speed (pages/second)
  - Elapsed time
- Live log viewer with auto-scroll
- Thread-safe crawling operations
- Background worker thread (`CrawlerThread`)
- Periodic stats updates (1 second interval)

**Main Classes**:
1. `CrawlerThread(QThread)`: Background worker for crawling
   - Signals: `progress_updated`, `domain_completed`, `log_message`, `crawl_completed`, `error_occurred`
   - Methods: `run()`, `pause()`, `resume()`, `stop()`

2. `Phase2CrawlControl(QWizardPage)`: UI page
   - Metric cards with real-time updates
   - Color-coded log messages (info/success/warning/error)
   - Integrates with `kse.crawler.kse_crawler_core.CrawlerCore`

**Key Methods**:
- `_start_crawling()`: Initialize and start crawler thread
- `_pause_crawling()`: Pause/resume crawling
- `_stop_crawling()`: Stop crawler gracefully
- `_update_stats_display()`: Update statistics every second
- `_on_crawl_completed()`: Handle completion and enable next button

**Signals**:
- `crawl_completed`: Emitted with final statistics

---

### 3. `phase_3_server_bootstrap.py` (23.5 KB)
**Purpose**: Flask server startup and API verification

**Key Features**:
- Start/Stop Flask server controls
- Server status indicator (🟢 Running / ⚫ Stopped)
- Server URL display with copy support
- Health check endpoint testing
- Search API endpoint testing
- Periodic health checks (every 10 seconds)
- Test result display with color-coded messages
- Next steps information with clickable links

**Main Classes**:
1. `ServerThread(QThread)`: Background server worker
   - Runs Flask server in separate thread
   - Signals: `server_started`, `server_stopped`, `status_changed`, `error_occurred`, `health_check_result`
   - Integrates with `kse.server.kse_server.create_app()`

2. `Phase3ServerBootstrap(QWizardPage)`: UI page
   - API testing interface
   - Health monitoring
   - Result visualization

**Key Methods**:
- `_start_server()`: Start Flask server in background thread
- `_test_health()`: Test `/api/health` endpoint
- `_test_search()`: Test `/api/search` endpoint with sample query
- `_periodic_health_check()`: Silent background health monitoring
- `isComplete()`: Check server is running and healthy

**Signals**:
- `server_ready`: Emitted when server starts successfully

---

## Architecture

### Design Patterns
- **Wizard Pattern**: Multi-step guided setup process
- **Observer Pattern**: Qt signals/slots for event handling
- **Thread Pool Pattern**: Background workers for long-running tasks
- **MVC Pattern**: Separation of UI and business logic

### Threading Architecture
```
Main GUI Thread
├── Phase1StorageConfig (UI only)
├── Phase2CrawlControl (UI)
│   └── CrawlerThread (Worker)
│       └── CrawlerCore (Backend)
└── Phase3ServerBootstrap (UI)
    └── ServerThread (Worker)
        └── Flask Server (Backend)
```

### Data Flow
```
Phase 1 → Configuration Dict → Phase 2 → Crawl Stats → Phase 3 → Server URL
```

---

## Integration Points

### Backend Modules Used
1. **kse.crawler.kse_crawler_core.CrawlerCore**
   - Main crawling orchestrator
   - Respects robots.txt
   - Domain-specific crawling

2. **kse.storage.kse_storage_manager.StorageManager**
   - Persistent storage
   - Crawl state management

3. **kse.server.kse_server.create_app()**
   - Flask application factory
   - REST API endpoints
   - Health monitoring

### Configuration Files
- `config/swedish_domains.json`: Domain list with metadata
- `config/kse_default_config.yaml`: Default KSE configuration

### GUI Modules Used
- `gui.kse_gui_config.GUIConfig`: Colors, fonts, dimensions
- `gui.kse_gui_styles.Styles`: Reusable style definitions

---

## User Experience Flow

### Phase 1: Storage Configuration (1-2 minutes)
1. Select storage directory (default: ./data)
2. Select domains to crawl from curated list
3. Configure crawl depth (1-5 pages)
4. Set crawl speed (slow/medium/fast)
5. Enable/disable robots.txt respect
6. Validation: At least 1 domain selected

### Phase 2: Web Crawling (5-10 minutes)
1. Click "Start Crawling"
2. Monitor real-time progress bar
3. View live statistics (pages/sec, errors)
4. Read crawler logs in real-time
5. Option to pause/resume or stop
6. Completion: All domains crawled

### Phase 3: Server Bootstrap (1-2 minutes)
1. Click "Start Server"
2. Wait for server initialization (3 seconds)
3. Automatic health check
4. Test search API (optional)
5. Review next steps and URLs
6. Completion: Server running + health check passed

**Total Time**: ~10-15 minutes (varies by domain count and depth)

---

## Error Handling

### Phase 1 Errors
- Invalid storage path → Warning message, prevent next
- No domains selected → Warning dialog
- JSON load failure → Critical error dialog

### Phase 2 Errors
- Crawler initialization failure → Error dialog, re-enable start
- Domain crawl failure → Log error, continue with next domain
- Network errors → Logged, counted in error stats

### Phase 3 Errors
- Server start failure → Critical error dialog
- Port already in use → Error message with suggestion
- Health check failure → Warning, allow retry
- Connection timeout → Informative message (server starting up)

---

## Styling and Themes

### Dark Theme
All components use consistent dark theme from `GUIConfig`:
- Background: #1E1E1E (primary), #252525 (secondary)
- Primary color: #2196F3 (blue)
- Success: #4CAF50 (green)
- Warning: #FF9800 (orange)
- Error: #F44336 (red)

### Custom Styles
- Metric cards with large values and labels
- Colored status indicators (🟢 🟡 🔴 ⚫)
- Monospace font for URLs and logs
- Rounded corners (4-8px border-radius)

---

## Testing Recommendations

### Unit Tests
```python
# Test Phase 1
def test_storage_path_validation():
    phase1 = Phase1StorageConfig()
    assert phase1._validate_storage_path("/valid/path")
    assert not phase1._validate_storage_path("")

def test_domain_loading():
    phase1 = Phase1StorageConfig()
    phase1._load_domains()
    assert len(phase1.all_domains) > 0

# Test Phase 2
def test_crawler_thread():
    config = {'storage_path': './test_data', 'domains': [...]}
    thread = CrawlerThread(config)
    thread.start()
    # ... verify signals

# Test Phase 3
def test_server_health():
    phase3 = Phase3ServerBootstrap()
    phase3._start_server()
    time.sleep(5)
    phase3._test_health()
    assert phase3.health_check_passed
```

### Integration Tests
1. Run full wizard with test configuration
2. Verify data stored in correct locations
3. Verify server starts and responds
4. Verify crawled data is indexed

---

## Dependencies

### Required Packages
- PyQt6 >= 6.6.0
- requests >= 2.31.0
- Flask >= 2.3.2
- beautifulsoup4 >= 4.12.0

### Backend Requirements
- KSE core modules (kse.*)
- Swedish domains configuration
- Storage directory with write permissions

---

## Future Enhancements

### Potential Improvements
1. **Phase 1**:
   - Domain search/filter
   - Custom domain addition
   - Import domains from file
   - Crawl schedule configuration

2. **Phase 2**:
   - Real-time page preview
   - Error log export
   - Pause/resume persistence
   - Crawl statistics charts
   - Domain-specific progress bars

3. **Phase 3**:
   - Multiple server instances
   - SSL/HTTPS support
   - Authentication setup
   - API key generation
   - Browser auto-launch

### Performance Optimizations
- Parallel domain crawling
- Async HTTP requests
- Database connection pooling
- Incremental indexing

---

## Troubleshooting

### Common Issues

**Issue**: "Cannot find domains configuration"
- **Solution**: Ensure `config/swedish_domains.json` exists

**Issue**: "Storage path cannot be created"
- **Solution**: Check write permissions, use absolute path

**Issue**: "Crawler not starting"
- **Solution**: Check storage manager initialization, verify domains list

**Issue**: "Server won't start"
- **Solution**: Check port 5000 is free, verify Flask installed

**Issue**: "Health check failing"
- **Solution**: Wait 5-10 seconds for server full initialization

---

## Code Quality

### Metrics
- **Total Lines**: ~1,800 lines
- **Classes**: 5 (1 per phase + 2 workers)
- **Methods**: 60+ methods
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Try-except blocks with logging
- **Thread Safety**: QThread with signals/slots

### Best Practices Followed
- Type hints for parameters
- Descriptive variable names
- Separation of concerns
- DRY principle (reusable methods)
- Consistent code style
- Comprehensive logging
- User-friendly error messages

---

## Maintenance Notes

### Key Files to Monitor
- `config/swedish_domains.json`: Keep domains updated
- Backend crawler API: Ensure compatibility
- Flask server API: Maintain endpoint contracts

### Breaking Changes to Avoid
- Phase configuration dictionary structure
- Signal signatures
- Backend API changes without adapter pattern

---

## License
Part of Klar Search Engine (KSE) project

## Authors
Implementation completed as per requirements specification
