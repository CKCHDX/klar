# Control Center Modules - Quick Reference

## Module Overview

| Module | File | Purpose | Update Rate |
|--------|------|---------|-------------|
| PCC | `pcc_primary_control.py` | System overview & quick actions | 2s |
| MCS | `mcs_main_control_server.py` | Server management & logs | 5s |
| SCS | `scs_system_status.py` | Health monitoring & alerts | 10s |
| ACC | `acc_auxiliary_control.py` | Maintenance & diagnostics | 30s |
| SCC | `scc_secondary_control.py` | Analytics & reporting | 15s |

## Quick Start

```python
from PyQt6.QtWidgets import QApplication
from gui.control_center.control_center_api_client import ControlCenterAPIClient
from gui.control_center.modules import PCCPrimaryControl

app = QApplication(sys.argv)
api_client = ControlCenterAPIClient()
pcc = PCCPrimaryControl(api_client)
pcc.show()
app.exec()
```

## Module Capabilities

### PCC - Primary Control Center
- ✅ Real-time CPU/RAM/Disk/Index metrics
- ✅ Event timeline (50 events)
- ✅ Quick actions (refresh, cache clear, rebuild)
- ✅ Color-coded status indicators
- ✅ Auto-updates every 2 seconds

### MCS - Main Control Server
- ✅ Start/Stop/Restart server
- ✅ Performance metrics (QPS, latency, uptime)
- ✅ Snapshot create/restore
- ✅ Live log streaming (100 lines)
- ✅ Port configuration
- ✅ Status indicators

### SCS - System Control Status
- ✅ 6 component health tracking
- ✅ Storage statistics
- ✅ Visual metric gauges
- ✅ Alert generation
- ✅ Health history
- ✅ Critical threshold monitoring

### ACC - Auxiliary Control
- ✅ Index rebuild with progress
- ✅ 6 cleanup operations
- ✅ Consistency checking
- ✅ Log rotation config
- ✅ System diagnostics
- ✅ Detailed reporting

### SCC - Secondary Control
- ✅ Search analytics with trends
- ✅ Crawler analytics
- ✅ Top 20 trending queries
- ✅ Domain statistics
- ✅ CSV/JSON/Excel export
- ✅ Time-range filtering

## API Endpoints

### Common Endpoints
```python
'/api/health'           # Health check
'/api/stats'            # System statistics
```

### PCC Specific
```python
'/api/cache/clear'      # Clear cache
```

### MCS Specific
```python
'/api/server/start'     # Start server
'/api/server/stop'      # Stop server
'/api/snapshot/create'  # Create snapshot
'/api/snapshot/restore' # Restore snapshot
```

### SCS Specific
```python
'/api/monitoring/status' # Monitoring data
```

### ACC Specific
```python
'/api/index/rebuild'    # Rebuild index
'/api/cleanup/*'        # Cleanup operations
'/api/diagnostics'      # Run diagnostics
```

### SCC Specific
```python
'/api/analytics/search'  # Search analytics
'/api/analytics/crawler' # Crawler analytics
'/api/trending'         # Trending queries
```

## Common Patterns

### Creating a Status Tile
```python
from gui.control_center.modules.pcc_primary_control import StatusTile

tile = StatusTile("CPU Usage")
tile.update_value("45.2%", "Normal", progress=45, color=GUIConfig.COLORS['success'])
```

### Adding Events
```python
event_timeline.add_event("System", "Cache cleared", "SUCCESS")
event_timeline.add_event("Error", "Connection failed", "ERROR")
```

### Updating Tables
```python
table.insertRow(0)
table.setItem(0, 0, QTableWidgetItem("Value"))
```

### Connecting Signals
```python
self.api_client.health_check_completed.connect(self._on_health_update)
self.button.clicked.connect(self._on_button_click)
```

## Styling

