# Control Center Quick Reference

## Files Created

```
gui/control_center/
├── __init__.py                      # Package initialization (lazy imports)
├── control_center_config.py         # Configuration (6.9 KB)
├── control_center_api_client.py     # API client (11 KB)
├── control_center_navigation.py     # Tab navigation (9 KB)
└── control_center_main.py           # Main window (18 KB)
```

## Quick Start

### Run Control Center
```bash
python gui/control_center/control_center_main.py
```

### Import in Code
```python
from gui.control_center import ControlCenterMain
from PyQt6.QtWidgets import QApplication

app = QApplication([])
window = ControlCenterMain()
window.show()
app.exec()
```

## Module Shortcuts

| Shortcut | Module | Purpose |
|----------|--------|---------|
| Ctrl+1 | PCC | Performance & Control |
| Ctrl+2 | MCS | Monitoring & Cache |
| Ctrl+3 | SCS | Statistics & Charts |
| Ctrl+4 | ACC | Analytics & Config |
| Ctrl+5 | SCC | System & Crawler |

## Menu Shortcuts

| Shortcut | Action |
|----------|--------|
| F5 | Refresh current module |
| F11 | Toggle fullscreen |
| F1 | Help documentation |
| Ctrl+, | Settings |
| Ctrl+Q | Quit application |

## Key Classes

### ControlCenterConfig
```python
# Get module configuration
config = ControlCenterConfig.get_module_config('pcc')

# Get API endpoint URL
url = ControlCenterConfig.get_api_endpoint('health')

# Get update interval
interval = ControlCenterConfig.get_update_interval('pcc')

# Save/load configuration
ControlCenterConfig.save_config(config_dict)
config = ControlCenterConfig.load_config()
```

### ControlCenterAPIClient
```python
from gui.control_center import ControlCenterAPIClient

client = ControlCenterAPIClient()

# Connect signals
client.connection_status_changed.connect(on_status_changed)
client.health_check_completed.connect(on_health_check)

# Start monitoring
client.start_health_monitoring()

# API calls
client.check_health()
client.get_stats()
client.search("query", max_results=10)
client.clear_cache()
```

### ControlCenterNavigation
```python
from gui.control_center import ControlCenterNavigation

nav = ControlCenterNavigation()

# Add modules
nav.add_module('pcc', widget)

# Set active module
nav.set_active_module('mcs')

# Get current module
module_id = nav.get_current_module_id()

# Connect signals
nav.module_changed.connect(on_module_changed)
nav.module_refresh_requested.connect(on_refresh)
```

### ControlCenterMain
```python
from gui.control_center import ControlCenterMain

window = ControlCenterMain()

# Access components
window.api_client  # API client instance
window.navigation  # Navigation widget
window.modules     # Dictionary of module widgets

# Connect signals
window.closing.connect(on_closing)
```

## Configuration

### Module Definition Structure
```python
{
    'id': 'pcc',
    'name': 'Performance & Control',
    'title': 'Performance & Control Center',
    'icon': 'performance',
    'description': 'Real-time performance metrics',
    'tooltip': 'Monitor system performance',
    'shortcut': 'Ctrl+1',
    'color': '#2196F3',
}
```

### API Endpoints
```python
API_ENDPOINTS = {
    'health': '/api/health',
    'stats': '/api/stats',
    'search': '/api/search',
    'history': '/api/history',
    'cache_stats': '/api/cache/stats',
    'cache_clear': '/api/cache/clear',
    'ranking_weights': '/api/ranking/weights',
    'monitoring_status': '/api/monitoring/status',
}
```

### Update Intervals
```python
UPDATE_INTERVALS = {
    'status_bar': 2000,   # 2 seconds
    'pcc': 5000,          # 5 seconds
    'mcs': 5000,          # 5 seconds
    'scs': 10000,         # 10 seconds
    'acc': 30000,         # 30 seconds
    'scc': 15000,         # 15 seconds
}
```

## Signals & Slots

### API Client Signals
```python
connection_status_changed(str)  # 'connected', 'disconnected', 'error'
health_check_completed(dict)    # Health check response
stats_received(dict)            # Statistics data
search_completed(dict)          # Search results
error_occurred(str)             # Error message
```

### Navigation Signals
```python
module_changed(str)             # Module ID
module_refresh_requested(str)   # Module ID to refresh
```

### Main Window Signals
```python
closing()                       # Window closing event
```

## Testing

### Run Validation
```bash
python validate_control_center.py
```

### Run Tests
```bash
python test_control_center.py
```

## Common Tasks

### Add a New Module
```python
# 1. Define in control_center_config.py
MODULES = {
    'new_module': {
        'id': 'new_module',
        'name': 'New Module',
        # ... other config
    }
}

# 2. Create widget
from PyQt6.QtWidgets import QWidget
widget = QWidget()

# 3. Add to navigation
navigation.add_module('new_module', widget)
```

### Make API Call
```python
# Define callback
def on_stats_received(data):
    print(f"Stats: {data}")

# Make request
client.get_stats()

# Or with custom endpoint
client._make_request('/api/custom', callback=on_stats_received)
```

### Handle Module Changes
```python
def on_module_changed(module_id):
    print(f"Switched to: {module_id}")
    # Update UI, fetch data, etc.

navigation.module_changed.connect(on_module_changed)
```

## File Sizes

- `control_center_config.py`: 6.9 KB
- `control_center_api_client.py`: 11 KB
- `control_center_navigation.py`: 9 KB
- `control_center_main.py`: 18 KB
- **Total**: ~45 KB

## Dependencies

- PyQt6 >= 6.6.0
- Python >= 3.8
- gui.kse_gui_config
- gui.kse_gui_styles

## Status

✅ Implementation complete
✅ All tests passing
✅ Code review addressed
✅ Security scanning passed
✅ Documentation complete

**Ready for production use!**
