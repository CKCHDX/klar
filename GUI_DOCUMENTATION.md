# 🎨 KSE GUI - Complete Documentation

**Klar Search Engine GUI Application**  
**Version:** 3.0.0  
**Date:** January 29, 2026  
**Status:** Production Ready  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Setup Wizard](#setup-wizard)
6. [Control Center](#control-center)
7. [Components Reference](#components-reference)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)
10. [Development](#development)

---

## 🎯 Overview

The KSE GUI is a professional PyQt6-based desktop application for managing and monitoring the Klar Search Engine. It provides:

- **Setup Wizard** - Interactive 3-phase setup for first-time configuration
- **Control Center** - 5 operational modules for system management
- **Dark Theme** - Professional dark theme for reduced eye strain
- **Real-time Monitoring** - Live system metrics and statistics
- **API Integration** - Seamless connection to KSE backend server

### Key Features

✅ **User-Friendly** - Intuitive interface for all skill levels  
✅ **Production-Ready** - Robust error handling and logging  
✅ **Responsive** - Async operations with progress feedback  
✅ **Extensible** - Modular architecture for easy enhancement  
✅ **Cross-Platform** - Works on Windows, Linux, and macOS  

---

## 🏗️ Architecture

### Directory Structure

```
gui/
├── kse_gui_main.py              # Main application entry point
├── kse_gui_config.py            # GUI configuration
├── kse_gui_dark_theme.py        # Dark theme stylesheet
├── kse_gui_styles.py            # Reusable styles
│
├── setup_wizard/                # Setup Wizard (Phases 1-3)
│   ├── setup_wizard_main.py     # Wizard orchestrator
│   ├── phase_1_storage_config.py # Storage configuration
│   ├── phase_2_crawl_control.py  # Crawl control
│   └── phase_3_server_bootstrap.py # Server bootstrap
│
├── control_center/              # Control Center (Phase 4)
│   ├── control_center_main.py   # Main window
│   ├── control_center_config.py # Configuration
│   ├── control_center_navigation.py # Navigation
│   ├── control_center_api_client.py # API client
│   │
│   ├── modules/                 # 5 Operational Modules
│   │   ├── pcc_primary_control.py       # Primary Control
│   │   ├── mcs_main_control_server.py   # Main Control Server
│   │   ├── scs_system_status.py         # System Status
│   │   ├── acc_auxiliary_control.py     # Auxiliary Control
│   │   └── scc_secondary_control.py     # Secondary Control
│   │
│   ├── widgets/                 # Reusable Widgets
│   │   ├── status_tile.py       # Status tiles
│   │   ├── chart_widget.py      # Charts
│   │   ├── gauge_widget.py      # Gauges
│   │   ├── metric_card.py       # Metric cards
│   │   ├── log_viewer.py        # Log viewer
│   │   ├── table_widget.py      # Enhanced tables
│   │   ├── timeline_widget.py   # Timeline
│   │   ├── progress_widget.py   # Progress bars
│   │   ├── notification_widget.py # Notifications
│   │   └── status_indicator.py  # Status indicators
│   │
│   └── dialogs/                 # Dialog Windows
│       ├── domain_selection_dialog.py # Domain picker
│       ├── settings_dialog.py         # Settings
│       ├── export_dialog.py           # Export data
│       ├── import_dialog.py           # Import data
│       ├── confirmation_dialog.py     # Confirmations
│       ├── about_dialog.py            # About dialog
│       ├── error_dialog.py            # Error display
│       └── snapshot_dialog.py         # Snapshot manager
│
└── components/                  # UI Components
    ├── menubar.py               # Menu bar
    ├── statusbar.py             # Status bar
    ├── toolbar.py               # Toolbar
    └── sidebar.py               # Sidebar
```

### Component Relationships

```
kse_gui_main.py
    ├── SetupWizard (First Run)
    │   ├── Phase1StorageConfig
    │   ├── Phase2CrawlControl
    │   └── Phase3ServerBootstrap
    │
    └── ControlCenter (Normal Run)
        ├── PrimaryControl (PCC)
        ├── MainControlServer (MCS)
        ├── SystemStatus (SCS)
        ├── AuxiliaryControl (ACC)
        └── SecondaryControl (SCC)
```

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Dependencies

```bash
# Core dependencies
pip install PyQt6>=6.6.0
pip install PyYAML>=6.0
pip install requests>=2.31.0

# Optional (for enhanced features)
pip install matplotlib>=3.7.0  # For charts
pip install psutil>=5.9.0      # For system metrics
```

### Install from Source

```bash
# Clone repository
git clone https://github.com/CKCHDX/klar.git
cd klar

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

---

## 🚀 Quick Start

### Method 1: Using Startup Script

```bash
# From project root
python scripts/start_gui.py
```

### Method 2: Direct Python Import

```bash
python -m gui.kse_gui_main
```

### Method 3: Python Code

```python
from gui.kse_gui_main import main
main()
```

### First Run

On first run, the **Setup Wizard** will launch automatically:

1. **Phase 1:** Configure storage and select domains
2. **Phase 2:** Start crawling and indexing
3. **Phase 3:** Bootstrap server and verify API

After setup, the **Control Center** will launch automatically.

### Subsequent Runs

On subsequent runs, the **Control Center** will launch directly, showing:

- System overview dashboard
- Server control panel
- Live monitoring and statistics
- Administrative tools

---

## 🧙 Setup Wizard

The Setup Wizard guides you through initial KSE configuration in 3 phases.

### Phase 1: Storage Configuration

**Purpose:** Configure storage location and select domains to crawl

**Steps:**
1. Choose storage path (default: `./data`)
2. Select domains from the list (multi-select)
3. Set crawl depth (1-5, default: 2)
4. Set crawl speed (slow/medium/fast)
5. Click "Next" to proceed

**Configuration:**
- Storage path is validated for write access
- At least 1 domain must be selected
- Crawl depth affects indexing time
- Crawl speed affects server load

### Phase 2: Crawl Control

**Purpose:** Initiate web crawling and indexing

**Features:**
- Start/Pause/Stop controls
- Real-time progress bar
- Live statistics (pages/sec, errors)
- Log viewer with filtering
- Estimated time remaining

**Controls:**
- **Start Crawling:** Begin crawling selected domains
- **Pause:** Temporarily pause crawling
- **Resume:** Continue paused crawl
- **Stop:** Terminate crawling completely

**Monitoring:**
- Domains crawled: X / Y
- Pages indexed: X,XXX
- Current speed: XX pages/sec
- Errors: X warnings, X errors

### Phase 3: Server Bootstrap

**Purpose:** Start Flask API server and verify operation

**Features:**
- Server start/stop controls
- Live server status indicator
- API endpoint health checks
- Connection testing
- Server configuration display

**Verification Tests:**
1. Health check (`/api/health`)
2. Search test (`/api/search?q=test`)
3. Stats check (`/api/stats`)

**Success Criteria:**
- Server started successfully
- All API tests pass
- Green status indicators

**Next Steps:**
After successful setup, click "Launch Control Center" to proceed to the main application.

---

## 🎛️ Control Center

The Control Center is the main operational interface with 5 modules.

### Module 1: Primary Control Center (PCC)

**Purpose:** System overview and quick actions

**Features:**
- 4 status tiles (CPU, RAM, Disk, Index)
- Event timeline (last 50 events)
- Quick action buttons
- Auto-refresh every 2 seconds

**Status Tiles:**
- **CPU Usage:** Current CPU percentage
- **RAM Usage:** Current memory usage
- **Disk Usage:** Storage space used
- **Index Size:** Number of indexed documents

**Quick Actions:**
- Refresh All Data
- Clear Search Cache
- Rebuild Index
- View System Diagnostics

**Keyboard Shortcut:** `Ctrl+1`

### Module 2: Main Control Server (MCS)

**Purpose:** Server management and performance monitoring

**Features:**
- Server start/stop/restart controls
- Live performance metrics
- Port configuration
- Log viewer
- Snapshot management

**Performance Metrics:**
- Queries Per Second (QPS)
- Average Latency (ms)
- Server Uptime
- Active Connections
- Error Rate

**Server Controls:**
- **Start Server:** Launch Flask API server
- **Stop Server:** Gracefully shutdown server
- **Restart Server:** Stop and start server
- **View Logs:** Show last 100 log lines

**Snapshot Management:**
- Create index snapshot
- Restore from snapshot
- Delete old snapshots
- View snapshot details

**Keyboard Shortcut:** `Ctrl+2`

### Module 3: System Control Status (SCS)

**Purpose:** Component health and system diagnostics

**Features:**
- Component health table
- Storage statistics
- Metric gauges
- Alert/warning display
- Historical health data

**Components Monitored:**
- Crawler (status, last run, pages crawled)
- Indexer (status, index size, last update)
- Search (status, queries/sec, cache hit rate)
- Server (status, uptime, port)
- Storage (status, disk space, file count)
- Cache (status, size, hit rate)

**Health Indicators:**
- 🟢 **Healthy:** Component operating normally
- 🟡 **Warning:** Minor issues detected
- 🔴 **Critical:** Major issues requiring attention
- ⚫ **Offline:** Component not running

**Storage Statistics:**
- Index size with progress bar
- Cache size with progress bar
- Disk usage with progress bar
- File counts and percentages

**Metric Gauges:**
- CPU usage (0-100%)
- Memory usage (0-100%)
- QPS (queries per second)

**Keyboard Shortcut:** `Ctrl+3`

### Module 4: Auxiliary Control Center (ACC)

**Purpose:** Maintenance and administrative tools

**Features:**
- Index rebuild tool
- Data cleanup operations
- Consistency checker
- Log rotation
- System diagnostics

**Index Rebuild:**
- Full index rebuild with progress
- Estimated time remaining
- Cancel/pause options
- Post-rebuild verification

**Data Cleanup Operations:**
1. Clear search cache
2. Clear query cache
3. Remove old logs (>30 days)
4. Optimize storage files
5. Remove orphaned files
6. Compact database (future)

**Consistency Checker:**
- Verify index integrity
- Check file consistency
- Validate data structures
- Generate diagnostic report

**Log Rotation:**
- Configure rotation settings
- Set max log size (MB)
- Set max log age (days)
- Manual rotation trigger

**System Diagnostics:**
- Generate comprehensive report
- Export to file
- Include system info, health, logs

**Keyboard Shortcut:** `Ctrl+4`

### Module 5: Secondary Control Center (SCC)

**Purpose:** Analytics and reporting

**Features:**
- Search analytics dashboard
- Crawler analytics
- Query trending table
- Domain statistics
- Data export functionality

**Search Analytics:**
- Total queries today
- Popular search terms (top 10)
- Average query latency
- Cache hit rate
- Query success rate

**Crawler Analytics:**
- Pages crawled today
- Crawl success rate
- Average crawl time
- Error distribution
- Domain coverage

**Query Trending:**
- Top 20 most searched queries
- Query frequency
- Last searched timestamp
- Average results returned

**Domain Statistics:**
- Domain name
- Pages indexed
- Last crawl date
- Crawl status
- Error count

**Data Export:**
- Export search analytics (CSV/JSON/Excel)
- Export crawler logs
- Export domain statistics
- Export query trends
- Custom date range selection

**Keyboard Shortcut:** `Ctrl+5`

---

## 🧩 Components Reference

### Widgets

#### StatusTile
Displays system metrics in a tile format.

```python
from gui.control_center.widgets.status_tile import StatusTile

tile = StatusTile("CPU Usage", "45%", status="warning")
tile.value_changed.connect(on_value_change)
```

#### ChartWidget
Live charts for visualizing data.

```python
from gui.control_center.widgets.chart_widget import ChartWidget

chart = ChartWidget(chart_type="line", title="QPS Over Time")
chart.add_data_point(time.time(), qps_value)
```

#### GaugeWidget
Circular gauge for percentage values.

```python
from gui.control_center.widgets.gauge_widget import GaugeWidget

gauge = GaugeWidget(min_value=0, max_value=100, title="CPU")
gauge.set_value(75)
```

### Dialogs

#### SettingsDialog
Application settings management.

```python
from gui.control_center.dialogs.settings_dialog import SettingsDialog

dialog = SettingsDialog(parent=self)
if dialog.exec():
    settings = dialog.get_settings()
```

#### ExportDialog
Data export with format selection.

```python
from gui.control_center.dialogs.export_dialog import ExportDialog

dialog = ExportDialog(data=analytics_data, parent=self)
if dialog.exec():
    file_path = dialog.get_file_path()
```

### Components

#### MenuBar
Application menu bar.

```python
from gui.components.menubar import MenuBar

menubar = MenuBar(parent=self)
menubar.file_exit.connect(self.close)
```

#### StatusBar
Status bar with live updates.

```python
from gui.components.statusbar import StatusBar

statusbar = StatusBar(parent=self)
statusbar.show_message("Ready", 3000)
```

---

## ⚙️ Configuration

### GUI Configuration File

Location: `gui/kse_gui_config.py`

```python
# Window dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Theme
THEME = "dark"

# Update intervals (milliseconds)
UPDATE_INTERVALS = {
    'fast': 1000,
    'normal': 5000,
    'slow': 10000,
}
```

### Control Center Configuration

Location: `gui/control_center/control_center_config.py`

```python
# Module update intervals
MODULE_UPDATE_INTERVALS = {
    'pcc': 2000,   # 2 seconds
    'mcs': 5000,   # 5 seconds
    'scs': 3000,   # 3 seconds
    'acc': 10000,  # 10 seconds
    'scc': 30000,  # 30 seconds
}

# API endpoints
API_BASE_URL = "http://localhost:5000"
API_ENDPOINTS = {
    'health': '/api/health',
    'search': '/api/search',
    'stats': '/api/stats',
    # ... more endpoints
}
```

### Customizing Theme

Edit `gui/kse_gui_dark_theme.py` to customize colors:

```python
COLORS = {
    'primary': '#2196F3',      # Change primary color
    'secondary': '#1976D2',
    'success': '#4CAF50',
    # ... more colors
}
```

---

## 🔧 Troubleshooting

### Issue: GUI doesn't start

**Symptoms:** Error message or blank window

**Solutions:**
1. Check PyQt6 installation: `pip install PyQt6`
2. Verify Python version: `python --version` (3.8+)
3. Check logs: `data/logs/kse.log`

### Issue: Setup Wizard fails

**Symptoms:** Error during crawling or server bootstrap

**Solutions:**
1. Check storage path permissions
2. Verify backend modules installed
3. Check Flask server logs
4. Ensure ports available (5000 default)

### Issue: Control Center shows errors

**Symptoms:** Red status indicators, API errors

**Solutions:**
1. Verify server is running
2. Check API URL configuration
3. Test API manually: `curl http://localhost:5000/api/health`
4. Review server logs

### Issue: Slow performance

**Symptoms:** Laggy UI, delayed updates

**Solutions:**
1. Increase update intervals in config
2. Reduce number of domains being crawled
3. Clear caches (ACC module)
4. Check system resources (CPU, RAM)

### Common Error Messages

**"Failed to connect to API"**
- Server not running
- Wrong port configured
- Firewall blocking connection

**"Index not found"**
- Setup not completed
- Index files deleted/corrupted
- Run Setup Wizard again

**"Permission denied"**
- Storage path not writable
- Run with appropriate permissions
- Check file ownership

---

## 👨‍💻 Development

### Running in Development Mode

```bash
# Enable debug logging
export KSE_DEBUG=1

# Run with verbose output
python -m gui.kse_gui_main --verbose
```

### Creating New Widgets

```python
from PyQt6.QtWidgets import QWidget
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles

class MyCustomWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Use GUIConfig for styling
        self.setStyleSheet(Styles.get_card_style())
```

### Adding New Modules

1. Create module file in `gui/control_center/modules/`
2. Inherit from `QWidget`
3. Implement `update_data()` method
4. Register in `control_center_config.py`
5. Add to navigation in `control_center_navigation.py`

### Testing

```bash
# Test individual components
python gui/control_center/widgets/status_tile.py

# Test modules
python gui/control_center/modules/pcc_primary_control.py

# Test full application
python scripts/start_gui.py
```

---

## 📚 Additional Resources

**Documentation:**
- `README.md` - Project overview
- `QUICKSTART.md` - Quick start guide
- `KSE-Tree.md` - Architecture specification

**Code Examples:**
- `gui/setup_wizard/README.md` - Setup Wizard guide
- `gui/control_center/README.md` - Control Center guide
- `example_widgets_usage.py` - Widget examples

**Support:**
- GitHub Issues: https://github.com/CKCHDX/klar/issues
- Email: support@oscyra.solutions

---

## 📄 License

MIT License - See LICENSE file for details

---

**KSE GUI - Professional Search Engine Management Interface**

*Built with PyQt6 | Designed for Klar Search Engine*

*Version 3.0.0 | January 2026*
