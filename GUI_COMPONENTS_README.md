# KSE GUI Components Documentation

This document provides an overview and usage guide for the reusable GUI components implemented for the Knowledge Search Engine (KSE) application.

## Overview

The KSE GUI framework consists of 22 production-ready components organized into three categories:
- **10 Widgets**: Reusable UI widgets for data display and interaction
- **8 Dialogs**: Modal dialogs for user interactions
- **4 Components**: Application-level components (menu bar, toolbar, status bar, sidebar)

All components follow these principles:
- **Consistent theming** using `GUIConfig` and `Styles`
- **Signal-based communication** using PyQt6 signals
- **Type hints** for better IDE support
- **Comprehensive logging** for debugging
- **Thread-safe operations**
- **Professional dark theme** styling

## Installation

Ensure you have PyQt6 installed:

```bash
pip install PyQt6
```

## Components

### Widgets (gui/control_center/widgets/)

#### 1. StatusTile
Displays system metrics in a tile format with progress bar and status indicator.

```python
from gui.control_center.widgets import StatusTile

tile = StatusTile(title="CPU Usage", unit="%", threshold=80)
tile.set_value(65.5)
tile.value_changed.connect(lambda v: print(f"Value: {v}"))
```

**Features:**
- Configurable threshold with color-coded status
- Progress bar visualization
- Emits signals on value change and threshold exceeded

#### 2. ChartWidget
Live charts supporting line, bar, and pie chart types.

```python
from gui.control_center.widgets import ChartWidget

chart = ChartWidget(title="Performance", chart_type='line', max_points=50)
chart.add_data_point(45.3)
chart.set_data([10, 20, 30, 40, 50])
```

**Features:**
- Three chart types: line, bar, pie
- Real-time data updates
- Configurable colors and max data points

#### 3. GaugeWidget
Circular gauge display for percentage values.

```python
from gui.control_center.widgets import GaugeWidget

gauge = GaugeWidget(title="Load", min_value=0, max_value=100, threshold=80)
gauge.set_value(65.0)
```

**Features:**
- Circular gauge with color-coded ranges
- Min/max labels
- Threshold-based color changes

#### 4. MetricCard
Compact metric display card with trend indicator.

```python
from gui.control_center.widgets import MetricCard

card = MetricCard(label="Active Users", value="1,234", unit="users")
card.set_trend(12.5)  # +12.5%
card.card_clicked.connect(lambda: print("Card clicked"))
```

**Features:**
- Value with optional unit
- Trend indicator (up/down arrows with percentage)
- Clickable with signals

#### 5. LogViewer
Scrollable log viewer with filtering and search.

```python
from gui.control_center.widgets import LogViewer

log_viewer = LogViewer(max_lines=1000, auto_scroll=True, show_timestamps=True)
log_viewer.add_log("Application started", "INFO")
log_viewer.add_log("Configuration loaded", "DEBUG")
log_viewer.export_logs("output.log")
```

**Features:**
- Color-coded log levels
- Search and filter capabilities
- Auto-scroll option
- Export to file

#### 6. TableWidget
Enhanced sortable table with search.

```python
from gui.control_center.widgets import TableWidget

table = TableWidget(headers=["Name", "Status", "Count"], sortable=True, searchable=True)
table.add_row(["Domain 1", "Active", "100"])
table.add_rows([...])
table.export_to_csv("data.csv")
```

**Features:**
- Sortable columns
- Search/filter functionality
- Row selection signals
- CSV export

#### 7. TimelineWidget
Event timeline display with color-coded events.

```python
from gui.control_center.widgets import TimelineWidget

timeline = TimelineWidget()
timeline.add_event("System Started", "Initialization complete", event_type="success")
timeline.add_event("Warning", "High memory usage", event_type="warning")
```

**Features:**
- Chronological event display
- Color-coded event types (info, success, warning, error)
- Clickable events
- Filter by event type

#### 8. ProgressWidget
Progress bar with percentage and status text.

```python
from gui.control_center.widgets import ProgressWidget

progress = ProgressWidget(title="Processing", show_percentage=True, show_status=True)
progress.set_progress(50, "Processing data...")
progress.increment(10)
progress.complete()
```

**Features:**
- Percentage display
- Status text
- Indeterminate mode
- Color changes based on progress

#### 9. NotificationWidget
Alert/notification display with auto-dismiss.

```python
from gui.control_center.widgets import NotificationWidget, NotificationContainer

# Single notification
notif = NotificationWidget("Success", "Operation completed", notification_type='success')

# Container for managing multiple notifications
container = NotificationContainer(max_notifications=5)
container.add_notification("Error", "Failed to connect", notification_type='error')
```

