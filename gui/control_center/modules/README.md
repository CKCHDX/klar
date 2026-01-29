# Control Center Modules Documentation

## Overview

The KSE Control Center consists of 5 specialized modules, each handling different aspects of system management and monitoring. All modules are built with PyQt6 and follow a consistent architecture.

## Module Architecture

### Common Structure

All modules inherit from `QWidget` and implement:
- **Constructor**: Takes `ControlCenterAPIClient` instance
- **_setup_ui()**: Builds the user interface
- **_connect_signals()**: Connects Qt signals/slots
- **showEvent()**: Starts auto-updates when visible
- **hideEvent()**: Stops auto-updates when hidden
- **refresh_data()**: Refreshes module data from API
- **start_updates()**: Starts periodic updates
- **stop_updates()**: Stops periodic updates

### API Integration

All modules use the `ControlCenterAPIClient` for backend communication:
- Non-blocking async requests
- Automatic retry with exponential backoff
- Signal-based response handling
- Connection status monitoring

## Modules

### 1. PCC - Primary Control Center (`pcc_primary_control.py`)

**Purpose**: Real-time system overview dashboard with quick actions

**Update Interval**: 2 seconds

**Components**:
- **StatusTile**: Metric display cards for CPU, RAM, Disk, Index
- **EventTimeline**: Recent events table (last 50 events)
- Quick action buttons (Refresh, Clear Cache, Rebuild Index)

**Features**:
- Real-time system metrics with color-coded status
- Progress bars for resource usage
- Event logging with timestamps
- Automatic metric updates

**Key Methods**:
- `refresh_data()`: Fetch latest system stats
- `_on_health_update(data)`: Process health check data
- `_on_stats_update(data)`: Update metric tiles
- `_clear_cache()`: Clear search cache
- `_rebuild_index()`: Trigger index rebuild

**Signals**:
- `refresh_requested`: Emitted when manual refresh triggered

---

### 2. MCS - Main Control Server (`mcs_main_control_server.py`)

**Purpose**: Server lifecycle management and performance monitoring

**Update Interval**: 5 seconds

**Components**:
- **ServerControlPanel**: Start/Stop/Restart controls with status indicator
- **PerformanceMetrics**: QPS, latency, uptime display
- **SnapshotManager**: Create and restore index snapshots
- **LogViewer**: Real-time server logs (last 100 lines)

**Features**:
- Server control with visual status feedback
- Live performance metrics with color-coded thresholds
- Port configuration management
- Index snapshot operations
- Log streaming with auto-scroll

**Key Methods**:
- `_start_server()`: Start server instance
- `_stop_server()`: Stop server gracefully
- `_restart_server()`: Restart server
- `_create_snapshot(name)`: Create index snapshot
- `_restore_snapshot(name)`: Restore from snapshot

**Signals**:
- `server_start_requested`
- `server_stop_requested`
- `server_restart_requested`
- `snapshot_create_requested`
- `snapshot_restore_requested`

---

### 3. SCS - System Control Status (`scs_system_status.py`)

**Purpose**: Component health monitoring and system diagnostics

**Update Interval**: 10 seconds

**Components**:
- **ComponentHealthTable**: Health status for 6 system components
  - Crawler, Indexer, Search Engine, API Server, Cache, Storage
- **StorageStatistics**: Index size, cache size, disk usage
- **MetricGauge**: Circular gauges for CPU, Memory, QPS
- **AlertPanel**: System alerts and warnings table

**Features**:
- Component-level health tracking
- Storage metrics with progress bars
- Visual metric gauges
- Alert generation for critical conditions
- Historical health data tracking

**Key Methods**:
- `_on_health_update(data)`: Update component health
- `_on_stats_update(data)`: Update storage stats and gauges
- Alert generation for CPU > 70%, Memory > 90%, etc.

**Health States**:
- `healthy`: Green - All systems operational
- `degraded`: Yellow - Performance issues
- `unhealthy`: Red - Critical issues
- `unknown`: Gray - Status unavailable

