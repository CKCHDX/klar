"""
Metric Card Widget
Displays a metric with value, label, and optional trend indicator
"""

from typing import Optional
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging

logger = logging.getLogger(__name__)


class MetricCard(QFrame):
    """Metric display card widget"""
    
    # Signals
    value_changed = pyqtSignal(str)
    card_clicked = pyqtSignal()
    
    def __init__(
        self,
        label: str,
        value: str = "0",
        unit: str = "",
        icon: Optional[str] = None,
        color: Optional[str] = None,
        parent=None
    ):
        """
        Initialize metric card
        
        Args:
            label: Metric label
            value: Initial value
            unit: Unit of measurement
            icon: Optional icon
            color: Optional custom color
            parent: Parent widget
        """
        super().__init__(parent)
        self.label_text = label
        self.value_text = value
        self.unit_text = unit
        self.icon = icon
        self.color = color or GUIConfig.COLORS['primary']
        self.trend_value = 0.0  # Positive = up, negative = down
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug(f"MetricCard created: {label}")
    
    def _setup_ui(self):
        """Setup the UI components"""
        self.setFixedSize(180, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Label
        self.label = QLabel(self.label_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['small'])
        self.label.setFont(label_font)
        self.label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addWidget(self.label)
        
        # Value container
        value_layout = QHBoxLayout()
        value_layout.setSpacing(4)
        
        # Value
        self.value = QLabel(self.value_text)
        self.value.setAlignment(Qt.AlignmentFlag.AlignLeft)
        value_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['header'] + 2)
        value_font.setBold(True)
        self.value.setFont(value_font)
        self.value.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
        value_layout.addWidget(self.value)
        
        # Unit
        if self.unit_text:
            self.unit = QLabel(self.unit_text)
            self.unit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
            unit_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['small'])
            self.unit.setFont(unit_font)
            self.unit.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
            value_layout.addWidget(self.unit)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        # Trend indicator
        self.trend_label = QLabel("")
        self.trend_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        trend_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['small'])
        self.trend_label.setFont(trend_font)
        layout.addWidget(self.trend_label)
        
        layout.addStretch()
    
    def _apply_styles(self):
        """Apply styling to the widget"""
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-left: 4px solid {self.color};
                border-radius: 8px;
            }}
            MetricCard:hover {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
                border: 1px solid {self.color};
                border-left: 4px solid {self.color};
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)
    
    def set_value(self, value: str):
        """
        Set the metric value
        
        Args:
            value: New value
        """
        try:
            self.value_text = value
            self.value.setText(value)
            self.value_changed.emit(value)
            logger.debug(f"{self.label_text} value: {value}")
        except Exception as e:
            logger.error(f"Error setting metric value: {e}")
    
    def set_trend(self, trend: float):
        """
        Set trend indicator
        
        Args:
            trend: Trend value (positive = up, negative = down)
        """
        try:
            self.trend_value = trend
            
            if trend > 0:
                arrow = "↑"
                color = GUIConfig.COLORS['success']
                text = f"{arrow} +{trend:.1f}%"
            elif trend < 0:
                arrow = "↓"
                color = GUIConfig.COLORS['error']
                text = f"{arrow} {trend:.1f}%"
            else:
                arrow = "→"
                color = GUIConfig.COLORS['text_secondary']
                text = f"{arrow} 0%"
            
            self.trend_label.setText(text)
            self.trend_label.setStyleSheet(f"color: {color}; background-color: transparent;")
        except Exception as e:
            logger.error(f"Error setting trend: {e}")
    
    def set_color(self, color: str):
        """
        Set the accent color
        
        Args:
            color: Color hex code
        """
        self.color = color
        self._apply_styles()
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.card_clicked.emit()
        super().mousePressEvent(event)
    
    def get_value(self) -> str:
        """Get current value"""
        return self.value_text
