"""
Example Usage of GUI Widgets, Dialogs, and Components
Demonstrates how to use the reusable KSE GUI components
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import QTimer

# Import widgets
from gui.control_center.widgets import (
    StatusTile, ChartWidget, GaugeWidget, MetricCard,
    LogViewer, TableWidget, TimelineWidget, ProgressWidget,
    NotificationWidget, NotificationContainer, StatusIndicator
)

# Import dialogs
from gui.control_center.dialogs import (
    DomainSelectionDialog, SettingsDialog, ExportDialog, ImportDialog,
    ConfirmationDialog, AboutDialog, ErrorDialog, SnapshotDialog
)

# Import components
from gui.components import MenuBar, StatusBar, ToolBar, SideBar

# Import config
from gui.kse_gui_config import GUIConfig


class ExampleWindow(QMainWindow):
    """Example window demonstrating all components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KSE GUI Components Example")
        self.resize(1400, 900)
        
        # Apply theme
        self.setStyleSheet(GUIConfig.get_default_stylesheet())
        
        self._setup_ui()
        self._setup_demo_data()
    
    def _setup_ui(self):
        """Setup the UI"""
        # Menu Bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.menu_action_triggered.connect(self._handle_menu_action)
        
        # Toolbar
        self.toolbar = ToolBar("Main Toolbar", self)
        self.addToolBar(self.toolbar)
        self.toolbar.action_triggered.connect(self._handle_toolbar_action)
        self.toolbar.search_requested.connect(self._handle_search)
        
        # Status Bar
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.set_status("Ready")
        self.status_bar.set_connection_status("online")
        self.status_bar.set_system_status("running")
        
        # Main layout with sidebar
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = SideBar(width=250, collapsible=True)
        self._setup_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)
        
        # Add example widgets
        self._add_status_tiles(content_layout)
        self._add_metric_cards(content_layout)
        self._add_chart_and_gauge(content_layout)
        self._add_progress_and_timeline(content_layout)
        self._add_table_and_logs(content_layout)
        self._add_action_buttons(content_layout)
        
        main_layout.addWidget(content_widget, 1)
        
        # Notification container (overlay)
        self.notifications = NotificationContainer()
        content_layout.insertLayout(0, self.notifications)
    
    def _setup_sidebar(self):
        """Setup sidebar navigation"""
        # Add sections
        dashboard_section = self.sidebar.add_section("dashboard", "Dashboard")
        self.sidebar.add_item("dashboard", "overview", "Overview")
        self.sidebar.add_item("dashboard", "analytics", "Analytics")
        
        modules_section = self.sidebar.add_section("modules", "Modules")
        self.sidebar.add_item("modules", "mcs", "Main Control")
        self.sidebar.add_item("modules", "pcc", "Primary Control")
        self.sidebar.add_item("modules", "scs", "System Status")
        
        tools_section = self.sidebar.add_section("tools", "Tools")
        self.sidebar.add_item("tools", "logs", "Logs")
        self.sidebar.add_item("tools", "settings", "Settings")
        
        self.sidebar.select_item("overview")
    
    def _add_status_tiles(self, layout):
        """Add status tiles row"""
        tiles_layout = QHBoxLayout()
        
        self.cpu_tile = StatusTile("CPU Usage", unit="%", threshold=80)
        self.cpu_tile.set_value(45.5)
        tiles_layout.addWidget(self.cpu_tile)
        
        self.ram_tile = StatusTile("RAM Usage", unit="%", threshold=85)
        self.ram_tile.set_value(62.3)
        tiles_layout.addWidget(self.ram_tile)
        
        self.disk_tile = StatusTile("Disk Usage", unit="%", threshold=90)
        self.disk_tile.set_value(38.7)
        tiles_layout.addWidget(self.disk_tile)
        
        self.network_tile = StatusTile("Network", unit=" Mbps", threshold=100)
        self.network_tile.set_value(23.4)
        tiles_layout.addWidget(self.network_tile)
        
        layout.addLayout(tiles_layout)
    
    def _add_metric_cards(self, layout):
        """Add metric cards row"""
        cards_layout = QHBoxLayout()
        
        self.users_card = MetricCard("Active Users", "1,234")
        self.users_card.set_trend(12.5)
        cards_layout.addWidget(self.users_card)
        
        self.requests_card = MetricCard("Requests", "45.6K", "/sec")
        self.requests_card.set_trend(-3.2)
        cards_layout.addWidget(self.requests_card)
        
        self.domains_card = MetricCard("Domains", "89")
        self.domains_card.set_trend(5.0)
        cards_layout.addWidget(self.domains_card)
        
        self.uptime_card = MetricCard("Uptime", "99.9", "%")
        self.uptime_card.set_trend(0.1)
        cards_layout.addWidget(self.uptime_card)
        
        cards_layout.addStretch()
        layout.addLayout(cards_layout)
    
    def _add_chart_and_gauge(self, layout):
        """Add chart and gauge"""
        row_layout = QHBoxLayout()
        
        # Chart
        self.chart = ChartWidget("System Performance", chart_type='line', max_points=20)
        self.chart.set_data([30, 45, 38, 52, 60, 55, 48, 62, 58, 65])
        row_layout.addWidget(self.chart)
        
        # Gauge
        self.gauge = GaugeWidget("CPU Load", min_value=0, max_value=100, threshold=75)
        self.gauge.set_value(45.5)
        row_layout.addWidget(self.gauge)
        
        layout.addLayout(row_layout)
    
    def _add_progress_and_timeline(self, layout):
        """Add progress and timeline"""
        row_layout = QHBoxLayout()
        
        # Progress
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        
        self.progress1 = ProgressWidget("Task Progress", show_percentage=True)
        self.progress1.set_progress(65, "Processing data...")
        progress_layout.addWidget(self.progress1)
        
        self.progress2 = ProgressWidget("Upload", show_percentage=True)
        self.progress2.set_progress(30, "Uploading files...")
        progress_layout.addWidget(self.progress2)
        
        row_layout.addWidget(progress_widget)
        
        # Timeline
        self.timeline = TimelineWidget()
        self.timeline.add_event("System Started", "Control center initialized", event_type="success")
        self.timeline.add_event("Configuration Loaded", "Settings applied", event_type="info")
        self.timeline.add_event("Warning Detected", "High memory usage", event_type="warning")
        row_layout.addWidget(self.timeline)
        
        layout.addLayout(row_layout)
    
    def _add_table_and_logs(self, layout):
        """Add table and logs"""
        row_layout = QHBoxLayout()
        
        # Table
        self.table = TableWidget(
            headers=["Domain", "Status", "Requests", "Last Update"],
            sortable=True,
            searchable=True
        )
        self.table.add_rows([
            ["example.com", "Active", "1,234", "2024-01-15 10:30"],
            ["test.org", "Active", "567", "2024-01-15 10:29"],
            ["demo.net", "Inactive", "0", "2024-01-15 08:15"],
        ])
        row_layout.addWidget(self.table)
        
        # Logs
        self.log_viewer = LogViewer(max_lines=100, auto_scroll=True)
        self.log_viewer.add_log("System initialized", "INFO")
        self.log_viewer.add_log("Configuration loaded successfully", "INFO")
        self.log_viewer.add_log("Connected to database", "INFO")
        self.log_viewer.add_log("High memory usage detected", "WARNING")
        row_layout.addWidget(self.log_viewer)
        
        layout.addLayout(row_layout)
    
    def _add_action_buttons(self, layout):
        """Add action buttons for testing dialogs"""
        buttons_layout = QHBoxLayout()
        
        btn_domains = QPushButton("Select Domains")
        btn_domains.clicked.connect(self._show_domain_dialog)
        buttons_layout.addWidget(btn_domains)
        
        btn_settings = QPushButton("Settings")
        btn_settings.clicked.connect(self._show_settings_dialog)
        buttons_layout.addWidget(btn_settings)
        
        btn_export = QPushButton("Export")
        btn_export.clicked.connect(self._show_export_dialog)
        buttons_layout.addWidget(btn_export)
        
        btn_import = QPushButton("Import")
        btn_import.clicked.connect(self._show_import_dialog)
        buttons_layout.addWidget(btn_import)
        
        btn_confirm = QPushButton("Confirm Action")
        btn_confirm.clicked.connect(self._show_confirmation_dialog)
        buttons_layout.addWidget(btn_confirm)
        
        btn_error = QPushButton("Show Error")
        btn_error.clicked.connect(self._show_error_dialog)
        buttons_layout.addWidget(btn_error)
        
        btn_about = QPushButton("About")
        btn_about.clicked.connect(self._show_about_dialog)
        buttons_layout.addWidget(btn_about)
        
        btn_snapshot = QPushButton("Snapshots")
        btn_snapshot.clicked.connect(self._show_snapshot_dialog)
        buttons_layout.addWidget(btn_snapshot)
        
        btn_notification = QPushButton("Show Notification")
        btn_notification.clicked.connect(self._show_notification)
        buttons_layout.addWidget(btn_notification)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
    
    def _setup_demo_data(self):
        """Setup demo data updates"""
        # Update metrics periodically
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_metrics)
        self.update_timer.start(2000)  # Every 2 seconds
    
    def _update_metrics(self):
        """Update metrics with random data"""
        import random
        
        # Update tiles
        self.cpu_tile.set_value(random.uniform(20, 80))
        self.ram_tile.set_value(random.uniform(40, 90))
        
        # Add chart data
        self.chart.add_data_point(random.uniform(30, 70))
        
        # Update gauge
        self.gauge.set_value(random.uniform(30, 80))
    
    def _handle_menu_action(self, action: str):
        """Handle menu action"""
        self.status_bar.show_info(f"Menu action: {action}")
        
        if action == "about":
            self._show_about_dialog()
        elif action == "settings":
            self._show_settings_dialog()
        elif action == "export":
            self._show_export_dialog()
        elif action == "import":
            self._show_import_dialog()
    
    def _handle_toolbar_action(self, action: str):
        """Handle toolbar action"""
        self.status_bar.show_info(f"Toolbar action: {action}")
    
    def _handle_search(self, text: str):
        """Handle search"""
        self.status_bar.show_info(f"Searching for: {text}")
    
    def _show_domain_dialog(self):
        """Show domain selection dialog"""
        domains = DomainSelectionDialog.get_domains(
            available_domains=["example.com", "test.org", "demo.net", "sample.io"],
            selected_domains=["example.com"],
            parent=self
        )
        if domains:
            self.status_bar.show_success(f"Selected {len(domains)} domains")
    
    def _show_settings_dialog(self):
        """Show settings dialog"""
        settings = SettingsDialog.get_settings_from_dialog(parent=self)
        if settings:
            self.status_bar.show_success("Settings saved")
    
    def _show_export_dialog(self):
        """Show export dialog"""
        dialog = ExportDialog(
            data=[{"name": "Test", "value": 123}],
            default_filename="export",
            parent=self
        )
        dialog.exec()
    
    def _show_import_dialog(self):
        """Show import dialog"""
        data = ImportDialog.import_data(parent=self)
        if data:
            self.status_bar.show_success("Data imported successfully")
    
    def _show_confirmation_dialog(self):
        """Show confirmation dialog"""
        confirmed = ConfirmationDialog.confirm(
            "Are you sure you want to proceed?",
            "Confirm Action",
            parent=self
        )
        if confirmed:
            self.status_bar.show_success("Action confirmed")
    
    def _show_error_dialog(self):
        """Show error dialog"""
        ErrorDialog.show_error(
            "Operation Failed",
            "An error occurred while processing your request.",
            "Traceback:\n  File example.py, line 123\n    raise Exception('Test error')",
            parent=self
        )
    
    def _show_about_dialog(self):
        """Show about dialog"""
        AboutDialog.show_about(
            app_name="KSE Control Center",
            version="1.0.0",
            description="Knowledge Search Engine Control Center",
            parent=self
        )
    
    def _show_snapshot_dialog(self):
        """Show snapshot dialog"""
        snapshots = [
            {
                'id': '20240115101500',
                'name': 'Before Update',
                'description': 'System snapshot before major update',
                'timestamp': '2024-01-15 10:15:00',
                'data': {}
            }
        ]
        SnapshotDialog.manage_snapshots(snapshots, parent=self)
    
    def _show_notification(self):
        """Show notification"""
        import random
        types = ['info', 'success', 'warning', 'error']
        messages = [
            ("Task Completed", "Your task has been completed successfully"),
            ("New Message", "You have a new message"),
            ("Warning", "System resources running low"),
            ("Error", "Failed to connect to server"),
        ]
        
        msg_type = random.choice(types)
        title, message = random.choice(messages)
        
        self.notifications.add_notification(
            title=title,
            message=message,
            notification_type=msg_type
        )


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
