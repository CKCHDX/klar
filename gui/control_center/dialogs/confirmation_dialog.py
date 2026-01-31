"""
Confirmation Dialog
Simple confirmation prompt dialog
"""

from typing import Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from gui.kse_gui_config import GUIConfig
import logging

logger = logging.getLogger(__name__)


class ConfirmationDialog(QDialog):
    """Confirmation prompt dialog"""
    
    # Signals
    confirmed = pyqtSignal()
    cancelled = pyqtSignal()
    
    DIALOG_TYPES = {
        'question': {'icon': '?', 'color': GUIConfig.COLORS['info']},
        'warning': {'icon': '⚠', 'color': GUIConfig.COLORS['warning']},
        'danger': {'icon': '!', 'color': GUIConfig.COLORS['error']},
        'info': {'icon': 'ℹ', 'color': GUIConfig.COLORS['primary']},
    }
    
    def __init__(
        self,
        title: str,
        message: str,
        dialog_type: str = 'question',
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
        show_dont_ask: bool = False,
        parent=None
    ):
        """
        Initialize confirmation dialog
        
        Args:
            title: Dialog title
            message: Confirmation message
            dialog_type: Dialog type (question, warning, danger, info)
            ok_text: OK button text
            cancel_text: Cancel button text
            show_dont_ask: Show "Don't ask again" checkbox
            parent: Parent widget
        """
        super().__init__(parent)
        self.title_text = title
        self.message_text = message
        self.dialog_type = dialog_type
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        self.show_dont_ask = show_dont_ask
        self.dont_ask_again = False
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(450, 200)
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug(f"ConfirmationDialog created: {title}")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Content layout with icon and message
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        
        # Icon
        type_info = self.DIALOG_TYPES.get(
            self.dialog_type,
            self.DIALOG_TYPES['question']
        )
        
        icon_label = QLabel(type_info['icon'])
        icon_font = QFont(GUIConfig.FONTS['family'], 32)
        icon_label.setFont(icon_font)
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            background-color: {type_info['color']};
            color: {GUIConfig.COLORS['text_primary']};
            border-radius: 30px;
        """)
        content_layout.addWidget(icon_label)
        
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
        
        content_layout.addLayout(message_layout, 1)
        layout.addLayout(content_layout)
        
        # "Don't ask again" checkbox
        if self.show_dont_ask:
            self.dont_ask_check = QCheckBox("Don't ask me again")
            self.dont_ask_check.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
            layout.addWidget(self.dont_ask_check)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton(self.ok_text)
        self.ok_button.clicked.connect(self._on_ok)
        self.ok_button.setDefault(True)
        
        # Color OK button based on type
        if self.dialog_type == 'danger':
            self.ok_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {GUIConfig.COLORS['error']};
                    color: {GUIConfig.COLORS['text_primary']};
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #D32F2F;
                }}
            """)
        
        button_layout.addWidget(self.ok_button)
        
        cancel_button = QPushButton(self.cancel_text)
        cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(cancel_button)
        
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
        """)
    
    def _on_ok(self):
        """Handle OK button"""
        if self.show_dont_ask and hasattr(self, 'dont_ask_check'):
            self.dont_ask_again = self.dont_ask_check.isChecked()
        
        self.confirmed.emit()
        self.accept()
    
    def _on_cancel(self):
        """Handle Cancel button"""
        self.cancelled.emit()
        self.reject()
    
    def should_skip(self) -> bool:
        """Check if "Don't ask again" was checked"""
        return self.dont_ask_again
    
    @staticmethod
    def ask(
        title: str,
        message: str,
        dialog_type: str = 'question',
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
        show_dont_ask: bool = False,
        parent=None
    ) -> tuple[bool, bool]:
        """
        Static method to show confirmation dialog
        
        Args:
            title: Dialog title
            message: Confirmation message
            dialog_type: Dialog type (question, warning, danger, info)
            ok_text: OK button text
            cancel_text: Cancel button text
            show_dont_ask: Show "Don't ask again" checkbox
            parent: Parent widget
            
        Returns:
            Tuple of (confirmed, dont_ask_again)
        """
        dialog = ConfirmationDialog(
            title,
            message,
            dialog_type,
            ok_text,
            cancel_text,
            show_dont_ask,
            parent
        )
        
        result = dialog.exec() == QDialog.DialogCode.Accepted
        dont_ask = dialog.should_skip()
        
        return result, dont_ask
    
    @staticmethod
    def confirm(
        message: str,
        title: str = "Confirm",
        parent=None
    ) -> bool:
        """
        Simple confirmation dialog
        
        Args:
            message: Confirmation message
            title: Dialog title
            parent: Parent widget
            
        Returns:
            True if confirmed, False otherwise
        """
        result, _ = ConfirmationDialog.ask(title, message, 'question', parent=parent)
        return result
    
    @staticmethod
    def warn(
        message: str,
        title: str = "Warning",
        parent=None
    ) -> bool:
        """
        Warning confirmation dialog
        
        Args:
            message: Warning message
            title: Dialog title
            parent: Parent widget
            
        Returns:
            True if confirmed, False otherwise
        """
        result, _ = ConfirmationDialog.ask(title, message, 'warning', parent=parent)
        return result
    
    @staticmethod
    def danger(
        message: str,
        title: str = "Confirm Action",
        ok_text: str = "Delete",
        parent=None
    ) -> bool:
        """
        Danger confirmation dialog
        
        Args:
            message: Danger message
            title: Dialog title
            ok_text: OK button text
            parent: Parent widget
            
        Returns:
            True if confirmed, False otherwise
        """
        result, _ = ConfirmationDialog.ask(title, message, 'danger', ok_text, parent=parent)
        return result
