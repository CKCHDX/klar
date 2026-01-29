"""
Timeline Widget
Displays events in a chronological timeline
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TimelineWidget(QWidget):
    """Event timeline display widget"""
    
    # Signals
    event_clicked = pyqtSignal(dict)  # Event data
    event_added = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """Initialize timeline widget"""
        super().__init__(parent)
        self.events = []
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug("TimelineWidget created")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Timeline container
        self.timeline_container = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_layout.setContentsMargins(16, 16, 16, 16)
        self.timeline_layout.setSpacing(4)
        self.timeline_layout.addStretch()
        
        scroll.setWidget(self.timeline_container)
        layout.addWidget(scroll)
    
    def _apply_styles(self):
        """Apply styling to the widget"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {GUIConfig.COLORS['bg_primary']};
            }}
            QScrollArea {{
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
            }}
        """)
    
    def add_event(
        self,
        title: str,
        description: str = "",
        timestamp: Optional[datetime] = None,
        event_type: str = "info",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add an event to the timeline
        
        Args:
            title: Event title
            description: Event description
            timestamp: Event timestamp (default: now)
            event_type: Event type (info, success, warning, error)
            metadata: Additional metadata
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            event_data = {
                'title': title,
                'description': description,
                'timestamp': timestamp,
                'type': event_type,
                'metadata': metadata or {}
            }
            
            self.events.insert(0, event_data)  # Add to beginning (newest first)
            
            # Create event widget
            event_widget = TimelineEventWidget(event_data, self)
            event_widget.clicked.connect(lambda: self.event_clicked.emit(event_data))
            
            # Insert at beginning (after any existing events)
            self.timeline_layout.insertWidget(0, event_widget)
            
            self.event_added.emit(event_data)
            logger.debug(f"Event added: {title}")
        except Exception as e:
            logger.error(f"Error adding event: {e}")
    
    def clear_events(self):
        """Clear all events"""
        self.events.clear()
        
        # Remove all widgets except stretch
        while self.timeline_layout.count() > 1:
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all events"""
        return self.events.copy()
    
    def filter_events(self, event_type: Optional[str] = None):
        """
        Filter events by type
        
        Args:
            event_type: Event type to show (None = show all)
        """
        for i in range(self.timeline_layout.count() - 1):
            widget = self.timeline_layout.itemAt(i).widget()
            if isinstance(widget, TimelineEventWidget):
                if event_type is None:
                    widget.show()
                else:
                    widget.setVisible(widget.event_data['type'] == event_type)


class TimelineEventWidget(QFrame):
    """Single event in timeline"""
    
    clicked = pyqtSignal()
    
    def __init__(self, event_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.event_data = event_data
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the UI"""
        self.setFixedHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Timeline indicator (dot and line)
        indicator = TimelineIndicator(self.event_data['type'])
        layout.addWidget(indicator)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Title and timestamp
        header_layout = QHBoxLayout()
        
        title = QLabel(self.event_data['title'])
        title.setStyleSheet(f"""
            color: {GUIConfig.COLORS['text_primary']};
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        timestamp = self.event_data['timestamp'].strftime("%H:%M:%S")
        time_label = QLabel(timestamp)
        time_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        header_layout.addWidget(time_label)
        
        content_layout.addLayout(header_layout)
        
        # Description
        if self.event_data['description']:
            desc = QLabel(self.event_data['description'])
            desc.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
            desc.setWordWrap(True)
            content_layout.addWidget(desc)
        
        layout.addLayout(content_layout)
    
    def _apply_styles(self):
        """Apply styles"""
        self.setStyleSheet(f"""
            TimelineEventWidget {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 8px;
            }}
            TimelineEventWidget:hover {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
                border: 1px solid {GUIConfig.COLORS['primary']};
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class TimelineIndicator(QWidget):
    """Timeline indicator (dot and line)"""
    
    def __init__(self, event_type: str, parent=None):
        super().__init__(parent)
        self.event_type = event_type
        self.setFixedSize(20, 60)
    
    def paintEvent(self, event):
        """Paint the indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get color based on type
        colors = {
            'info': GUIConfig.COLORS['info'],
            'success': GUIConfig.COLORS['success'],
            'warning': GUIConfig.COLORS['warning'],
            'error': GUIConfig.COLORS['error'],
        }
        color = QColor(colors.get(self.event_type, GUIConfig.COLORS['primary']))
        
        # Draw vertical line
        painter.setPen(QPen(QColor(GUIConfig.COLORS['border']), 2))
        center_x = self.width() // 2
        painter.drawLine(center_x, 0, center_x, self.height())
        
        # Draw dot
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        center_y = self.height() // 2
        painter.drawEllipse(center_x - 6, center_y - 6, 12, 12)