**Features:**
- Auto-dismiss with timeout
- Action button support
- Multiple notification types
- Slide-in animation

#### 10. StatusIndicator
Live status indicator with pulsing animation.

```python
from gui.control_center.widgets import StatusIndicator

indicator = StatusIndicator(label="Connection", initial_status='online', pulsing=True)
indicator.set_status('offline')
```

**Features:**
- Color-coded status (green/yellow/red/gray)
- Pulsing animation option
- Status label
- Status badge variant

### Dialogs (gui/control_center/dialogs/)

#### 1. DomainSelectionDialog
Multi-select domain picker with search.

```python
from gui.control_center.dialogs import DomainSelectionDialog

domains = DomainSelectionDialog.get_domains(
    available_domains=["example.com", "test.org"],
    selected_domains=["example.com"],
    allow_multi_select=True
)
```

**Features:**
- Search/filter domains
- Select all/clear all
- Multi or single selection

#### 2. SettingsDialog
Comprehensive settings dialog with tabs.

```python
from gui.control_center.dialogs import SettingsDialog

settings = SettingsDialog.get_settings_from_dialog(
    current_settings={'theme': 'dark', 'font_size': 10}
)
```

**Features:**
- Tabbed interface (General, Appearance, Network, Advanced)
- All common settings
- Reset to defaults

#### 3. ExportDialog
Data export with multiple format support.

```python
from gui.control_center.dialogs import ExportDialog

dialog = ExportDialog(
    data=[{"name": "Test", "value": 123}],
    default_filename="export"
)
dialog.exec()
```

**Features:**
- CSV, JSON, XML, TEXT formats
- Preview before export
- Open file after export option

#### 4. ImportDialog
Data import with validation.

```python
from gui.control_center.dialogs import ImportDialog

data = ImportDialog.import_data(
    allowed_formats=['CSV', 'JSON']
)
```

**Features:**
- Multiple format support
- Preview before import
- Data validation
- Header detection for CSV

#### 5. ConfirmationDialog
Flexible confirmation prompts.

```python
from gui.control_center.dialogs import ConfirmationDialog

# Simple confirmation
confirmed = ConfirmationDialog.confirm("Are you sure?", "Confirm")

# Warning confirmation
confirmed = ConfirmationDialog.warn("This will delete data", "Warning")

# Danger confirmation
confirmed = ConfirmationDialog.danger("Delete permanently?", "Confirm Delete", "Delete")
```

**Features:**
- Multiple dialog types (question, warning, danger, info)
- "Don't ask again" checkbox option
- Custom button text

#### 6. AboutDialog
Application about/help dialog.

```python
from gui.control_center.dialogs import AboutDialog

AboutDialog.show_about(
    app_name="KSE Control Center",
    version="1.0.0",
    description="Knowledge Search Engine"
)
```

**Features:**
- About, System Info, License, Credits tabs
- System information display
- Links support

#### 7. ErrorDialog
Error display with collapsible details.

```python
from gui.control_center.dialogs import ErrorDialog

# Show error with details
ErrorDialog.show_error("Operation Failed", "Error message", details="Stack trace...")

# From exception
try:
    raise ValueError("Test error")
except Exception as e:
    ErrorDialog.from_exception(e, "An Error Occurred")
```

**Features:**
- Collapsible details section
- Copy to clipboard
- Multiple severity levels

#### 8. SnapshotDialog
Snapshot management for system states.

```python
from gui.control_center.dialogs import SnapshotDialog

snapshots = SnapshotDialog.manage_snapshots(
    snapshots=[...]
)
```

**Features:**
- Create, load, delete snapshots
- Snapshot metadata display
- Confirmation prompts

### Components (gui/components/)

#### 1. MenuBar
Application menu bar with standard menus.

```python
from gui.components import MenuBar

menu_bar = MenuBar(self)
self.setMenuBar(menu_bar)
menu_bar.menu_action_triggered.connect(self.handle_menu_action)
menu_bar.set_action_enabled('save', False)
```

**Features:**
- File, Edit, View, Tools, Help menus
- Keyboard shortcuts
- Enable/disable actions

#### 2. StatusBar
Status bar with live updates and indicators.

```python
from gui.components import StatusBar

status_bar = StatusBar(self)
self.setStatusBar(status_bar)
status_bar.set_status("Ready")
status_bar.show_success("Operation completed")
status_bar.set_connection_status("online")
status_bar.set_progress(50)
```

**Features:**
- Status messages with timeout
- Color-coded messages
- Progress bar
- Status indicators
- Custom indicators

#### 3. ToolBar
Quick action toolbar.