---

### 4. ACC - Auxiliary Control Center (`acc_auxiliary_control.py`)

**Purpose**: System maintenance and diagnostic tools

**Update Interval**: 30 seconds

**Components**:
- **IndexRebuildPanel**: Full/partial index rebuild with progress
- **DataCleanupPanel**: 6 cleanup operations
  - Clear cache, clear logs, compact database
  - Optimize index, remove duplicates, vacuum storage
- **ConsistencyChecker**: Data integrity verification with reporting
- **LogRotationControl**: Log rotation settings and controls
- **DiagnosticsPanel**: System diagnostics runner

**Features**:
- Index rebuild with options (full/optimize/verify)
- Progress tracking for long-running operations
- Consistency checking with detailed reports
- Configurable log rotation (size, age, backup count)
- Comprehensive system diagnostics

**Key Methods**:
- `_on_rebuild_index(options)`: Handle rebuild request
- `_on_cleanup(cleanup_type)`: Execute cleanup operation
- `_on_consistency_check()`: Run data consistency check
- `_on_log_rotation(settings)`: Apply log rotation settings
- `_on_run_diagnostics()`: Run system diagnostics

**Signals**:
- `rebuild_requested`
- `cleanup_requested`
- `check_requested`
- `rotate_requested`
- `diagnostics_requested`

---

### 5. SCC - Secondary Control Center (`scc_secondary_control.py`)

**Purpose**: Analytics, reporting, and data export

**Update Interval**: 15 seconds

**Components**:
- **SearchAnalytics**: Search metrics (queries/day, latency, popular terms)
- **CrawlerAnalytics**: Crawler metrics (pages/day, success rate, errors)
- **QueryTrendingTable**: Top 20 trending queries with filters
- **DomainStatisticsTable**: Per-domain crawl statistics
- **DataExportPanel**: Export data to CSV/JSON/Excel

**Features**:
- Search and crawler analytics with trends
- Time-range filtering (Today, 7 days, 30 days, All time)
- Top 20 trending queries with latency and trend indicators
- Domain-level statistics
- Data export in multiple formats

**Key Methods**:
- `_load_sample_data()`: Load demonstration data
- `_on_stats_update(data)`: Update analytics from API
- `_on_export_data(data_type, filename)`: Export data
- `_export_json(data_type, filename)`: JSON export
- `_export_csv(data_type, filename)`: CSV export

**Signals**:
- `export_requested`

**Analytics Metrics**:
- Queries today/yesterday with % change
- Average/min/max latency
- Success rate percentage
- Error counts and rates
- Popular search terms

---

## Styling and Theming

All modules use centralized styling from `gui/kse_gui_styles.py`:

### Available Styles
- `get_card_style()`: Card containers
- `get_button_style()`: Primary buttons
- `get_success_button_style()`: Success/green buttons
- `get_danger_button_style()`: Danger/red buttons
- `get_warning_button_style()`: Warning/orange buttons
- `get_title_style(size)`: Headers and titles
- `get_status_label_style(status)`: Status-colored labels
- `get_metric_card_style()`: Metric display cards
- `get_log_viewer_style()`: Log text areas
- `get_table_style()`: Data tables

### Color Scheme (Dark Theme)
- **Primary**: #2196F3 (Blue)
- **Success**: #4CAF50 (Green)
- **Warning**: #FF9800 (Orange)
- **Error**: #F44336 (Red)
- **Info**: #00BCD4 (Cyan)
- **Background**: #1E1E1E
- **Text**: #FFFFFF / #B0B0B0

---

## Usage Example

