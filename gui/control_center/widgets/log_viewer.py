"""
Log Viewer Widget
Scrollable log viewer with filtering and auto-scroll capabilities
"""

from typing import Optional, List
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
                              QLineEdit, QPushButton, QComboBox, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QFont, QColor, QTextCharFormat
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LogViewer(QWidget):
    """Scrollable log viewer widget with filtering"""
    
    # Signals
    log_added = pyqtSignal(str)
    log_cleared = pyqtSignal()
    filter_changed = pyqtSignal(str)
    
    LOG_LEVELS = ['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def __init__(
        self,
        max_lines: int = 1000,
        auto_scroll: bool = True,
        show_timestamps: bool = True,
        parent=None
    ):
        """
        Initialize log viewer
        
        Args:
            max_lines: Maximum number of log lines to keep
            auto_scroll: Automatically scroll to bottom
            show_timestamps: Show timestamps in logs
            parent: Parent widget
        """
        super().__init__(parent)
        self.max_lines = max_lines
        self.auto_scroll = auto_scroll
        self.show_timestamps = show_timestamps
        self.current_filter = 'ALL'
        self.search_text = ""
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug("LogViewer created")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search logs...")
        self.search_box.textChanged.connect(self._on_search_changed)
        toolbar.addWidget(self.search_box)
        
        # Level filter
        filter_label = QLabel("Level:")
        filter_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
        toolbar.addWidget(filter_label)
        
        self.level_filter = QComboBox()
        self.level_filter.addItems(self.LOG_LEVELS)
        self.level_filter.currentTextChanged.connect(self._on_filter_changed)
        self.level_filter.setFixedWidth(120)
        toolbar.addWidget(self.level_filter)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_logs)
        self.clear_btn.setFixedWidth(80)
        toolbar.addWidget(self.clear_btn)
        
        # Auto-scroll toggle
        self.autoscroll_btn = QPushButton("Auto-scroll: ON" if self.auto_scroll else "Auto-scroll: OFF")
        self.autoscroll_btn.clicked.connect(self._toggle_autoscroll)
        self.autoscroll_btn.setCheckable(True)
        self.autoscroll_btn.setChecked(self.auto_scroll)
        self.autoscroll_btn.setFixedWidth(120)
        toolbar.addWidget(self.autoscroll_btn)
        
        layout.addLayout(toolbar)
        
        # Log text area
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.log_text.setMaximumBlockCount(self.max_lines)
        
        # Set monospace font
        font = QFont("Courier New", GUIConfig.FONTS['size']['small'])
        self.log_text.setFont(font)
        
        layout.addWidget(self.log_text)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.line_count_label = QLabel("Lines: 0")
        self.line_count_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        status_layout.addWidget(self.line_count_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
    
    def _apply_styles(self):
        """Apply styling to the widget"""
        self.log_text.setStyleSheet(Styles.get_log_viewer_style())
        
        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
                padding: 6px;
            }}
        """)
    
    def add_log(self, message: str, level: str = 'INFO'):
        """
        Add a log message
        
        Args:
            message: Log message
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        try:
            level = level.upper()
            
            # Format log entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if self.show_timestamps else ""
            prefix = f"[{timestamp}] [{level}]" if timestamp else f"[{level}]"
            log_entry = f"{prefix} {message}"
            
            # Apply filter
            if self.current_filter != 'ALL' and level != self.current_filter:
                return
            
            # Apply search filter
            if self.search_text and self.search_text.lower() not in log_entry.lower():
                return
            
            # Get color based on level
            color = self._get_level_color(level)
            
            # Add to text area with color
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            
            format = QTextCharFormat()
            format.setForeground(QColor(color))
            
            cursor.insertText(log_entry + "\n", format)
            
            # Auto-scroll
            if self.auto_scroll:
                self.log_text.verticalScrollBar().setValue(
                    self.log_text.verticalScrollBar().maximum()
                )
            
            # Update line count
            self._update_line_count()
            
            self.log_added.emit(log_entry)
        except Exception as e:
            logger.error(f"Error adding log: {e}")
    
    def _get_level_color(self, level: str) -> str:
        """Get color for log level"""
        colors = {
            'DEBUG': GUIConfig.COLORS['text_secondary'],
            'INFO': GUIConfig.COLORS['info'],
            'WARNING': GUIConfig.COLORS['warning'],
            'ERROR': GUIConfig.COLORS['error'],
            'CRITICAL': GUIConfig.COLORS['error'],
        }
        return colors.get(level, GUIConfig.COLORS['text_primary'])
    
    def add_logs(self, messages: List[str], level: str = 'INFO'):
        """Add multiple log messages"""
        for message in messages:
            self.add_log(message, level)
    
    def clear_logs(self):
        """Clear all logs"""
        self.log_text.clear()
        self._update_line_count()
        self.log_cleared.emit()
        logger.debug("Logs cleared")
    
    def _on_search_changed(self, text: str):
        """Handle search text change"""
        self.search_text = text
        self._refresh_logs()
    
    def _on_filter_changed(self, level: str):
        """Handle filter change"""
        self.current_filter = level
        self._refresh_logs()
        self.filter_changed.emit(level)
    
    def _refresh_logs(self):
        """Refresh log display with current filters"""
        # Note: In a full implementation, you'd want to store all logs
        # and re-display them based on filters. For simplicity, this
        # just updates the filter for new logs.
        pass
    
    def _toggle_autoscroll(self):
        """Toggle auto-scroll"""
        self.auto_scroll = not self.auto_scroll
        self.autoscroll_btn.setText("Auto-scroll: ON" if self.auto_scroll else "Auto-scroll: OFF")
    
    def _update_line_count(self):
        """Update line count label"""
        count = self.log_text.document().blockCount()
        self.line_count_label.setText(f"Lines: {count}")
    
    def set_max_lines(self, max_lines: int):
        """Set maximum number of lines"""
        self.max_lines = max_lines
        self.log_text.setMaximumBlockCount(max_lines)
    
    def get_logs(self) -> str:
        """Get all log text"""
        return self.log_text.toPlainText()
    
    def export_logs(self, filename: str):
        """
        Export logs to file
        
        Args:
            filename: Output file path
        """
        try:
            with open(filename, 'w') as f:
                f.write(self.get_logs())
            logger.info(f"Logs exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting logs: {e}")
