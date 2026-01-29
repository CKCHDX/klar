"""
Settings Dialog
Application settings and preferences dialog
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTabWidget, QWidget, QLabel, QLineEdit, QSpinBox,
                              QCheckBox, QComboBox, QGroupBox, QFormLayout,
                              QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging
import json

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Settings and preferences dialog"""
    
    # Signals
    settings_changed = pyqtSignal(dict)  # Emitted when settings are saved
    
    def __init__(self, current_settings: Optional[Dict[str, Any]] = None, parent=None):
        """
        Initialize settings dialog
        
        Args:
            current_settings: Current settings dictionary
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_settings = current_settings or {}
        self.modified_settings = self.current_settings.copy()
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(700, 600)
        
        self._setup_ui()
        self._apply_styles()
        self._load_settings()
        
        logger.debug("SettingsDialog created")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Application Settings")
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['header'])
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # General tab
        self.tabs.addTab(self._create_general_tab(), "General")
        
        # Appearance tab
        self.tabs.addTab(self._create_appearance_tab(), "Appearance")
        
        # Network tab
        self.tabs.addTab(self._create_network_tab(), "Network")
        
        # Advanced tab
        self.tabs.addTab(self._create_advanced_tab(), "Advanced")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self._reset_defaults)
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Startup group
        startup_group = QGroupBox("Startup")
        startup_layout = QFormLayout(startup_group)
        
        self.auto_start_check = QCheckBox("Start with system")
        startup_layout.addRow("", self.auto_start_check)
        
        self.restore_session_check = QCheckBox("Restore last session")
        startup_layout.addRow("", self.restore_session_check)
        
        layout.addWidget(startup_group)
        
        # Updates group
        updates_group = QGroupBox("Updates")
        updates_layout = QFormLayout(updates_group)
        
        self.auto_update_check = QCheckBox("Check for updates automatically")
        updates_layout.addRow("", self.auto_update_check)
        
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(1, 30)
        self.update_interval_spin.setSuffix(" days")
        updates_layout.addRow("Check interval:", self.update_interval_spin)
        
        layout.addWidget(updates_group)
        
        # Logging group
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        logging_layout.addRow("Log level:", self.log_level_combo)
        
        self.max_log_size_spin = QSpinBox()
        self.max_log_size_spin.setRange(1, 100)
        self.max_log_size_spin.setSuffix(" MB")
        logging_layout.addRow("Max log size:", self.max_log_size_spin)
        
        layout.addWidget(logging_group)
        
        layout.addStretch()
        return widget
    
    def _create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        theme_layout.addRow("Theme:", self.theme_combo)
        
        self.accent_color_combo = QComboBox()
        self.accent_color_combo.addItems(["Blue", "Green", "Orange", "Purple", "Red"])
        theme_layout.addRow("Accent color:", self.accent_color_combo)
        
        layout.addWidget(theme_group)
        
        # Font group
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setSuffix(" pt")
        font_layout.addRow("Font size:", self.font_size_spin)
        
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Segoe UI", "Arial", "Helvetica", "Roboto", "System Default"
        ])
        font_layout.addRow("Font family:", self.font_family_combo)
        
        layout.addWidget(font_group)
        
        # UI group
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.animations_check = QCheckBox("Enable animations")
        ui_layout.addRow("", self.animations_check)
        
        self.tooltips_check = QCheckBox("Show tooltips")
        ui_layout.addRow("", self.tooltips_check)
        
        layout.addWidget(ui_group)
        
        layout.addStretch()
        return widget
    
    def _create_network_tab(self) -> QWidget:
        """Create network settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Connection group
        connection_group = QGroupBox("Connection")
        connection_layout = QFormLayout(connection_group)
        
        self.server_host_edit = QLineEdit()
        self.server_host_edit.setPlaceholderText("localhost")
        connection_layout.addRow("Server host:", self.server_host_edit)
        
        self.server_port_spin = QSpinBox()
        self.server_port_spin.setRange(1, 65535)
        connection_layout.addRow("Server port:", self.server_port_spin)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setSuffix(" seconds")
        connection_layout.addRow("Timeout:", self.timeout_spin)
        
        layout.addWidget(connection_group)
        
        # Proxy group
        proxy_group = QGroupBox("Proxy")
        proxy_layout = QFormLayout(proxy_group)
        
        self.use_proxy_check = QCheckBox("Use proxy server")
        proxy_layout.addRow("", self.use_proxy_check)
        
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("proxy.example.com")
        proxy_layout.addRow("Proxy host:", self.proxy_host_edit)
        
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        proxy_layout.addRow("Proxy port:", self.proxy_port_spin)
        
        layout.addWidget(proxy_group)
        
        layout.addStretch()
        return widget
    
    def _create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Performance group
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout(perf_group)
        
        self.thread_pool_spin = QSpinBox()
        self.thread_pool_spin.setRange(1, 32)
        perf_layout.addRow("Thread pool size:", self.thread_pool_spin)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setSuffix(" MB")
        perf_layout.addRow("Cache size:", self.cache_size_spin)
        
        layout.addWidget(perf_group)
        
        # Data group
        data_group = QGroupBox("Data")
        data_layout = QFormLayout(data_group)
        
        self.auto_save_check = QCheckBox("Auto-save data")
        data_layout.addRow("", self.auto_save_check)
        
        self.save_interval_spin = QSpinBox()
        self.save_interval_spin.setRange(1, 60)
        self.save_interval_spin.setSuffix(" minutes")
        data_layout.addRow("Save interval:", self.save_interval_spin)
        
        layout.addWidget(data_group)
        
        # Debug group
        debug_group = QGroupBox("Debug")
        debug_layout = QFormLayout(debug_group)
        
        self.debug_mode_check = QCheckBox("Enable debug mode")
        debug_layout.addRow("", self.debug_mode_check)
        
        self.verbose_logging_check = QCheckBox("Verbose logging")
        debug_layout.addRow("", self.verbose_logging_check)
        
        layout.addWidget(debug_group)
        
        layout.addStretch()
        return widget
    
    def _apply_styles(self):
        """Apply styling to the dialog"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {GUIConfig.COLORS['bg_primary']};
            }}
            QLabel {{
                color: {GUIConfig.COLORS['text_primary']};
            }}
            QGroupBox {{
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                color: {GUIConfig.COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {GUIConfig.COLORS['primary']};
            }}
        """)
    
    def _load_settings(self):
        """Load current settings into UI"""
        # General
        self.auto_start_check.setChecked(self.current_settings.get('auto_start', False))
        self.restore_session_check.setChecked(self.current_settings.get('restore_session', True))
        self.auto_update_check.setChecked(self.current_settings.get('auto_update', True))
        self.update_interval_spin.setValue(self.current_settings.get('update_interval', 7))
        self.log_level_combo.setCurrentText(self.current_settings.get('log_level', 'INFO'))
        self.max_log_size_spin.setValue(self.current_settings.get('max_log_size', 10))
        
        # Appearance
        self.theme_combo.setCurrentText(self.current_settings.get('theme', 'Dark'))
        self.accent_color_combo.setCurrentText(self.current_settings.get('accent_color', 'Blue'))
        self.font_size_spin.setValue(self.current_settings.get('font_size', 10))
        self.font_family_combo.setCurrentText(self.current_settings.get('font_family', 'Segoe UI'))
        self.animations_check.setChecked(self.current_settings.get('animations', True))
        self.tooltips_check.setChecked(self.current_settings.get('tooltips', True))
        
        # Network
        self.server_host_edit.setText(self.current_settings.get('server_host', 'localhost'))
        self.server_port_spin.setValue(self.current_settings.get('server_port', 8080))
        self.timeout_spin.setValue(self.current_settings.get('timeout', 30))
        self.use_proxy_check.setChecked(self.current_settings.get('use_proxy', False))
        self.proxy_host_edit.setText(self.current_settings.get('proxy_host', ''))
        self.proxy_port_spin.setValue(self.current_settings.get('proxy_port', 8080))
        
        # Advanced
        self.thread_pool_spin.setValue(self.current_settings.get('thread_pool_size', 4))
        self.cache_size_spin.setValue(self.current_settings.get('cache_size', 100))
        self.auto_save_check.setChecked(self.current_settings.get('auto_save', True))
        self.save_interval_spin.setValue(self.current_settings.get('save_interval', 5))
        self.debug_mode_check.setChecked(self.current_settings.get('debug_mode', False))
        self.verbose_logging_check.setChecked(self.current_settings.get('verbose_logging', False))
    
    def _collect_settings(self) -> Dict[str, Any]:
        """Collect settings from UI"""
        return {
            # General
            'auto_start': self.auto_start_check.isChecked(),
            'restore_session': self.restore_session_check.isChecked(),
            'auto_update': self.auto_update_check.isChecked(),
            'update_interval': self.update_interval_spin.value(),
            'log_level': self.log_level_combo.currentText(),
            'max_log_size': self.max_log_size_spin.value(),
            
            # Appearance
            'theme': self.theme_combo.currentText(),
            'accent_color': self.accent_color_combo.currentText(),
            'font_size': self.font_size_spin.value(),
            'font_family': self.font_family_combo.currentText(),
            'animations': self.animations_check.isChecked(),
            'tooltips': self.tooltips_check.isChecked(),
            
            # Network
            'server_host': self.server_host_edit.text(),
            'server_port': self.server_port_spin.value(),
            'timeout': self.timeout_spin.value(),
            'use_proxy': self.use_proxy_check.isChecked(),
            'proxy_host': self.proxy_host_edit.text(),
            'proxy_port': self.proxy_port_spin.value(),
            
            # Advanced
            'thread_pool_size': self.thread_pool_spin.value(),
            'cache_size': self.cache_size_spin.value(),
            'auto_save': self.auto_save_check.isChecked(),
            'save_interval': self.save_interval_spin.value(),
            'debug_mode': self.debug_mode_check.isChecked(),
            'verbose_logging': self.verbose_logging_check.isChecked(),
        }
    
    def _reset_defaults(self):
        """Reset all settings to defaults"""
        self.current_settings = {}
        self._load_settings()
        logger.info("Settings reset to defaults")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get collected settings"""
        return self.modified_settings
    
    def accept(self):
        """Handle Save button"""
        self.modified_settings = self._collect_settings()
        self.settings_changed.emit(self.modified_settings)
        logger.info("Settings saved")
        super().accept()
    
    @staticmethod
    def get_settings_from_dialog(
        current_settings: Optional[Dict[str, Any]] = None,
        parent=None
    ) -> Optional[Dict[str, Any]]:
        """
        Static method to show dialog and get settings
        
        Args:
            current_settings: Current settings
            parent: Parent widget
            
        Returns:
            Settings dictionary or None if cancelled
        """
        dialog = SettingsDialog(current_settings, parent)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_settings()
        return None
