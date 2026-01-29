"""
Reusable GUI Styles
Common style definitions for GUI components
"""

from gui.kse_gui_config import GUIConfig

class Styles:
    """Reusable style definitions"""
    
    @staticmethod
    def get_card_style(color: str = None) -> str:
        """Get card style with optional custom color"""
        bg_color = color or GUIConfig.COLORS['bg_secondary']
        return f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """
    
    @staticmethod
    def get_button_style(color: str = None, size: str = 'normal') -> str:
        """Get button style with optional custom color"""
        bg_color = color or GUIConfig.COLORS['primary']
        
        sizes = {
            'small': 'padding: 4px 8px; font-size: 9pt;',
            'normal': 'padding: 8px 16px; font-size: 10pt;',
            'large': 'padding: 12px 24px; font-size: 12pt;',
        }
        padding = sizes.get(size, sizes['normal'])
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {GUIConfig.COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                {padding}
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {GUIConfig.COLORS['secondary']};
            }}
            QPushButton:pressed {{
                background-color: #0D47A1;
            }}
            QPushButton:disabled {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
                color: {GUIConfig.COLORS['text_secondary']};
            }}
        """
    
    @staticmethod
    def get_success_button_style() -> str:
        """Get success/green button style"""
        return Styles.get_button_style(GUIConfig.COLORS['success'])
    
    @staticmethod
    def get_danger_button_style() -> str:
        """Get danger/red button style"""
        return Styles.get_button_style(GUIConfig.COLORS['error'])
    
    @staticmethod
    def get_warning_button_style() -> str:
        """Get warning/orange button style"""
        return Styles.get_button_style(GUIConfig.COLORS['warning'])
    
    @staticmethod
    def get_title_style(size: str = 'title') -> str:
        """Get title/header style"""
        font_size = GUIConfig.get_font_size(size)
        return f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_primary']};
                font-size: {font_size}pt;
                font-weight: bold;
                background-color: transparent;
            }}
        """
    
    @staticmethod
    def get_status_label_style(status: str) -> str:
        """Get status label style with color"""
        color = GUIConfig.get_status_color(status)
        return f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                background-color: transparent;
            }}
        """
    
    @staticmethod
    def get_metric_card_style() -> str:
        """Get metric display card style"""
        return f"""
            QFrame {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 8px;
                padding: 16px;
            }}
            QLabel {{
                background-color: transparent;
            }}
        """
    
    @staticmethod
    def get_log_viewer_style() -> str:
        """Get log viewer style"""
        return f"""
            QPlainTextEdit {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                padding: 8px;
            }}
        """
    
    @staticmethod
    def get_chart_style() -> str:
        """Get chart container style"""
        return f"""
            QFrame {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """
    
    @staticmethod
    def get_sidebar_style() -> str:
        """Get sidebar style"""
        return f"""
            QFrame {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
                border-right: 1px solid {GUIConfig.COLORS['border']};
            }}
            QPushButton {{
                background-color: transparent;
                color: {GUIConfig.COLORS['text_secondary']};
                border: none;
                border-radius: 4px;
                padding: 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
            }}
            QPushButton:checked {{
                background-color: {GUIConfig.COLORS['primary']};
                color: {GUIConfig.COLORS['text_primary']};
            }}
        """
    
    @staticmethod
    def get_toolbar_style() -> str:
        """Get toolbar style"""
        return f"""
            QToolBar {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border-bottom: 1px solid {GUIConfig.COLORS['border']};
                spacing: 8px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: transparent;
                color: {GUIConfig.COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                padding: 8px;
            }}
            QToolButton:hover {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
            }}
            QToolButton:pressed {{
                background-color: {GUIConfig.COLORS['primary']};
            }}
        """
    
    @staticmethod
    def get_table_style() -> str:
        """Get table/grid style"""
        return f"""
            QTableWidget {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
                gridline-color: {GUIConfig.COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 4px;
            }}
            QTableWidget::item:selected {{
                background-color: {GUIConfig.COLORS['primary']};
            }}
            QHeaderView::section {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
                color: {GUIConfig.COLORS['text_primary']};
                border: none;
                border-bottom: 1px solid {GUIConfig.COLORS['border']};
                padding: 8px;
                font-weight: bold;
            }}
        """
