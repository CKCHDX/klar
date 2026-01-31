"""
Progress Widget
Enhanced progress bar with percentage display and status
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
import logging

logger = logging.getLogger(__name__)


class ProgressWidget(QWidget):
    """Progress bar widget with percentage and status"""
    
    # Signals
    progress_changed = pyqtSignal(int)  # 0-100
    progress_completed = pyqtSignal()
    
    def __init__(
        self,
        title: str = "Progress",
        show_percentage: bool = True,
        show_status: bool = True,
        indeterminate: bool = False,
        parent=None
    ):
        """
        Initialize progress widget
        
        Args:
            title: Progress title
            show_percentage: Show percentage text
            show_status: Show status label
            indeterminate: Show indeterminate progress
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.show_percentage = show_percentage
        self.show_status = show_status
        self.indeterminate = indeterminate
        self.current_value = 0
        self.status_text = "Starting..."
        
        self._setup_ui()
        self._apply_styles()
        
        if indeterminate:
            self._start_indeterminate()
        
        logger.debug(f"ProgressWidget created: {title}")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        self.title_label = QLabel(self.title)
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['medium'])
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
        layout.addWidget(self.title_label)
        
        # Progress bar with percentage
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(8)
        
        self.progress_bar = QProgressBar()
        if self.indeterminate:
            self.progress_bar.setRange(0, 0)  # Indeterminate mode
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
        
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(24)
        progress_layout.addWidget(self.progress_bar)
        
        if self.show_percentage and not self.indeterminate:
            self.percentage_label = QLabel("0%")
            percentage_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['medium'])
            percentage_font.setBold(True)
            self.percentage_label.setFont(percentage_font)
            self.percentage_label.setStyleSheet(f"color: {GUIConfig.COLORS['primary']};")
            self.percentage_label.setFixedWidth(50)
            progress_layout.addWidget(self.percentage_label)
        
        layout.addLayout(progress_layout)
        
        # Status label
        if self.show_status:
            self.status_label = QLabel(self.status_text)
            status_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['small'])
            self.status_label.setFont(status_font)
            self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
            layout.addWidget(self.status_label)
    
    def _apply_styles(self):
        """Apply styling to the widget"""
        color = self._get_progress_color()
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 12px;
                text-align: center;
                color: {GUIConfig.COLORS['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 11px;
            }}
        """)
    
    def _get_progress_color(self) -> str:
        """Get color based on progress value"""
        if self.current_value == 100:
            return GUIConfig.COLORS['success']
        elif self.current_value >= 75:
            return GUIConfig.COLORS['info']
        elif self.current_value >= 50:
            return GUIConfig.COLORS['primary']
        elif self.current_value >= 25:
            return GUIConfig.COLORS['warning']
        else:
            return GUIConfig.COLORS['primary']
    
    def set_progress(self, value: int, status: Optional[str] = None):
        """
        Set progress value
        
        Args:
            value: Progress value (0-100)
            status: Optional status text
        """
        try:
            if self.indeterminate:
                logger.warning("Cannot set value in indeterminate mode")
                return
            
            old_value = self.current_value
            self.current_value = max(0, min(100, value))
            
            self.progress_bar.setValue(self.current_value)
            
            if self.show_percentage:
                self.percentage_label.setText(f"{self.current_value}%")
            
            if status:
                self.set_status(status)
            
            # Update color
            self._apply_styles()
            
            self.progress_changed.emit(self.current_value)
            
            if self.current_value == 100 and old_value != 100:
                self.progress_completed.emit()
            
            logger.debug(f"Progress: {self.current_value}%")
        except Exception as e:
            logger.error(f"Error setting progress: {e}")
    
    def set_status(self, status: str):
        """
        Set status text
        
        Args:
            status: Status message
        """
        self.status_text = status
        if self.show_status:
            self.status_label.setText(status)
    
    def increment(self, amount: int = 1):
        """
        Increment progress by amount
        
        Args:
            amount: Amount to increment
        """
        self.set_progress(self.current_value + amount)
    
    def reset(self):
        """Reset progress to 0"""
        self.set_progress(0, "Starting...")
    
    def complete(self):
        """Set progress to 100%"""
        self.set_progress(100, "Completed")
    
    def set_error(self, message: str = "Error occurred"):
        """
        Set error state
        
        Args:
            message: Error message
        """
        self.set_status(message)
        if self.show_status:
            self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['error']};")
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 12px;
            }}
            QProgressBar::chunk {{
                background-color: {GUIConfig.COLORS['error']};
                border-radius: 11px;
            }}
        """)
    
    def set_indeterminate(self, indeterminate: bool):
        """
        Toggle indeterminate mode
        
        Args:
            indeterminate: Enable/disable indeterminate mode
        """
        self.indeterminate = indeterminate
        
        if indeterminate:
            self.progress_bar.setRange(0, 0)
            if self.show_percentage:
                self.percentage_label.hide()
            self._start_indeterminate()
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(self.current_value)
            if self.show_percentage:
                self.percentage_label.show()
            self._stop_indeterminate()
    
    def _start_indeterminate(self):
        """Start indeterminate animation"""
        pass  # Qt handles this automatically
    
    def _stop_indeterminate(self):
        """Stop indeterminate animation"""
        pass
    
    def get_progress(self) -> int:
        """Get current progress value"""
        return self.current_value
