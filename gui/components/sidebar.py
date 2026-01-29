"""
Sidebar Component
Navigation sidebar with collapsible sections
"""

from typing import Optional, Callable, Dict, List
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QWidget, QScrollArea, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging

logger = logging.getLogger(__name__)


class SideBar(QFrame):
    """Navigation sidebar component"""
    
    # Signals
    item_selected = pyqtSignal(str)  # Item name
    section_toggled = pyqtSignal(str, bool)  # Section name, expanded state
    
    def __init__(
        self,
        width: int = 250,
        collapsible: bool = True,
        parent=None
    ):
        """
        Initialize sidebar
        
        Args:
            width: Sidebar width
            collapsible: Allow sidebar collapse
            parent: Parent widget
        """
        super().__init__(parent)
        self.sidebar_width = width
        self.collapsible = collapsible
        self.is_collapsed = False
        
        self.sections = {}
        self.items = {}
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        self.setFixedWidth(width)
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug("SideBar created")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 12, 12, 12)
        
        self.title_label = QLabel("Navigation")
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['title'])
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        if self.collapsible:
            self.collapse_btn = QPushButton("◀")
            self.collapse_btn.setFixedSize(24, 24)
            self.collapse_btn.clicked.connect(self.toggle_collapse)
            self.collapse_btn.setToolTip("Collapse sidebar")
            header_layout.addWidget(self.collapse_btn)
        
        layout.addWidget(header)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {GUIConfig.COLORS['border']};")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.setSpacing(4)
        self.content_layout.addStretch()
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
    
    def _apply_styles(self):
        """Apply styling to sidebar"""
        self.setStyleSheet(Styles.get_sidebar_style())
    
    def add_section(self, name: str, title: str, expanded: bool = True) -> 'SideBarSection':
        """
        Add a section to sidebar
        
        Args:
            name: Section name (internal)
            title: Section title
            expanded: Initially expanded
            
        Returns:
            Created SideBarSection
        """
        section = SideBarSection(title, expanded, self)
        section.toggled.connect(lambda exp: self.section_toggled.emit(name, exp))
        
        # Insert before stretch
        self.content_layout.insertWidget(self.content_layout.count() - 1, section)
        self.sections[name] = section
        
        return section
    
    def add_item(
        self,
        section_name: str,
        item_name: str,
        item_title: str,
        icon: Optional[str] = None,
        callback: Optional[Callable] = None
    ) -> QPushButton:
        """
        Add an item to a section
        
        Args:
            section_name: Section name
            item_name: Item name (internal)
            item_title: Item display title
            icon: Optional icon
            callback: Optional callback function
            
        Returns:
            Created QPushButton
        """
        section = self.sections.get(section_name)
        if not section:
            logger.warning(f"Section '{section_name}' not found")
            return None
        
        button = QPushButton(item_title)
        button.setCheckable(True)
        button.clicked.connect(lambda: self._on_item_clicked(item_name, callback))
        
        section.add_item(button)
        self.button_group.addButton(button)
        self.items[item_name] = button
        
        return button
    
    def add_simple_item(
        self,
        item_name: str,
        item_title: str,
        callback: Optional[Callable] = None
    ) -> QPushButton:
        """
        Add a simple item (no section)
        
        Args:
            item_name: Item name
            item_title: Item title
            callback: Optional callback
            
        Returns:
            Created QPushButton
        """
        button = QPushButton(item_title)
        button.setCheckable(True)
        button.clicked.connect(lambda: self._on_item_clicked(item_name, callback))
        
        # Insert before stretch
        self.content_layout.insertWidget(self.content_layout.count() - 1, button)
        self.button_group.addButton(button)
        self.items[item_name] = button
        
        return button
    
    def _on_item_clicked(self, name: str, callback: Optional[Callable] = None):
        """Handle item click"""
        self.item_selected.emit(name)
        
        if callback:
            callback()
        
        logger.debug(f"Sidebar item selected: {name}")
    
    def select_item(self, name: str):
        """
        Select an item
        
        Args:
            name: Item name
        """
        button = self.items.get(name)
        if button:
            button.setChecked(True)
    
    def get_selected_item(self) -> Optional[str]:
        """
        Get currently selected item
        
        Returns:
            Item name or None
        """
        for name, button in self.items.items():
            if button.isChecked():
                return name
        return None
    
    def set_item_enabled(self, name: str, enabled: bool):
        """
        Enable/disable an item
        
        Args:
            name: Item name
            enabled: Enable state
        """
        button = self.items.get(name)
        if button:
            button.setEnabled(enabled)
    
    def toggle_collapse(self):
        """Toggle sidebar collapse"""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            self.setFixedWidth(50)
            self.title_label.hide()
            if hasattr(self, 'collapse_btn'):
                self.collapse_btn.setText("▶")
                self.collapse_btn.setToolTip("Expand sidebar")
            
            # Hide section titles and item text
            for section in self.sections.values():
                section.hide_text()
            
        else:
            self.setFixedWidth(self.sidebar_width)
            self.title_label.show()
            if hasattr(self, 'collapse_btn'):
                self.collapse_btn.setText("◀")
                self.collapse_btn.setToolTip("Collapse sidebar")
            
            # Show section titles and item text
            for section in self.sections.values():
                section.show_text()
    
    def set_title(self, title: str):
        """
        Set sidebar title
        
        Args:
            title: Title text
        """
        self.title_label.setText(title)


class SideBarSection(QWidget):
    """Collapsible section in sidebar"""
    
    toggled = pyqtSignal(bool)  # Expanded state
    
    def __init__(self, title: str, expanded: bool = True, parent=None):
        super().__init__(parent)
        self.title = title
        self.is_expanded = expanded
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(2)
        
        # Section header
        self.header_btn = QPushButton(f"{'▼' if self.is_expanded else '▶'} {self.title}")
        self.header_btn.setCheckable(False)
        self.header_btn.clicked.connect(self.toggle)
        self.header_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {GUIConfig.COLORS['text_secondary']};
                border: none;
                padding: 6px;
                text-align: left;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {GUIConfig.COLORS['text_primary']};
            }}
        """)
        layout.addWidget(self.header_btn)
        
        # Items container
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setContentsMargins(8, 0, 0, 0)
        self.items_layout.setSpacing(2)
        self.items_widget.setVisible(self.is_expanded)
        
        layout.addWidget(self.items_widget)
    
    def add_item(self, button: QPushButton):
        """Add item button to section"""
        self.items_layout.addWidget(button)
    
    def toggle(self):
        """Toggle section expansion"""
        self.is_expanded = not self.is_expanded
        self.items_widget.setVisible(self.is_expanded)
        self.header_btn.setText(f"{'▼' if self.is_expanded else '▶'} {self.title}")
        self.toggled.emit(self.is_expanded)
    
    def hide_text(self):
        """Hide text (for collapsed sidebar)"""
        self.header_btn.setText("▪")
    
    def show_text(self):
        """Show text (for expanded sidebar)"""
        self.header_btn.setText(f"{'▼' if self.is_expanded else '▶'} {self.title}")