```python
from PyQt6.QtWidgets import QApplication
from gui.control_center.control_center_api_client import ControlCenterAPIClient
from gui.control_center.modules import (
    PCCPrimaryControl,
    MCSMainControlServer,
    SCSSystemStatus,
    ACCAuxiliaryControl,
    SCCSecondaryControl
)

# Initialize Qt application
app = QApplication(sys.argv)

# Create API client
api_client = ControlCenterAPIClient()
api_client.start_health_monitoring()

# Create modules
pcc = PCCPrimaryControl(api_client)
mcs = MCSMainControlServer(api_client)
scs = SCSSystemStatus(api_client)
acc = ACCAuxiliaryControl(api_client)
scc = SCCSecondaryControl(api_client)

# Show module
pcc.show()

# Start event loop
app.exec()
```

---

## API Endpoints Used

Each module interacts with specific API endpoints:

### PCC Endpoints
- `/api/health` - Health check
- `/api/stats` - System statistics
- `/api/cache/clear` - Clear cache

### MCS Endpoints
- `/api/health` - Server status
- `/api/stats` - Performance metrics
- `/api/server/start` - Start server
- `/api/server/stop` - Stop server
- `/api/snapshot/create` - Create snapshot
- `/api/snapshot/restore` - Restore snapshot

### SCS Endpoints
- `/api/health` - Component health
- `/api/stats` - System metrics
- `/api/monitoring/status` - Monitoring data

### ACC Endpoints
- `/api/index/rebuild` - Rebuild index
- `/api/cleanup/*` - Cleanup operations
- `/api/diagnostics` - Run diagnostics

### SCC Endpoints
- `/api/stats` - Analytics data
- `/api/analytics/search` - Search analytics
- `/api/analytics/crawler` - Crawler analytics
- `/api/trending` - Trending queries

---

## Error Handling

All modules implement robust error handling:

1. **API Errors**: Caught and logged, displayed in UI
2. **Update Failures**: Graceful degradation, retry logic
3. **UI Errors**: Exception logging, user notification
4. **Thread Safety**: Qt signals for cross-thread communication

---

## Performance Considerations

### Update Intervals
- **PCC**: 2s - Frequent for real-time monitoring
- **MCS**: 5s - Balance of freshness and load
- **SCS**: 10s - Component health changes slowly
- **ACC**: 30s - Maintenance tasks are infrequent
- **SCC**: 15s - Analytics aggregation delay

### Resource Usage
- Auto-pause updates when module hidden
- Efficient signal/slot connections
- Limited data retention (50-100 items)
- Async API calls prevent UI blocking

---

## Testing

To test module functionality:

```bash
# Syntax check
python -m py_compile gui/control_center/modules/*.py

# Import check (requires PyQt6)
python -c "from gui.control_center.modules import *"

# Run test suite
python test_control_center_modules.py
```

---

## Module Integration

Modules are integrated into the Control Center via `control_center_main.py`:

1. **Module Registry**: Defined in `control_center_config.py`
2. **Navigation**: Managed by `control_center_navigation.py`
3. **Layout**: Stacked widget system for module switching
4. **Lifecycle**: Auto-start/stop updates on show/hide

---

## Future Enhancements

Potential improvements:

1. **Customizable Dashboards**: User-configurable layouts
2. **Alert Rules**: User-defined alert thresholds
3. **Export Scheduling**: Automatic periodic exports
4. **Historical Charts**: Time-series visualization
5. **Mobile View**: Responsive design for smaller screens
6. **Plugin System**: Custom module support
7. **Real-time Streaming**: WebSocket-based updates
8. **Multi-server Support**: Monitor multiple KSE instances

---

## Troubleshooting

### Common Issues

**Module won't load**:
- Check PyQt6 installation: `pip install PyQt6`
- Verify API client is initialized
- Check import paths

**Updates not working**:
- Verify API server is running
- Check API base URL in config
- Review network connectivity

**High CPU usage**:
- Reduce update intervals
- Check for infinite loops in callbacks
- Profile with Qt Creator

**UI freezing**:
- Ensure API calls are async
- Check for blocking operations in UI thread
- Use QTimer for delays instead of time.sleep()

---

## License

These modules are part of the KSE (Klar Search Engine) project.

---

## Contributors

Control Center Module Implementation - January 2024
