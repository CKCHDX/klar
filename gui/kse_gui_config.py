"""
KSE GUI Configuration
Manages GUI settings, themes, and global styling
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json

class GUIConfig:
    """GUI configuration manager"""
    
    # Window dimensions
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    
    # Theme settings
    THEME = "dark"  # "dark" or "light"
    
    # Color scheme (Dark theme)
    COLORS = {
        'primary': '#2196F3',      # Blue
        'secondary': '#1976D2',    # Dark blue
        'success': '#4CAF50',      # Green
        'warning': '#FF9800',      # Orange
        'error': '#F44336',        # Red
        'info': '#00BCD4',         # Cyan
        
        # Dark theme colors
        'bg_primary': '#1E1E1E',   # Main background
        'bg_secondary': '#252525', # Secondary background
        'bg_tertiary': '#2D2D2D',  # Tertiary background
        'text_primary': '#FFFFFF', # Main text
        'text_secondary': '#B0B0B0', # Secondary text
        'border': '#3E3E3E',       # Border color
        
        # Light theme colors (alternative)
        'light_bg': '#FFFFFF',
        'light_text': '#000000',
    }
    
    # Font settings
    FONTS = {
        'family': 'Segoe UI',
        'size': {
            'small': 9,
            'normal': 10,
            'medium': 11,
            'large': 12,
            'title': 14,
            'header': 16,
        }
    }
    
    # Status colors
    STATUS_COLORS = {
        'running': COLORS['success'],
        'stopped': COLORS['error'],
        'warning': COLORS['warning'],
        'idle': COLORS['text_secondary'],
        'unknown': COLORS['text_secondary'],
    }
    
    # Chart colors
    CHART_COLORS = [
        '#2196F3',  # Blue
        '#4CAF50',  # Green
        '#FF9800',  # Orange
        '#9C27B0',  # Purple
        '#F44336',  # Red
        '#00BCD4',  # Cyan
        '#FFEB3B',  # Yellow
        '#795548',  # Brown
    ]
    
    # Icon paths
    ICONS_DIR = Path(__file__).parent.parent / 'assets' / 'icons'
    
    # Animations
    ANIMATION_DURATION = 200  # milliseconds
    
    # Update intervals (milliseconds)
    UPDATE_INTERVALS = {
        'fast': 1000,      # 1 second
        'normal': 5000,    # 5 seconds
        'slow': 10000,     # 10 seconds
    }
    
    @classmethod
    def get_color(cls, name: str) -> str:
        """Get color by name"""
        return cls.COLORS.get(name, cls.COLORS['text_primary'])
    
    @classmethod
    def get_font_size(cls, size_name: str = 'normal') -> int:
        """Get font size by name"""
        return cls.FONTS['size'].get(size_name, 10)
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """Get status color"""
        return cls.STATUS_COLORS.get(status.lower(), cls.STATUS_COLORS['unknown'])
    
    @classmethod
    def get_icon_path(cls, icon_name: str) -> Path:
        """Get icon file path"""
        return cls.ICONS_DIR / f"{icon_name}.png"
    
    @classmethod
    def load_theme(cls, theme_name: str = 'dark') -> str:
        """Load theme stylesheet"""
        theme_file = Path(__file__).parent.parent / 'assets' / 'themes' / f'{theme_name}.qss'
        if theme_file.exists():
            return theme_file.read_text()
        return cls.get_default_stylesheet()
    
    @classmethod
    def get_default_stylesheet(cls) -> str:
        """Get default dark theme stylesheet"""
        return f"""
        QMainWindow, QDialog {{
            background-color: {cls.COLORS['bg_primary']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QWidget {{
            background-color: {cls.COLORS['bg_primary']};
            color: {cls.COLORS['text_primary']};
            font-family: {cls.FONTS['family']};
            font-size: {cls.FONTS['size']['normal']}pt;
        }}
        
        QPushButton {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text_primary']};
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {cls.COLORS['secondary']};
        }}
        
        QPushButton:pressed {{
            background-color: #0D47A1;
        }}
        
        QPushButton:disabled {{
            background-color: {cls.COLORS['bg_tertiary']};
            color: {cls.COLORS['text_secondary']};
        }}
        
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            padding: 6px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {cls.COLORS['primary']};
        }}
        
        QComboBox {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            padding: 6px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {cls.COLORS['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QListWidget, QTreeWidget, QTableWidget {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
        }}
        
        QHeaderView::section {{
            background-color: {cls.COLORS['bg_tertiary']};
            color: {cls.COLORS['text_primary']};
            border: none;
            padding: 6px;
        }}
        
        QProgressBar {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {cls.COLORS['primary']};
            border-radius: 3px;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {cls.COLORS['border']};
            background-color: {cls.COLORS['bg_primary']};
        }}
        
        QTabBar::tab {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_secondary']};
            padding: 8px 16px;
            border: none;
        }}
        
        QTabBar::tab:selected {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {cls.COLORS['bg_tertiary']};
        }}
        
        QLabel {{
            background-color: transparent;
            color: {cls.COLORS['text_primary']};
        }}
        
        QGroupBox {{
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: {cls.COLORS['primary']};
        }}
        
        QStatusBar {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_secondary']};
        }}
        
        QMenuBar {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {cls.COLORS['primary']};
        }}
        
        QMenu {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
        }}
        
        QMenu::item:selected {{
            background-color: {cls.COLORS['primary']};
        }}
        
        QScrollBar:vertical {{
            background-color: {cls.COLORS['bg_secondary']};
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['border']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['text_secondary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {cls.COLORS['bg_secondary']};
            height: 12px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {cls.COLORS['border']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.COLORS['text_secondary']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        """
