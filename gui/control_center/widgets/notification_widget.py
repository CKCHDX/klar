"""
Notification Widget
Alert and notification display with auto-dismiss
"""

from typing import Optional
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
import logging

logger = logging.getLogger(__name__)


class NotificationWidget(QFrame):
    """Alert/notification display widget"""
    
    # Signals
    dismissed = pyqtSignal()
    action_clicked = pyqtSignal()
    
    NOTIFICATION_TYPES = {
        'info': {'color': GUIConfig.COLORS['info'], 'icon': 'ℹ'},
        'success': {'color': GUIConfig.COLORS['success'], 'icon': '✓'},
        'warning': {'color': GUIConfig.COLORS['warning'], 'icon': '⚠'},
        'error': {'color': GUIConfig.COLORS['error'], 'icon': '✗'},
    }
    
    def __init__(
        self,
        title: str,
        message: str = "",
        notification_type: str = 'info',
        auto_dismiss: bool = True,
        dismiss_timeout: int = 5000,
        show_action: bool = False,
        action_text: str = "Action",
        parent=None
    ):
        """
        Initialize notification widget
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type (info, success, warning, error)
            auto_dismiss: Auto-dismiss after timeout
            dismiss_timeout: Timeout in milliseconds
            show_action: Show action button
            action_text: Action button text
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.auto_dismiss = auto_dismiss
        self.dismiss_timeout = dismiss_timeout
        self.show_action = show_action
        self.action_text = action_text
        
        self._setup_ui()
        self._apply_styles()
        
        if auto_dismiss:
            self._start_dismiss_timer()
        
        logger.debug(f"Notification created: {title} ({notification_type})")
    
    def _setup_ui(self):
        """Setup the UI components"""
        self.setFixedHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon
        type_info = self.NOTIFICATION_TYPES.get(
            self.notification_type,
            self.NOTIFICATION_TYPES['info']
        )
        
        self.icon_label = QLabel(type_info['icon'])
        icon_font = QFont(GUIConfig.FONTS['family'], 20)
        self.icon_label.setFont(icon_font)
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet(f"""
            background-color: {type_info['color']};
            color: {GUIConfig.COLORS['text_primary']};
            border-radius: 20px;
        """)
        layout.addWidget(self.icon_label)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Title
        self.title_label = QLabel(self.title)
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['medium'])
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
        content_layout.addWidget(self.title_label)
        
        # Message
        if self.message:
            self.message_label = QLabel(self.message)
            message_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['small'])
            self.message_label.setFont(message_font)
            self.message_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
            self.message_label.setWordWrap(True)
            content_layout.addWidget(self.message_label)
        
        layout.addLayout(content_layout, 1)
        
        # Action button
        if self.show_action:
            self.action_btn = QPushButton(self.action_text)
            self.action_btn.clicked.connect(self._on_action_clicked)
            self.action_btn.setFixedWidth(80)
            layout.addWidget(self.action_btn)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.clicked.connect(self.dismiss)
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {GUIConfig.COLORS['text_secondary']};
                border: none;
                font-size: {GUIConfig.get_font_size('title')}pt;
                padding: 0;
            }}
            QPushButton:hover {{
                color: {GUIConfig.COLORS['text_primary']};
                background-color: {GUIConfig.COLORS['bg_tertiary']};
                border-radius: 12px;
            }}
        """)
        layout.addWidget(self.close_btn)
    
    def _apply_styles(self):
        """Apply styling to the widget"""
        type_info = self.NOTIFICATION_TYPES.get(
            self.notification_type,
            self.NOTIFICATION_TYPES['info']
        )
        
        self.setStyleSheet(f"""
            NotificationWidget {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border-left: 4px solid {type_info['color']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-left: 4px solid {type_info['color']};
                border-radius: 8px;
            }}
            NotificationWidget:hover {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)
    
    def _start_dismiss_timer(self):
        """Start auto-dismiss timer"""
        self.dismiss_timer = QTimer(self)
        self.dismiss_timer.timeout.connect(self.dismiss)
        self.dismiss_timer.start(self.dismiss_timeout)
    
    def _on_action_clicked(self):
        """Handle action button click"""
        self.action_clicked.emit()
        self.dismiss()
    
    def dismiss(self):
        """Dismiss the notification"""
        try:
            if hasattr(self, 'dismiss_timer'):
                self.dismiss_timer.stop()
            
            # Fade out animation
            self.animation = QPropertyAnimation(self, b"windowOpacity")
            self.animation.setDuration(300)
            self.animation.setStartValue(1.0)
            self.animation.setEndValue(0.0)
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animation.finished.connect(self._on_animation_finished)
            self.animation.start()
            
        except Exception as e:
            logger.error(f"Error dismissing notification: {e}")
            self._on_animation_finished()
    
    def _on_animation_finished(self):
        """Handle animation finished"""
        self.dismissed.emit()
        self.deleteLater()
    
    def mousePressEvent(self, event):
        """Handle mouse press - dismiss on click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dismiss()
        super().mousePressEvent(event)


class NotificationContainer(QVBoxLayout):
    """Container for managing multiple notifications"""
    
    def __init__(self, max_notifications: int = 5):
        """
        Initialize notification container
        
        Args:
            max_notifications: Maximum number of visible notifications
        """
        super().__init__()
        self.max_notifications = max_notifications
        self.notifications = []
        
        self.setSpacing(8)
        self.setContentsMargins(8, 8, 8, 8)
        self.addStretch()
    
    def add_notification(
        self,
        title: str,
        message: str = "",
        notification_type: str = 'info',
        **kwargs
    ) -> NotificationWidget:
        """
        Add a notification
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type (info, success, warning, error)
            **kwargs: Additional NotificationWidget arguments
            
        Returns:
            The created notification widget
        """
        # Remove oldest if at max
        if len(self.notifications) >= self.max_notifications:
            oldest = self.notifications[0]
            oldest.dismiss()
        
        # Create notification
        notification = NotificationWidget(
            title=title,
            message=message,
            notification_type=notification_type,
            **kwargs
        )
        
        notification.dismissed.connect(lambda: self._remove_notification(notification))
        
        # Add to layout
        self.insertWidget(self.count() - 1, notification)
        self.notifications.append(notification)
        
        return notification
    
    def _remove_notification(self, notification: NotificationWidget):
        """Remove a notification from the list"""
        if notification in self.notifications:
            self.notifications.remove(notification)
    
    def clear_all(self):
        """Clear all notifications"""
        for notification in self.notifications[:]:
            notification.dismiss()
