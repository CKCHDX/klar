"""
Status Tile Widget
Displays system status metrics (CPU, RAM, Disk, etc.) in a tile format
"""

from typing import Optional
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging

logger = logging.getLogger(__name__)


class StatusTile(QFrame):
    """Status display tile widget for metrics"""
    
    # Signals
    value_changed = pyqtSignal(float)  # Emitted when value changes
    threshold_exceeded = pyqtSignal(str, float)  # Emitted when threshold exceeded
    
    def __init__(
        self,
        title: str,
        icon: Optional[str] = None,
        unit: str = "%",
        threshold: float = 80.0,
        parent=None
    ):
        """
        Initialize status tile
        
        Args:
            title: Tile title (e.g., "CPU Usage")
            icon: Optional icon name
            unit: Unit of measurement (default: "%")
            threshold: Warning threshold value (default: 80.0)
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.threshold = threshold
        self.current_value = 0.0
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug(f"StatusTile created: {title}")
    
    def _setup_ui(self):
        """Setup the UI components"""
        self.setFixedSize(200, 150)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['medium'])
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # Value label
        self.value_label = QLabel("0" + self.unit)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['header'])
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        layout.addWidget(self.value_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Normal")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['small'])
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def _apply_styles(self):
        """Apply styling to the widget"""
        self.setStyleSheet(f"""
            StatusTile {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 8px;
            }}
            QLabel {{
                background-color: transparent;
                color: {GUIConfig.COLORS['text_primary']};
            }}
        """)
        
        self._update_progress_style()
    
    def _update_progress_style(self):
        """Update progress bar color based on value"""
        if self.current_value >= self.threshold:
            color = GUIConfig.COLORS['error']
            status = "Critical"
        elif self.current_value >= self.threshold * 0.7:
            color = GUIConfig.COLORS['warning']
            status = "Warning"
        else:
            color = GUIConfig.COLORS['success']
            status = "Normal"
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color}; background-color: transparent;")
    
    def set_value(self, value: float):
        """
        Set the current value
        
        Args:
            value: Value to set (0-100)
        """
        try:
            self.current_value = max(0.0, min(100.0, value))
            self.value_label.setText(f"{self.current_value:.1f}{self.unit}")
            self.progress_bar.setValue(int(self.current_value))
            self._update_progress_style()
            
            # Emit signals
            self.value_changed.emit(self.current_value)
            
            if self.current_value >= self.threshold:
                self.threshold_exceeded.emit(self.title, self.current_value)
            
            logger.debug(f"{self.title} value updated: {self.current_value}")
        except Exception as e:
            logger.error(f"Error setting value: {e}")
    
    def set_threshold(self, threshold: float):
        """
        Set the warning threshold
        
        Args:
            threshold: Threshold value (0-100)
        """
        self.threshold = max(0.0, min(100.0, threshold))
        self._update_progress_style()
    
    def get_value(self) -> float:
        """Get current value"""
        return self.current_value
    
    def reset(self):
        """Reset the tile to default state"""
        self.set_value(0.0)
