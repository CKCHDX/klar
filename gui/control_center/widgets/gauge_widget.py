"""
Gauge Widget
Circular gauge display for percentage values (0-100%)
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QConicalGradient
import math
from gui.kse_gui_config import GUIConfig
import logging

logger = logging.getLogger(__name__)


class GaugeWidget(QWidget):
    """Circular gauge display widget"""
    
    # Signals
    value_changed = pyqtSignal(float)
    threshold_exceeded = pyqtSignal(float)
    
    def __init__(
        self,
        title: str = "Gauge",
        min_value: float = 0.0,
        max_value: float = 100.0,
        threshold: float = 80.0,
        parent=None
    ):
        """
        Initialize gauge widget
        
        Args:
            title: Gauge title
            min_value: Minimum value
            max_value: Maximum value
            threshold: Warning threshold
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.min_value = min_value
        self.max_value = max_value
        self.threshold = threshold
        self.current_value = min_value
        
        self.setMinimumSize(200, 220)
        self._setup_ui()
        
        logger.debug(f"GaugeWidget created: {title}")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['medium'])
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
    
    def paintEvent(self, event):
        """Paint the gauge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate dimensions
        center_x = self.width() // 2
        center_y = self.height() // 2 + 20
        radius = min(self.width(), self.height() - 40) // 2 - 10
        
        # Draw background arc
        painter.setPen(QPen(QColor(GUIConfig.COLORS['bg_tertiary']), 20))
        painter.drawArc(
            center_x - radius,
            center_y - radius,
            radius * 2,
            radius * 2,
            30 * 16,  # Start at 30 degrees
            300 * 16  # Span 300 degrees
        )
        
        # Calculate value angle
        value_range = self.max_value - self.min_value
        if value_range == 0:
            value_range = 1
        
        normalized_value = (self.current_value - self.min_value) / value_range
        angle = int(normalized_value * 300)
        
        # Determine color based on threshold
        if self.current_value >= self.threshold:
            color = QColor(GUIConfig.COLORS['error'])
        elif self.current_value >= self.threshold * 0.7:
            color = QColor(GUIConfig.COLORS['warning'])
        else:
            color = QColor(GUIConfig.COLORS['success'])
        
        # Draw value arc
        painter.setPen(QPen(color, 20))
        painter.drawArc(
            center_x - radius,
            center_y - radius,
            radius * 2,
            radius * 2,
            30 * 16,
            angle * 16
        )
        
        # Draw center circle
        inner_radius = radius - 30
        painter.setBrush(QColor(GUIConfig.COLORS['bg_primary']))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            center_x - inner_radius,
            center_y - inner_radius,
            inner_radius * 2,
            inner_radius * 2
        )
        
        # Draw value text
        painter.setPen(QColor(GUIConfig.COLORS['text_primary']))
        value_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['header'] + 4)
        value_font.setBold(True)
        painter.setFont(value_font)
        
        value_text = f"{self.current_value:.1f}"
        text_rect = painter.fontMetrics().boundingRect(value_text)
        painter.drawText(
            center_x - text_rect.width() // 2,
            center_y + text_rect.height() // 4,
            value_text
        )
        
        # Draw min/max labels
        label_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['small'])
        painter.setFont(label_font)
        painter.setPen(QColor(GUIConfig.COLORS['text_secondary']))
        
        # Min label (bottom left)
        min_text = str(int(self.min_value))
        min_angle = math.radians(210)  # 30 + 180
        min_x = center_x + int((radius + 15) * math.cos(min_angle))
        min_y = center_y + int((radius + 15) * math.sin(min_angle))
        painter.drawText(min_x - 10, min_y + 5, min_text)
        
        # Max label (bottom right)
        max_text = str(int(self.max_value))
        max_angle = math.radians(-30)  # 330 - 360
        max_x = center_x + int((radius + 15) * math.cos(max_angle))
        max_y = center_y + int((radius + 15) * math.sin(max_angle))
        painter.drawText(max_x - 10, max_y + 5, max_text)
    
    def set_value(self, value: float):
        """
        Set the gauge value
        
        Args:
            value: New value
        """
        try:
            old_value = self.current_value
            self.current_value = max(self.min_value, min(self.max_value, value))
            self.update()
            
            if old_value != self.current_value:
                self.value_changed.emit(self.current_value)
            
            if self.current_value >= self.threshold and old_value < self.threshold:
                self.threshold_exceeded.emit(self.current_value)
            
            logger.debug(f"{self.title} value: {self.current_value}")
        except Exception as e:
            logger.error(f"Error setting gauge value: {e}")
    
    def get_value(self) -> float:
        """Get current value"""
        return self.current_value
    
    def set_threshold(self, threshold: float):
        """Set the warning threshold"""
        self.threshold = threshold
        self.update()
    
    def set_range(self, min_value: float, max_value: float):
        """Set the value range"""
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = max(min_value, min(max_value, self.current_value))
        self.update()
