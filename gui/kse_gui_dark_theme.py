"""
Dark Theme Stylesheet for KSE GUI
Professional dark theme with modern aesthetics
"""

from gui.kse_gui_config import GUIConfig

def get_dark_theme() -> str:
    """Get complete dark theme stylesheet"""
    
    colors = GUIConfig.COLORS
    
    return f"""
/* ===== MAIN WINDOW ===== */
QMainWindow, QDialog {{
    background-color: {colors['bg_primary']};
    color: {colors['text_primary']};
}}

/* ===== WIDGETS ===== */
QWidget {{
    background-color: {colors['bg_primary']};
    color: {colors['text_primary']};
    font-family: {GUIConfig.FONTS['family']};
    font-size: {GUIConfig.FONTS['size']['normal']}pt;
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background-color: {colors['primary']};
    color: {colors['text_primary']};
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {colors['secondary']};
}}

QPushButton:pressed {{
    background-color: #0D47A1;
}}

QPushButton:disabled {{
    background-color: {colors['bg_tertiary']};
    color: {colors['text_secondary']};
}}

QPushButton[buttonType="success"] {{
    background-color: {colors['success']};
}}

QPushButton[buttonType="danger"] {{
    background-color: {colors['error']};
}}

QPushButton[buttonType="warning"] {{
    background-color: {colors['warning']};
}}

/* ===== INPUT FIELDS ===== */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    padding: 6px;
    selection-background-color: {colors['primary']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {colors['primary']};
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {colors['bg_primary']};
    color: {colors['text_secondary']};
}}

/* ===== COMBO BOX ===== */
QComboBox {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    padding: 6px;
    min-width: 100px;
}}

QComboBox:hover {{
    border: 1px solid {colors['primary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {colors['text_secondary']};
    margin-right: 5px;
}}

QComboBox QAbstractItemView {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    selection-background-color: {colors['primary']};
}}

/* ===== LISTS AND TREES ===== */
QListWidget, QTreeWidget, QTreeView {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    outline: none;
}}

QListWidget::item, QTreeWidget::item, QTreeView::item {{
    padding: 4px;
}}

QListWidget::item:selected, QTreeWidget::item:selected, QTreeView::item:selected {{
    background-color: {colors['primary']};
    color: {colors['text_primary']};
}}

QListWidget::item:hover, QTreeWidget::item:hover, QTreeView::item:hover {{
    background-color: {colors['bg_tertiary']};
}}

/* ===== TABLES ===== */
QTableWidget, QTableView {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    gridline-color: {colors['border']};
    selection-background-color: {colors['primary']};
}}

QTableWidget::item, QTableView::item {{
    padding: 4px;
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {colors['primary']};
}}

QHeaderView::section {{
    background-color: {colors['bg_tertiary']};
    color: {colors['text_primary']};
    border: none;
    border-bottom: 1px solid {colors['border']};
    border-right: 1px solid {colors['border']};
    padding: 8px;
    font-weight: bold;
}}

QHeaderView::section:hover {{
    background-color: {colors['border']};
}}

/* ===== PROGRESS BAR ===== */
QProgressBar {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    text-align: center;
    height: 20px;
}}

QProgressBar::chunk {{
    background-color: {colors['primary']};
    border-radius: 3px;
}}

/* ===== TAB WIDGET ===== */
QTabWidget::pane {{
    border: 1px solid {colors['border']};
    background-color: {colors['bg_primary']};
    top: -1px;
}}

QTabBar::tab {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_secondary']};
    padding: 8px 16px;
    border: none;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    background-color: {colors['bg_primary']};
    color: {colors['text_primary']};
    border-bottom: 2px solid {colors['primary']};
}}

QTabBar::tab:hover {{
    background-color: {colors['bg_tertiary']};
    color: {colors['text_primary']};
}}

/* ===== GROUP BOX ===== */
QGroupBox {{
    background-color: {colors['bg_secondary']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    padding: 12px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: {colors['primary']};
    font-weight: bold;
}}

/* ===== LABELS ===== */
QLabel {{
    background-color: transparent;
    color: {colors['text_primary']};
}}

QLabel[labelType="title"] {{
    font-size: {GUIConfig.FONTS['size']['title']}pt;
    font-weight: bold;
}}

QLabel[labelType="header"] {{
    font-size: {GUIConfig.FONTS['size']['header']}pt;
    font-weight: bold;
    color: {colors['primary']};
}}

QLabel[labelType="secondary"] {{
    color: {colors['text_secondary']};
}}

/* ===== STATUS BAR ===== */
QStatusBar {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_secondary']};
    border-top: 1px solid {colors['border']};
}}

/* ===== MENU BAR ===== */
QMenuBar {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_primary']};
    border-bottom: 1px solid {colors['border']};
}}

QMenuBar::item {{
    padding: 6px 12px;
    background-color: transparent;
}}

QMenuBar::item:selected {{
    background-color: {colors['primary']};
}}

QMenuBar::item:pressed {{
    background-color: {colors['secondary']};
}}

/* ===== MENU ===== */
QMenu {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
}}

QMenu::item {{
    padding: 6px 24px 6px 12px;
}}

QMenu::item:selected {{
    background-color: {colors['primary']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {colors['border']};
    margin: 4px 0;
}}

/* ===== TOOL BAR ===== */
QToolBar {{
    background-color: {colors['bg_secondary']};
    border-bottom: 1px solid {colors['border']};
    spacing: 8px;
    padding: 4px;
}}

QToolButton {{
    background-color: transparent;
    color: {colors['text_primary']};
    border: none;
    border-radius: 4px;
    padding: 8px;
}}

QToolButton:hover {{
    background-color: {colors['bg_tertiary']};
}}

QToolButton:pressed {{
    background-color: {colors['primary']};
}}

/* ===== SCROLL BAR ===== */
QScrollBar:vertical {{
    background-color: {colors['bg_secondary']};
    width: 12px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background-color: {colors['border']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {colors['text_secondary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background-color: {colors['bg_secondary']};
    height: 12px;
    border: none;
}}

QScrollBar::handle:horizontal {{
    background-color: {colors['border']};
    border-radius: 6px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {colors['text_secondary']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

/* ===== CHECK BOX ===== */
QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {colors['border']};
    border-radius: 3px;
    background-color: {colors['bg_secondary']};
}}

QCheckBox::indicator:hover {{
    border: 1px solid {colors['primary']};
}}

QCheckBox::indicator:checked {{
    background-color: {colors['primary']};
    image: none;
}}

/* ===== RADIO BUTTON ===== */
QRadioButton {{
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {colors['border']};
    border-radius: 9px;
    background-color: {colors['bg_secondary']};
}}

QRadioButton::indicator:hover {{
    border: 1px solid {colors['primary']};
}}

QRadioButton::indicator:checked {{
    background-color: {colors['primary']};
    border: 1px solid {colors['primary']};
}}

/* ===== SLIDER ===== */
QSlider::groove:horizontal {{
    height: 6px;
    background-color: {colors['bg_secondary']};
    border: 1px solid {colors['border']};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background-color: {colors['primary']};
    border: 1px solid {colors['primary']};
    width: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background-color: {colors['secondary']};
}}

/* ===== TOOL TIP ===== */
QToolTip {{
    background-color: {colors['bg_tertiary']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    padding: 4px;
}}

/* ===== SPLITTER ===== */
QSplitter::handle {{
    background-color: {colors['border']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {colors['primary']};
}}

/* ===== FRAME ===== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    border: 1px solid {colors['border']};
}}

/* ===== CUSTOM CARDS ===== */
QFrame[frameType="card"] {{
    background-color: {colors['bg_secondary']};
    border: 1px solid {colors['border']};
    border-radius: 8px;
    padding: 12px;
}}

QFrame[frameType="metric"] {{
    background-color: {colors['bg_tertiary']};
    border: 1px solid {colors['border']};
    border-radius: 8px;
    padding: 16px;
}}

/* ===== DIALOG ===== */
QDialog {{
    background-color: {colors['bg_primary']};
}}

QDialogButtonBox QPushButton {{
    min-width: 80px;
}}
"""
