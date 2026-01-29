"""
Status Bar Component
Status bar with live updates and indicators
"""

from typing import Optional, Dict
from PyQt6.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
from gui.control_center.widgets.status_indicator import StatusIndicator
import logging

logger = logging.getLogger(__name__)


class StatusBar(QStatusBar):
    """Status bar component with live updates"""
    
    # Signals
    status_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialize status bar
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.indicators = {}
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug("StatusBar created")
    
    def _setup_ui(self):
        """Setup the UI components"""
        # Main status label (left side)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
        self.addWidget(self.status_label, 1)
        
        # Right side container
        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 8, 0)
        right_layout.setSpacing(12)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)
        
        # Connection status indicator
        self.connection_indicator = StatusIndicator(
            label="Connection",
            initial_status='unknown',
            show_label=True,
            pulsing=False
        )
        right_layout.addWidget(self.connection_indicator)
        self.indicators['connection'] = self.connection_indicator
        
        # System status indicator
        self.system_indicator = StatusIndicator(
            label="System",
            initial_status='idle',
            show_label=True,
            pulsing=False
        )
        right_layout.addWidget(self.system_indicator)
        self.indicators['system'] = self.system_indicator
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        right_layout.addWidget(self.info_label)
        
        self.addPermanentWidget(right_widget)
    
    def _apply_styles(self):
        """Apply styling to status bar"""
        self.setStyleSheet(f"""
            QStatusBar {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
                border-top: 1px solid {GUIConfig.COLORS['border']};
                padding: 4px 8px;
            }}
            QStatusBar::item {{
                border: none;
            }}
            QProgressBar {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {GUIConfig.COLORS['primary']};
                border-radius: 7px;
            }}
        """)
    
    def set_status(self, message: str, timeout: int = 0):
        """
        Set status message
        
        Args:
            message: Status message
            timeout: Message timeout in milliseconds (0 = permanent)
        """
        self.status_label.setText(message)
        
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready"))
        
        logger.debug(f"Status: {message}")
    
    def set_status_with_color(self, message: str, color: str, timeout: int = 0):
        """
        Set status message with color
        
        Args:
            message: Status message
            color: Text color
            timeout: Message timeout in milliseconds
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")
        
        if timeout > 0:
            def reset():
                self.status_label.setText("Ready")
                self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
            
            QTimer.singleShot(timeout, reset)
    
    def show_success(self, message: str, timeout: int = 3000):
        """
        Show success message
        
        Args:
            message: Success message
            timeout: Message timeout in milliseconds
        """
        self.set_status_with_color(message, GUIConfig.COLORS['success'], timeout)
    
    def show_error(self, message: str, timeout: int = 5000):
        """
        Show error message
        
        Args:
            message: Error message
            timeout: Message timeout in milliseconds
        """
        self.set_status_with_color(message, GUIConfig.COLORS['error'], timeout)
    
    def show_warning(self, message: str, timeout: int = 4000):
        """
        Show warning message
        
        Args:
            message: Warning message
            timeout: Message timeout in milliseconds
        """
        self.set_status_with_color(message, GUIConfig.COLORS['warning'], timeout)
    
    def show_info(self, message: str, timeout: int = 3000):
        """
        Show info message
        
        Args:
            message: Info message
            timeout: Message timeout in milliseconds
        """
        self.set_status_with_color(message, GUIConfig.COLORS['info'], timeout)
    
    def set_info(self, text: str):
        """
        Set info label text
        
        Args:
            text: Info text
        """
        self.info_label.setText(text)
    
    def show_progress(self, show: bool = True):
        """
        Show/hide progress bar
        
        Args:
            show: Show progress bar
        """
        self.progress_bar.setVisible(show)
    
    def set_progress(self, value: int):
        """
        Set progress bar value
        
        Args:
            value: Progress value (0-100)
        """
        self.progress_bar.setValue(value)
        if value > 0:
            self.show_progress(True)
        if value >= 100:
            QTimer.singleShot(1000, lambda: self.show_progress(False))
    
    def set_progress_indeterminate(self, indeterminate: bool = True):
        """
        Set progress bar to indeterminate mode
        
        Args:
            indeterminate: Enable indeterminate mode
        """
        if indeterminate:
            self.progress_bar.setRange(0, 0)
            self.show_progress(True)
        else:
            self.progress_bar.setRange(0, 100)
    
    def set_indicator_status(self, indicator_name: str, status: str):
        """
        Set status indicator
        
        Args:
            indicator_name: Indicator name ('connection', 'system')
            status: Status value
        """
        indicator = self.indicators.get(indicator_name)
        if indicator:
            indicator.set_status(status)
    
    def set_connection_status(self, status: str):
        """
        Set connection status
        
        Args:
            status: Connection status (online, offline, etc.)
        """
        self.set_indicator_status('connection', status)
    
    def set_system_status(self, status: str):
        """
        Set system status
        
        Args:
            status: System status (running, idle, error, etc.)
        """
        self.set_indicator_status('system', status)
    
    def add_indicator(
        self,
        name: str,
        label: str,
        initial_status: str = 'unknown'
    ) -> StatusIndicator:
        """
        Add a custom status indicator
        
        Args:
            name: Indicator name
            label: Indicator label
            initial_status: Initial status
            
        Returns:
            Created StatusIndicator
        """
        indicator = StatusIndicator(
            label=label,
            initial_status=initial_status,
            show_label=True,
            pulsing=False
        )
        
        # Find the right widget to insert before info_label
        for i in range(self.children().__len__()):
            widget = self.children()[i]
            if isinstance(widget, QWidget):
                layout = widget.layout()
                if layout and isinstance(layout, QHBoxLayout):
                    # Insert before info_label
                    count = layout.count()
                    if count > 0:
                        layout.insertWidget(count - 1, indicator)
                        break
        
        self.indicators[name] = indicator
        return indicator
    
    def remove_indicator(self, name: str):
        """
        Remove a status indicator
        
        Args:
            name: Indicator name
        """
        indicator = self.indicators.get(name)
        if indicator:
            indicator.deleteLater()
            del self.indicators[name]
    
    def clear_status(self):
        """Clear all status messages"""
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
        self.show_progress(False)
