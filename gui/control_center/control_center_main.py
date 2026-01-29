"""
Control Center Main Window
Main window for KSE Control Center with tab-based module navigation
"""

import logging
import sys
from typing import Optional, Dict
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QStatusBar, QMenuBar, QMenu, QToolBar, QPushButton,
    QMessageBox, QDialog, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
from gui.control_center.control_center_config import ControlCenterConfig
from gui.control_center.control_center_navigation import ControlCenterNavigation
from gui.control_center.control_center_api_client import ControlCenterAPIClient

logger = logging.getLogger(__name__)


class ControlCenterMain(QMainWindow):
    """Main Control Center window"""
    
    # Signals
    closing = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # API client
        self.api_client = ControlCenterAPIClient()
        
        # Module instances (to be populated)
        self.modules = {}
        
        # Server status
        self.server_connected = False
        self.server_health = {}
        
        # Setup window
        self._setup_window()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._setup_navigation()
        self._load_modules()
        self._setup_connections()
        self._load_window_state()
        
        # Start monitoring
        self.api_client.start_health_monitoring()
        
        logger.info("Control Center initialized")
    
    def _setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle(ControlCenterConfig.WINDOW_TITLE)
        self.setMinimumSize(
            ControlCenterConfig.MIN_WIDTH,
            ControlCenterConfig.MIN_HEIGHT
        )
        self.resize(
            ControlCenterConfig.WINDOW_WIDTH,
            ControlCenterConfig.WINDOW_HEIGHT
        )
        
        # Set window icon
        icon_path = GUIConfig.get_icon_path('app_icon')
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Apply stylesheet
        self.setStyleSheet(GUIConfig.get_default_stylesheet())
        
        # Center window
        self._center_window()
    
    def _center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self._refresh_current_module)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        fullscreen_action = QAction("&Full Screen", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        view_menu.addSeparator()
        
        # Module quick access
        for module_id, config in ControlCenterConfig.MODULES.items():
            action = QAction(config['name'], self)
            shortcut = config.get('shortcut')
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(
                lambda checked, mid=module_id: self.navigation.set_active_module(mid)
            )
            view_menu.addAction(action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        clear_cache_action = QAction("Clear &Cache", self)
        clear_cache_action.triggered.connect(self._clear_cache)
        tools_menu.addAction(clear_cache_action)
        
        test_connection_action = QAction("&Test Connection", self)
        test_connection_action.triggered.connect(self._test_connection)
        tools_menu.addAction(test_connection_action)
        
        tools_menu.addSeparator()
        
        logs_action = QAction("View &Logs", self)
        logs_action.triggered.connect(self._view_logs)
        tools_menu.addAction(logs_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut(QKeySequence("F1"))
        docs_action.triggered.connect(self._show_documentation)
        help_menu.addAction(docs_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Create toolbar with quick actions"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        
        # Refresh button
        refresh_btn = QAction("Refresh", self)
        refresh_btn.setToolTip("Refresh current module (F5)")
        refresh_btn.triggered.connect(self._refresh_current_module)
        toolbar.addAction(refresh_btn)
        
        toolbar.addSeparator()
        
        # Connection status button
        self.connection_btn = QAction("Check Connection", self)
        self.connection_btn.setToolTip("Test server connection")
        self.connection_btn.triggered.connect(self._test_connection)
        toolbar.addAction(self.connection_btn)
        
        toolbar.addSeparator()
        
        # Clear cache button
        clear_cache_btn = QAction("Clear Cache", self)
        clear_cache_btn.setToolTip("Clear search cache")
        clear_cache_btn.triggered.connect(self._clear_cache)
        toolbar.addAction(clear_cache_btn)
        
        toolbar.addSeparator()
        
        # Settings button
        settings_btn = QAction("Settings", self)
        settings_btn.setToolTip("Open settings")
        settings_btn.triggered.connect(self._show_settings)
        toolbar.addAction(settings_btn)
        
        # Apply toolbar style
        toolbar.setStyleSheet(Styles.get_toolbar_style())
        
        self.addToolBar(toolbar)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connection status label
        self.connection_status_label = QLabel("Disconnected")
        self.connection_status_label.setStyleSheet(
            Styles.get_status_label_style('error')
        )
        self.status_bar.addPermanentWidget(self.connection_status_label)
        
        # Server health label
        self.health_status_label = QLabel("Health: Unknown")
        self.status_bar.addPermanentWidget(self.health_status_label)
        
        # Active module label
        self.module_status_label = QLabel("Module: None")
        self.status_bar.addWidget(self.module_status_label)
        
        # Update timer for status bar
        self.status_timer = QTimer()
        self.status_timer.setInterval(ControlCenterConfig.UPDATE_INTERVALS['status_bar'])
        self.status_timer.timeout.connect(self._update_status_bar)
        self.status_timer.start()
    
    def _setup_navigation(self):
        """Setup navigation widget"""
        self.navigation = ControlCenterNavigation()
        self.setCentralWidget(self.navigation)
        
        # Connect navigation signals
        self.navigation.module_changed.connect(self._on_module_changed)
        self.navigation.module_refresh_requested.connect(self._on_module_refresh)
    
    def _load_modules(self):
        """Load and initialize all modules"""
        logger.info("Loading modules...")
        
        # Import actual module implementations
        try:
            from gui.control_center.modules import (
                PCCPrimaryControl,
                MCSMainControlServer,
                SCSSystemStatus,
                ACCAuxiliaryControl,
                SCCSecondaryControl
            )
            
            # Module mapping
            module_classes = {
                'pcc': PCCPrimaryControl,
                'mcs': MCSMainControlServer,
                'scs': SCSSystemStatus,
                'acc': ACCAuxiliaryControl,
                'scc': SCCSecondaryControl,
            }
            
            # Instantiate each module
            for module_id, module_class in module_classes.items():
                try:
                    widget = module_class(self.api_client)
                    self.navigation.add_module(module_id, widget)
                    self.modules[module_id] = widget
                    logger.info(f"Module loaded: {module_id}")
                except Exception as e:
                    logger.error(f"Error loading module {module_id}: {e}")
                    # Fallback to placeholder
                    widget = self._create_module_placeholder(module_id)
                    self.navigation.add_module(module_id, widget)
                    self.modules[module_id] = widget
            
        except ImportError as e:
            logger.error(f"Failed to import modules: {e}")
            # Fallback to placeholders
            for module_id in ControlCenterConfig.get_module_list():
                try:
                    widget = self._create_module_placeholder(module_id)
                    self.navigation.add_module(module_id, widget)
                    self.modules[module_id] = widget
                    logger.info(f"Placeholder loaded: {module_id}")
                except Exception as e:
                    logger.error(f"Error loading placeholder {module_id}: {e}")
        
        # Set initial module
        self.navigation.set_active_module('pcc')
    
    def _create_module_placeholder(self, module_id: str) -> QWidget:
        """Create placeholder widget for module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        config = ControlCenterConfig.get_module_config(module_id)
        
        # Title
        title = QLabel(config.get('title', 'Module'))
        title.setStyleSheet(Styles.get_title_style('header'))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(config.get('description', 'No description'))
        desc.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addStretch()
        
        # Placeholder message
        placeholder = QLabel("Module implementation coming soon...")
        placeholder.setStyleSheet(f"""
            color: {GUIConfig.COLORS['text_secondary']};
            font-size: 14pt;
            padding: 20px;
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        
        layout.addStretch()
        
        return widget
    
    def _setup_connections(self):
        """Setup signal connections"""
        # API client signals
        self.api_client.connection_status_changed.connect(self._on_connection_status_changed)
        self.api_client.health_check_completed.connect(self._on_health_check)
        self.api_client.error_occurred.connect(self._on_api_error)
    
    def _on_connection_status_changed(self, status: str):
        """Handle connection status change"""
        self.server_connected = (status == 'connected')
        
        # Update status label
        status_text = ControlCenterConfig.STATUS_STATES[status]['label']
        status_color = ControlCenterConfig.STATUS_STATES[status]['color']
        
        self.connection_status_label.setText(status_text)
        self.connection_status_label.setStyleSheet(f"""
            QLabel {{
                color: {status_color};
                font-weight: bold;
                padding: 4px 8px;
                background-color: transparent;
            }}
        """)
        
        logger.info(f"Connection status: {status}")
    
    def _on_health_check(self, health_data: Dict):
        """Handle health check response"""
        self.server_health = health_data
        
        # Extract health status
        status = health_data.get('status', 'unknown')
        version = health_data.get('version', 'N/A')
        
        # Update health label
        health_color = ControlCenterConfig.get_health_color(status)
        self.health_status_label.setText(f"Health: {status.title()} | v{version}")
        self.health_status_label.setStyleSheet(f"""
            QLabel {{
                color: {health_color};
                padding: 4px 8px;
                background-color: transparent;
            }}
        """)
    
    def _on_api_error(self, error: str):
        """Handle API error"""
        logger.error(f"API error: {error}")
        self.status_bar.showMessage(f"Error: {error}", 5000)
    
    def _on_module_changed(self, module_id: str):
        """Handle module change"""
        config = ControlCenterConfig.get_module_config(module_id)
        self.module_status_label.setText(f"Module: {config.get('name', module_id)}")
        logger.info(f"Active module: {module_id}")
    
    def _on_module_refresh(self, module_id: str):
        """Handle module refresh request"""
        logger.info(f"Refreshing module: {module_id}")
        # Module-specific refresh logic would go here
        self.status_bar.showMessage(f"Refreshed {module_id}", 2000)
    
    def _update_status_bar(self):
        """Update status bar periodically"""
        # This would update live metrics in the status bar
        pass
    
    def _refresh_current_module(self):
        """Refresh currently active module"""
        self.navigation.refresh_current_module()
    
    def _test_connection(self):
        """Test server connection"""
        self.status_bar.showMessage("Testing connection...", 2000)
        self.api_client.test_connection()
    
    def _clear_cache(self):
        """Clear search cache"""
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "Are you sure you want to clear the search cache?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.clear_cache()
            self.status_bar.showMessage("Cache cleared", 2000)
            logger.info("Cache cleared by user")
    
    def _show_settings(self):
        """Show settings dialog"""
        # Settings dialog to be implemented
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog coming soon..."
        )
    
    def _view_logs(self):
        """View application logs"""
        # Log viewer to be implemented
        QMessageBox.information(
            self,
            "Logs",
            "Log viewer coming soon..."
        )
    
    def _show_documentation(self):
        """Show documentation"""
        QMessageBox.information(
            self,
            "Documentation",
            "Documentation will open in your default browser."
        )
    
    def _show_about(self):
        """Show about dialog"""
        about_text = f"""
        <h2>KSE Control Center</h2>
        <p>Version 3.0.0</p>
        <p>Knowledge Search Engine Control Center</p>
        <p>© 2024 KSE Project</p>
        <p><b>Modules:</b> {self.navigation.get_module_count()}</p>
        <p><b>Connection:</b> {'Connected' if self.server_connected else 'Disconnected'}</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About KSE Control Center")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet(GUIConfig.get_default_stylesheet())
        msg.exec()
    
    def _toggle_fullscreen(self, checked: bool):
        """Toggle fullscreen mode"""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()
    
    def _load_window_state(self):
        """Load saved window state"""
        config = ControlCenterConfig.load_config()
        window_state = config.get('window_state', ControlCenterConfig.get_default_window_state())
        
        # Restore window size
        width = window_state.get('width', ControlCenterConfig.WINDOW_WIDTH)
        height = window_state.get('height', ControlCenterConfig.WINDOW_HEIGHT)
        self.resize(width, height)
        
        # Restore maximized state
        if window_state.get('maximized', False):
            self.showMaximized()
        
        # Restore active module
        active_module = window_state.get('active_module', 'pcc')
        self.navigation.set_active_module(active_module)
    
    def _save_window_state(self):
        """Save window state"""
        window_state = {
            'width': self.width(),
            'height': self.height(),
            'maximized': self.isMaximized(),
            'active_module': self.navigation.get_current_module_id(),
        }
        
        config = ControlCenterConfig.load_config()
        config['window_state'] = window_state
        ControlCenterConfig.save_config(config)
        
        logger.info("Window state saved")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop monitoring
        self.api_client.stop_health_monitoring()
        
        # Save window state
        self._save_window_state()
        
        # Emit closing signal
        self.closing.emit()
        
        logger.info("Control Center closing")
        event.accept()


def main():
    """Main entry point for Control Center"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("KSE Control Center")
    app.setOrganizationName("KSE Project")
    
    # Create and show window
    window = ControlCenterMain()
    window.show()
    
    # Run application
    sys.exit(app.exec())


# Backwards compatibility alias
ControlCenter = ControlCenterMain


if __name__ == '__main__':
    main()
