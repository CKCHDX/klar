"""
Error Dialog
Error display dialog with details and logging
"""

from typing import Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
import logging
import traceback

logger = logging.getLogger(__name__)


class ErrorDialog(QDialog):
    """Error display dialog"""
    
    # Signals
    error_reported = pyqtSignal(str)  # Error details
    
    def __init__(
        self,
        title: str,
        message: str,
        details: Optional[str] = None,
        error_type: str = 'error',
        parent=None
    ):
        """
        Initialize error dialog
        
        Args:
            title: Error title
            message: Error message
            details: Detailed error information
            error_type: Error type (error, critical, warning)
            parent: Parent widget
        """
        super().__init__(parent)
        self.title_text = title
        self.message_text = message
        self.details_text = details or ""
        self.error_type = error_type
        self.details_visible = False
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(500, 300)
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug(f"ErrorDialog created: {title}")
        logger.error(f"Error: {message}")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with icon
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        # Error icon
        icon_colors = {
            'error': GUIConfig.COLORS['error'],
            'critical': GUIConfig.COLORS['error'],
            'warning': GUIConfig.COLORS['warning'],
        }
        
        icon_symbols = {
            'error': '✗',
            'critical': '⚠',
            'warning': '⚠',
        }
        
        color = icon_colors.get(self.error_type, icon_colors['error'])
        symbol = icon_symbols.get(self.error_type, icon_symbols['error'])
        
        icon_label = QLabel(symbol)
        icon_font = QFont(GUIConfig.FONTS['family'], 36)
        icon_label.setFont(icon_font)
        icon_label.setFixedSize(70, 70)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            background-color: {color};
            color: {GUIConfig.COLORS['text_primary']};
            border-radius: 35px;
        """)
        header_layout.addWidget(icon_label)
        
        # Message layout
        message_layout = QVBoxLayout()
        message_layout.setSpacing(8)
        
        # Title
        title_label = QLabel(self.title_text)
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['title'])
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        message_layout.addWidget(title_label)
        
        # Message
        message_label = QLabel(self.message_text)
        message_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['normal'])
        message_label.setFont(message_font)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        message_layout.addWidget(message_label)
        
        header_layout.addLayout(message_layout, 1)
        layout.addLayout(header_layout)
        
        # Details section (collapsible)
        if self.details_text:
            self.details_widget = QTextEdit()
            self.details_widget.setReadOnly(True)
            self.details_widget.setPlainText(self.details_text)
            self.details_widget.setVisible(False)
            self.details_widget.setMaximumHeight(200)
            layout.addWidget(self.details_widget)
            
            self.details_button = QPushButton("Show Details ▼")
            self.details_button.clicked.connect(self._toggle_details)
            layout.addWidget(self.details_button)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        if self.details_text:
            copy_button = QPushButton("Copy Error")
            copy_button.clicked.connect(self._copy_error)
            button_layout.addWidget(copy_button)
        
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
    
    def _apply_styles(self):
        """Apply styling to the dialog"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {GUIConfig.COLORS['bg_primary']};
            }}
            QLabel {{
                color: {GUIConfig.COLORS['text_primary']};
                background-color: transparent;
            }}
            QTextEdit {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }}
        """)
    
    def _toggle_details(self):
        """Toggle details visibility"""
        self.details_visible = not self.details_visible
        
        if hasattr(self, 'details_widget'):
            self.details_widget.setVisible(self.details_visible)
            self.details_button.setText(
                "Hide Details ▲" if self.details_visible else "Show Details ▼"
            )
            
            # Resize dialog
            if self.details_visible:
                self.resize(self.width(), self.height() + 200)
            else:
                self.resize(self.width(), 300)
    
    def _copy_error(self):
        """Copy error details to clipboard"""
        try:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            
            error_text = f"""
{self.title_text}

{self.message_text}

Details:
{self.details_text}
            """.strip()
            
            clipboard.setText(error_text)
            logger.info("Error details copied to clipboard")
        except Exception as e:
            logger.error(f"Failed to copy error: {e}")
    
    @staticmethod
    def show_error(
        title: str,
        message: str,
        details: Optional[str] = None,
        parent=None
    ):
        """
        Static method to show error dialog
        
        Args:
            title: Error title
            message: Error message
            details: Detailed error information
            parent: Parent widget
        """
        dialog = ErrorDialog(title, message, details, 'error', parent)
        dialog.exec()
    
    @staticmethod
    def show_critical(
        title: str,
        message: str,
        details: Optional[str] = None,
        parent=None
    ):
        """
        Static method to show critical error dialog
        
        Args:
            title: Error title
            message: Error message
            details: Detailed error information
            parent: Parent widget
        """
        dialog = ErrorDialog(title, message, details, 'critical', parent)
        dialog.exec()
    
    @staticmethod
    def show_warning(
        title: str,
        message: str,
        details: Optional[str] = None,
        parent=None
    ):
        """
        Static method to show warning dialog
        
        Args:
            title: Warning title
            message: Warning message
            details: Detailed information
            parent: Parent widget
        """
        dialog = ErrorDialog(title, message, details, 'warning', parent)
        dialog.exec()
    
    @staticmethod
    def from_exception(
        exception: Exception,
        title: str = "An Error Occurred",
        parent=None
    ):
        """
        Create error dialog from exception
        
        Args:
            exception: Exception object
            title: Error title
            parent: Parent widget
        """
        message = str(exception)
        details = ''.join(traceback.format_exception(
            type(exception),
            exception,
            exception.__traceback__
        ))
        
        dialog = ErrorDialog(title, message, details, 'error', parent)
        dialog.exec()
