"""
Status Indicator Widget
Live status indicator with color-coded states (green/yellow/red)
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QFont
from gui.kse_gui_config import GUIConfig
import logging

logger = logging.getLogger(__name__)


class StatusIndicator(QWidget):
    """Live status indicator widget"""
    
    # Signals
    status_changed = pyqtSignal(str)
    
    STATUS_COLORS = {
        'active': GUIConfig.COLORS['success'],      # Green
        'running': GUIConfig.COLORS['success'],
        'online': GUIConfig.COLORS['success'],
        'warning': GUIConfig.COLORS['warning'],     # Yellow/Orange
        'degraded': GUIConfig.COLORS['warning'],
        'error': GUIConfig.COLORS['error'],         # Red
        'offline': GUIConfig.COLORS['error'],
        'stopped': GUIConfig.COLORS['error'],
        'inactive': GUIConfig.COLORS['text_secondary'],  # Gray
        'idle': GUIConfig.COLORS['text_secondary'],
        'unknown': GUIConfig.COLORS['text_secondary'],
    }
    
    def __init__(
        self,
        label: str = "Status",
        initial_status: str = 'unknown',
        show_label: bool = True,
        pulsing: bool = True,
        size: int = 12,
        parent=None
    ):
        """
        Initialize status indicator
        
        Args:
            label: Status label text
            initial_status: Initial status
            show_label: Show status text label
            pulsing: Enable pulsing animation
            size: Indicator dot size
            parent: Parent widget
        """
        super().__init__(parent)
        self.label_text = label
        self.current_status = initial_status
        self.show_label = show_label
        self.pulsing = pulsing
        self.indicator_size = size
        self.pulse_opacity = 1.0
        
        self._setup_ui()
        
        if pulsing:
            self._start_pulse_animation()
        
        logger.debug(f"StatusIndicator created: {label} ({initial_status})")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        
        # Indicator dot
        self.indicator = StatusDot(self.indicator_size, self.current_status)
        layout.addWidget(self.indicator)
        
        # Label
        if self.show_label:
            self.label = QLabel(self._format_status(self.current_status))
            label_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['normal'])
            self.label.setFont(label_font)
            self.label.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
            layout.addWidget(self.label)
        
        layout.addStretch()
    
    def _format_status(self, status: str) -> str:
        """Format status text"""
        return f"{self.label_text}: {status.title()}"
    
    def set_status(self, status: str):
        """
        Set the status
        
        Args:
            status: Status value
        """
        try:
            old_status = self.current_status
            self.current_status = status.lower()
            
            # Update indicator
            self.indicator.set_status(self.current_status)
            
            # Update label
            if self.show_label:
                self.label.setText(self._format_status(self.current_status))
            
            if old_status != self.current_status:
                self.status_changed.emit(self.current_status)
            
            logger.debug(f"Status changed: {old_status} -> {self.current_status}")
        except Exception as e:
            logger.error(f"Error setting status: {e}")
    
    def get_status(self) -> str:
        """Get current status"""
        return self.current_status
    
    def set_pulsing(self, enabled: bool):
        """Enable/disable pulsing animation"""
        self.pulsing = enabled
        if enabled:
            self._start_pulse_animation()
        else:
            self._stop_pulse_animation()
    
    def _start_pulse_animation(self):
        """Start pulsing animation"""
        if not hasattr(self, 'pulse_timer'):
            self.pulse_timer = QTimer(self)
            self.pulse_timer.timeout.connect(self._pulse_step)
            self.pulse_timer.start(50)  # 50ms interval
            self.pulse_direction = -1
    
    def _stop_pulse_animation(self):
        """Stop pulsing animation"""
        if hasattr(self, 'pulse_timer'):
            self.pulse_timer.stop()
    
    def _pulse_step(self):
        """Pulse animation step"""
        self.pulse_opacity += 0.05 * self.pulse_direction
        
        if self.pulse_opacity <= 0.3:
            self.pulse_direction = 1
        elif self.pulse_opacity >= 1.0:
            self.pulse_direction = -1
        
        self.indicator.set_opacity(self.pulse_opacity)


class StatusDot(QWidget):
    """Status indicator dot"""
    
    def __init__(self, size: int, status: str, parent=None):
        super().__init__(parent)
        self.dot_size = size
        self.status = status
        self.opacity = 1.0
        
        self.setFixedSize(size + 4, size + 4)
    
    def set_status(self, status: str):
        """Set the status"""
        self.status = status
        self.update()
    
    def set_opacity(self, opacity: float):
        """Set the opacity for pulsing"""
        self.opacity = opacity
        self.update()
    
    def paintEvent(self, event):
        """Paint the status dot"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get color
        color = QColor(StatusIndicator.STATUS_COLORS.get(
            self.status,
            StatusIndicator.STATUS_COLORS['unknown']
        ))
        
        # Apply opacity
        color.setAlphaF(self.opacity)
        
        # Draw outer glow (if active status)
        if self.status in ['active', 'running', 'online']:
            glow_color = QColor(color)
            glow_color.setAlphaF(self.opacity * 0.3)
            painter.setBrush(glow_color)
            painter.setPen(Qt.PenStyle.NoPen)
            
            center = self.width() // 2
            glow_radius = self.dot_size // 2 + 2
            painter.drawEllipse(
                center - glow_radius,
                center - glow_radius,
                glow_radius * 2,
                glow_radius * 2
            )
        
        # Draw main dot
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        center = self.width() // 2
        radius = self.dot_size // 2
        painter.drawEllipse(
            center - radius,
            center - radius,
            radius * 2,
            radius * 2
        )


class StatusBadge(QWidget):
    """Status badge with text"""
    
    def __init__(self, status: str = 'unknown', parent=None):
        super().__init__(parent)
        self.status = status
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)
        
        self.label = QLabel(self.status.upper())
        label_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['small'])
        label_font.setBold(True)
        self.label.setFont(label_font)
        
        layout.addWidget(self.label)
    
    def _apply_styles(self):
        """Apply styles"""
        color = StatusIndicator.STATUS_COLORS.get(
            self.status,
            StatusIndicator.STATUS_COLORS['unknown']
        )
        
        self.setStyleSheet(f"""
            StatusBadge {{
                background-color: {color};
                border-radius: 4px;
            }}
            QLabel {{
                color: {GUIConfig.COLORS['text_primary']};
                background-color: transparent;
            }}
        """)
    
    def set_status(self, status: str):
        """Set the status"""
        self.status = status
        self.label.setText(status.upper())
        self._apply_styles()
