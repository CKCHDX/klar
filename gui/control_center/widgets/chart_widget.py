"""
Chart Widget
Displays live charts (line, bar, pie) for data visualization
"""

from typing import List, Dict, Optional, Tuple
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging
from collections import deque

logger = logging.getLogger(__name__)


class ChartWidget(QFrame):
    """Live chart widget for data visualization"""
    
    # Signals
    data_updated = pyqtSignal()
    point_clicked = pyqtSignal(int, float)  # index, value
    
    CHART_TYPES = ['line', 'bar', 'pie']
    
    def __init__(
        self,
        title: str = "Chart",
        chart_type: str = 'line',
        max_points: int = 50,
        parent=None
    ):
        """
        Initialize chart widget
        
        Args:
            title: Chart title
            chart_type: Type of chart ('line', 'bar', 'pie')
            max_points: Maximum number of data points to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.chart_type = chart_type if chart_type in self.CHART_TYPES else 'line'
        self.max_points = max_points
        
        self.data_points = deque(maxlen=max_points)
        self.labels = []
        self.colors = GUIConfig.CHART_COLORS.copy()
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug(f"ChartWidget created: {title} ({chart_type})")
    
    def _setup_ui(self):
        """Setup the UI components"""
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['title'])
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # Chart canvas
        self.canvas = ChartCanvas(self)
        layout.addWidget(self.canvas)
    
    def _apply_styles(self):
        """Apply styling to the widget"""
        self.setStyleSheet(Styles.get_chart_style())
    
    def add_data_point(self, value: float, label: str = ""):
        """
        Add a single data point
        
        Args:
            value: Data value
            label: Optional label
        """
        try:
            self.data_points.append(value)
            if label:
                self.labels.append(label)
            
            self.canvas.update()
            self.data_updated.emit()
            
            logger.debug(f"Data point added: {value}")
        except Exception as e:
            logger.error(f"Error adding data point: {e}")
    
    def set_data(self, data: List[float], labels: Optional[List[str]] = None):
        """
        Set all data points at once
        
        Args:
            data: List of data values
            labels: Optional list of labels
        """
        try:
            self.data_points = deque(data[-self.max_points:], maxlen=self.max_points)
            if labels:
                self.labels = labels[-self.max_points:]
            
            self.canvas.update()
            self.data_updated.emit()
            
            logger.debug(f"Data set: {len(data)} points")
        except Exception as e:
            logger.error(f"Error setting data: {e}")
    
    def clear_data(self):
        """Clear all data points"""
        self.data_points.clear()
        self.labels.clear()
        self.canvas.update()
    
    def set_chart_type(self, chart_type: str):
        """Change the chart type"""
        if chart_type in self.CHART_TYPES:
            self.chart_type = chart_type
            self.canvas.update()
    
    def get_data(self) -> List[float]:
        """Get current data points"""
        return list(self.data_points)


class ChartCanvas(QWidget):
    """Canvas for drawing charts"""
    
    def __init__(self, parent: ChartWidget):
        super().__init__(parent)
        self.chart_widget = parent
        self.setMinimumSize(300, 200)
    
    def paintEvent(self, event):
        """Paint the chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(GUIConfig.COLORS['bg_tertiary']))
        
        if not self.chart_widget.data_points:
            self._draw_no_data(painter)
            return
        
        # Draw based on chart type
        if self.chart_widget.chart_type == 'line':
            self._draw_line_chart(painter)
        elif self.chart_widget.chart_type == 'bar':
            self._draw_bar_chart(painter)
        elif self.chart_widget.chart_type == 'pie':
            self._draw_pie_chart(painter)
    
    def _draw_no_data(self, painter: QPainter):
        """Draw 'No Data' message"""
        painter.setPen(QColor(GUIConfig.COLORS['text_secondary']))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No Data Available")
    
    def _draw_line_chart(self, painter: QPainter):
        """Draw line chart"""
        data = list(self.chart_widget.data_points)
        if not data:
            return
        
        # Calculate dimensions
        padding = 40
        width = self.width() - 2 * padding
        height = self.height() - 2 * padding
        
        max_val = max(data) if data else 1
        min_val = min(data) if data else 0
        val_range = max_val - min_val if max_val != min_val else 1
        
        # Draw grid lines
        painter.setPen(QPen(QColor(GUIConfig.COLORS['border']), 1))
        for i in range(5):
            y = padding + (height * i / 4)
            painter.drawLine(padding, int(y), padding + width, int(y))
        
        # Draw line
        path = QPainterPath()
        for i, value in enumerate(data):
            x = padding + (width * i / max(len(data) - 1, 1))
            y = padding + height - ((value - min_val) / val_range * height)
            
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        painter.setPen(QPen(QColor(GUIConfig.COLORS['primary']), 2))
        painter.drawPath(path)
        
        # Draw points
        painter.setBrush(QColor(GUIConfig.COLORS['primary']))
        for i, value in enumerate(data):
            x = padding + (width * i / max(len(data) - 1, 1))
            y = padding + height - ((value - min_val) / val_range * height)
            painter.drawEllipse(int(x - 3), int(y - 3), 6, 6)
    
    def _draw_bar_chart(self, painter: QPainter):
        """Draw bar chart"""
        data = list(self.chart_widget.data_points)
        if not data:
            return
        
        padding = 40
        width = self.width() - 2 * padding
        height = self.height() - 2 * padding
        
        max_val = max(data) if data else 1
        bar_width = width / len(data) * 0.8
        bar_spacing = width / len(data) * 0.2
        
        painter.setBrush(QColor(GUIConfig.COLORS['primary']))
        for i, value in enumerate(data):
            x = padding + (width * i / len(data)) + bar_spacing / 2
            bar_height = (value / max_val) * height
            y = padding + height - bar_height
            
            painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))
    
    def _draw_pie_chart(self, painter: QPainter):
        """Draw pie chart"""
        data = list(self.chart_widget.data_points)
        if not data:
            return
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(center_x, center_y) - 40
        
        total = sum(data)
        if total == 0:
            return
        
        start_angle = 0
        for i, value in enumerate(data):
            angle = int(value / total * 360 * 16)  # Qt uses 1/16th degree units
            
            color = QColor(self.chart_widget.colors[i % len(self.chart_widget.colors)])
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            
            painter.drawPie(
                center_x - radius,
                center_y - radius,
                radius * 2,
                radius * 2,
                start_angle,
                angle
            )
            
            start_angle += angle