### Available Styles
```python
from gui.kse_gui_styles import Styles

Styles.get_card_style()              # Card container
Styles.get_button_style()            # Primary button
Styles.get_success_button_style()    # Green button
Styles.get_danger_button_style()     # Red button
Styles.get_warning_button_style()    # Orange button
Styles.get_title_style('header')     # Large title
Styles.get_metric_card_style()       # Metric display
Styles.get_log_viewer_style()        # Log text area
Styles.get_table_style()             # Data table
```

### Colors
```python
from gui.kse_gui_config import GUIConfig

GUIConfig.COLORS['primary']    # #2196F3 Blue
GUIConfig.COLORS['success']    # #4CAF50 Green
GUIConfig.COLORS['warning']    # #FF9800 Orange
GUIConfig.COLORS['error']      # #F44336 Red
GUIConfig.COLORS['info']       # #00BCD4 Cyan
```

## Error Handling

### Try-Except Pattern
```python
def refresh_data(self):
    try:
        self.api_client.get_stats()
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        self.show_error(str(e))
```

### Signal Error Handling
```python
self.api_client.error_occurred.connect(self._on_error)

def _on_error(self, error: str):
    logger.error(f"API error: {error}")
    self.status_label.setText(f"Error: {error}")
```

## Timer Management

### Start/Stop Updates
```python
def showEvent(self, event):
    super().showEvent(event)
    self.start_updates()

def hideEvent(self, event):
    super().hideEvent(event)
    self.stop_updates()

def start_updates(self):
    if not self.update_timer.isActive():
        self.update_timer.start()

def stop_updates(self):
    if self.update_timer.isActive():
        self.update_timer.stop()
```

## Component Lifecycle

```
1. __init__()           → Create widgets, setup timers
2. _setup_ui()          → Build UI layout
3. _connect_signals()   → Connect signal/slots
4. showEvent()          → Start auto-updates
5. refresh_data()       → Fetch data from API
6. _on_*_update()       → Process API responses
7. hideEvent()          → Stop auto-updates
```

## Data Flow

```
API Client → Signal → Module Handler → UI Update

Example:
api_client.get_stats()
    ↓
stats_received signal
    ↓
_on_stats_update(data)
    ↓
tile.update_value(...)
```

## Testing Checklist

- [ ] Module imports successfully
- [ ] UI renders without errors
- [ ] API client connects
- [ ] Updates start/stop correctly
- [ ] Signals connected properly
- [ ] Error handling works
- [ ] Timers cleanup on hide
- [ ] Memory doesn't leak

## Performance Tips

1. **Reduce Update Frequency**: Adjust timer intervals for less critical data
2. **Limit Table Rows**: Keep max 50-100 rows in tables
3. **Use Signals**: Always use signals for cross-thread communication
4. **Cleanup Timers**: Stop timers when module hidden
5. **Batch Updates**: Group multiple UI updates together
6. **Lazy Loading**: Load data only when module visible

## Common Issues

### UI Freezing
**Cause**: Blocking operations in UI thread
**Fix**: Use async API calls with signals

### Memory Leaks
**Cause**: Timers not stopped
**Fix**: Implement hideEvent() to stop timers

### Update Delays
**Cause**: Timer interval too long
**Fix**: Adjust interval in __init__()

### Missing Data
**Cause**: API not responding
**Fix**: Check API client connection status

## File Structure

```
gui/control_center/modules/
├── __init__.py                    # Module exports
├── pcc_primary_control.py         # Primary Control
├── mcs_main_control_server.py     # Main Server
├── scs_system_status.py           # System Status
├── acc_auxiliary_control.py       # Auxiliary Control
├── scc_secondary_control.py       # Secondary Control
└── README.md                      # Documentation
```

## Dependencies

```python
# Required imports
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
from gui.control_center.control_center_api_client import ControlCenterAPIClient
```

## Version Info

- **Python**: 3.8+
- **PyQt6**: 6.6.0+
- **Architecture**: Signal/Slot based
- **Theme**: Dark theme by default
- **Updates**: Automatic with configurable intervals

## Support

For issues or questions:
1. Check module README.md
2. Review code comments
3. Check API client documentation
4. Review Qt6 documentation

## License

Part of KSE (Klar Search Engine) project