```python
from gui.components import ToolBar

toolbar = ToolBar("Main Toolbar", self)
self.addToolBar(toolbar)
toolbar.action_triggered.connect(self.handle_action)
toolbar.search_requested.connect(self.handle_search)
toolbar.add_action_button("Custom", "custom_action", "Custom action")
```

**Features:**
- Standard actions (New, Open, Save, etc.)
- Search box
- Custom actions
- Toggle buttons
- Custom widgets

#### 4. SideBar
Collapsible navigation sidebar.

```python
from gui.components import SideBar

sidebar = SideBar(width=250, collapsible=True)
section = sidebar.add_section("main", "Main Section")
sidebar.add_item("main", "overview", "Overview")
sidebar.item_selected.connect(self.handle_navigation)
```

**Features:**
- Collapsible sections
- Navigation items
- Collapse sidebar
- Custom width

## Example Usage

See `example_widgets_usage.py` for a comprehensive example demonstrating all components:

```bash
python example_widgets_usage.py
```

This example includes:
- All widgets in action with live updates
- Dialog demonstrations
- Menu bar, toolbar, status bar, and sidebar integration
- Proper signal connections
- Theme application

## Theming

All components use the centralized theming system:

```python
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles

# Apply theme to application
app.setStyleSheet(GUIConfig.get_default_stylesheet())

# Get colors
primary_color = GUIConfig.get_color('primary')
success_color = GUIConfig.COLORS['success']

# Get styles
button_style = Styles.get_button_style()
card_style = Styles.get_card_style()
```

## Best Practices

1. **Use signals for communication**: Connect to widget signals instead of polling
2. **Handle errors gracefully**: All components have error handling, but wrap critical operations
3. **Respect threading**: Update UI from main thread only
4. **Use layouts**: Don't set fixed sizes unless necessary
5. **Clean up resources**: Disconnect signals and stop timers when widgets are destroyed

## Common Patterns

### Creating a Dashboard

```python
from gui.control_center.widgets import StatusTile, MetricCard, ChartWidget

# Create tiles
cpu_tile = StatusTile("CPU", unit="%", threshold=80)
ram_tile = StatusTile("RAM", unit="%", threshold=85)

# Create metric cards
users_card = MetricCard("Users", "1,234")
users_card.set_trend(5.2)

# Create chart
chart = ChartWidget("Performance", chart_type='line')
```

### Showing Notifications

```python
from gui.control_center.widgets import NotificationContainer

notifications = NotificationContainer()
layout.addLayout(notifications)

# Show notifications
notifications.add_notification("Success", "Data saved", notification_type='success')
notifications.add_notification("Error", "Connection failed", notification_type='error')
```

### Using Dialogs

```python
# Confirmation
from gui.control_center.dialogs import ConfirmationDialog
if ConfirmationDialog.confirm("Delete this item?", "Confirm"):
    # Delete item
    pass

# Error
from gui.control_center.dialogs import ErrorDialog
try:
    # Operation
    pass
except Exception as e:
    ErrorDialog.from_exception(e, "Operation Failed")
```

## Testing

Basic smoke test:

```python
python -c "from gui.control_center.widgets import *; from gui.control_center.dialogs import *; from gui.components import *; print('All imports successful')"
```

Run the example:

```bash
python example_widgets_usage.py
```

## Architecture

```
gui/
├── kse_gui_config.py          # Configuration and theming
├── kse_gui_styles.py          # Reusable style definitions
├── components/                # Application-level components
│   ├── __init__.py
│   ├── menubar.py
│   ├── statusbar.py
│   ├── toolbar.py
│   └── sidebar.py
└── control_center/
    ├── widgets/               # Reusable widgets
    │   ├── __init__.py
    │   ├── status_tile.py
    │   ├── chart_widget.py
    │   ├── gauge_widget.py
    │   ├── metric_card.py
    │   ├── log_viewer.py
    │   ├── table_widget.py
    │   ├── timeline_widget.py
    │   ├── progress_widget.py
    │   ├── notification_widget.py
    │   └── status_indicator.py
    └── dialogs/               # Modal dialogs
        ├── __init__.py
        ├── domain_selection_dialog.py
        ├── settings_dialog.py
        ├── export_dialog.py
        ├── import_dialog.py
        ├── confirmation_dialog.py
        ├── about_dialog.py
        ├── error_dialog.py
        └── snapshot_dialog.py
```

## Contributing

When adding new components:
1. Follow the existing patterns
2. Use GUIConfig and Styles for theming
3. Implement proper signals
4. Add type hints
5. Include documentation
6. Add to __init__.py
7. Update this README

## License

MIT License - See LICENSE file for details
