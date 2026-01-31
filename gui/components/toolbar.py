"""
Toolbar Component
Application toolbar with quick action buttons
"""

from typing import Optional, Callable, Dict
from PyQt6.QtWidgets import QToolBar, QWidget, QLabel, QLineEdit, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging

logger = logging.getLogger(__name__)


class ToolBar(QToolBar):
    """Application toolbar component"""
    
    # Signals
    action_triggered = pyqtSignal(str)  # Action name
    search_requested = pyqtSignal(str)  # Search text
    
    def __init__(self, title: str = "Toolbar", parent=None):
        """
        Initialize toolbar
        
        Args:
            title: Toolbar title
            parent: Parent widget
        """
        super().__init__(title, parent)
        self.actions_dict = {}
        self.widgets_dict = {}
        
        self.setMovable(False)
        self.setFloatable(False)
        
        self._setup_actions()
        self._apply_styles()
        
        logger.debug("ToolBar created")
    
    def _setup_actions(self):
        """Setup toolbar actions"""
        # New
        self.add_action_button(
            "New",
            "new",
            "Create new"
        )
        
        # Open
        self.add_action_button(
            "Open",
            "open",
            "Open file"
        )
        
        # Save
        self.add_action_button(
            "Save",
            "save",
            "Save file"
        )
        
        self.addSeparator()
        
        # Refresh
        self.add_action_button(
            "Refresh",
            "refresh",
            "Refresh data"
        )
        
        # Start
        self.add_action_button(
            "Start",
            "start",
            "Start operation"
        )
        
        # Stop
        self.add_action_button(
            "Stop",
            "stop",
            "Stop operation"
        )
        
        self.addSeparator()
        
        # Search box
        search_label = QLabel("Search:")
        search_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']}; padding: 0 8px;")
        self.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setFixedWidth(200)
        self.search_box.returnPressed.connect(self._on_search)
        self.addWidget(self.search_box)
        self.widgets_dict['search'] = self.search_box
        
        # Search button
        self.add_action_button(
            "🔍",
            "search",
            "Search",
            self._on_search
        )
        
        # Add spacer to push remaining items to the right
        spacer = QWidget()
        spacer.setSizePolicy(QWidget.SizePolicy.Policy.Expanding, QWidget.SizePolicy.Policy.Preferred)
        self.addWidget(spacer)
        
        # Settings
        self.add_action_button(
            "Settings",
            "settings",
            "Open settings"
        )
    
    def _apply_styles(self):
        """Apply styling to toolbar"""
        self.setStyleSheet(Styles.get_toolbar_style() + f"""
            QLineEdit {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
                padding: 6px;
            }}
        """)
    
    def add_action_button(
        self,
        text: str,
        name: str,
        tooltip: str = "",
        callback: Optional[Callable] = None
    ) -> QAction:
        """
        Add an action button to toolbar
        
        Args:
            text: Button text
            name: Action name (internal)
            tooltip: Tooltip text
            callback: Optional callback function
            
        Returns:
            Created QAction
        """
        action = QAction(text, self)
        
        if tooltip:
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)
        
        if callback:
            action.triggered.connect(callback)
        else:
            action.triggered.connect(lambda: self._on_action_triggered(name))
        
        self.addAction(action)
        self.actions_dict[name] = action
        
        return action
    
    def add_toggle_button(
        self,
        text: str,
        name: str,
        tooltip: str = "",
        initial_state: bool = False,
        callback: Optional[Callable] = None
    ) -> QAction:
        """
        Add a toggle button to toolbar
        
        Args:
            text: Button text
            name: Action name
            tooltip: Tooltip text
            initial_state: Initial checked state
            callback: Optional callback function
            
        Returns:
            Created QAction
        """
        action = self.add_action_button(text, name, tooltip, callback)
        action.setCheckable(True)
        action.setChecked(initial_state)
        return action
    
    def add_widget(self, widget: QWidget, name: str = ""):
        """
        Add a custom widget to toolbar
        
        Args:
            widget: Widget to add
            name: Optional widget name
        """
        self.addWidget(widget)
        if name:
            self.widgets_dict[name] = widget
    
    def add_combo_box(
        self,
        items: list,
        name: str,
        tooltip: str = "",
        callback: Optional[Callable] = None
    ) -> QComboBox:
        """
        Add a combo box to toolbar
        
        Args:
            items: Combo box items
            name: Combo box name
            tooltip: Tooltip text
            callback: Optional callback function
            
        Returns:
            Created QComboBox
        """
        combo = QComboBox()
        combo.addItems(items)
        
        if tooltip:
            combo.setToolTip(tooltip)
        
        if callback:
            combo.currentTextChanged.connect(callback)
        
        self.addWidget(combo)
        self.widgets_dict[name] = combo
        
        return combo
    
    def _on_action_triggered(self, name: str):
        """Handle action triggered"""
        self.action_triggered.emit(name)
        logger.debug(f"Toolbar action: {name}")
    
    def _on_search(self):
        """Handle search"""
        text = self.search_box.text()
        self.search_requested.emit(text)
        logger.debug(f"Search: {text}")
    
    def get_action(self, name: str) -> Optional[QAction]:
        """
        Get action by name
        
        Args:
            name: Action name
            
        Returns:
            QAction or None
        """
        return self.actions_dict.get(name)
    
    def get_widget(self, name: str) -> Optional[QWidget]:
        """
        Get widget by name
        
        Args:
            name: Widget name
            
        Returns:
            QWidget or None
        """
        return self.widgets_dict.get(name)
    
    def set_action_enabled(self, name: str, enabled: bool):
        """
        Enable/disable an action
        
        Args:
            name: Action name
            enabled: Enable state
        """
        action = self.get_action(name)
        if action:
            action.setEnabled(enabled)
    
    def set_action_checked(self, name: str, checked: bool):
        """
        Set action checked state
        
        Args:
            name: Action name
            checked: Checked state
        """
        action = self.get_action(name)
        if action and action.isCheckable():
            action.setChecked(checked)
    
    def connect_action(self, name: str, callback: Callable):
        """
        Connect action to callback
        
        Args:
            name: Action name
            callback: Callback function
        """
        action = self.get_action(name)
        if action:
            action.triggered.connect(callback)
    
    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_box.text()
    
    def set_search_text(self, text: str):
        """
        Set search text
        
        Args:
            text: Search text
        """
        self.search_box.setText(text)
    
    def clear_search(self):
        """Clear search text"""
        self.search_box.clear()
