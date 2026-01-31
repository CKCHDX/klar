"""
Control Center Navigation
Tab-based navigation widget for Control Center modules
"""

import logging
from typing import Optional, Dict

from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QKeySequence, QAction, QShortcut

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
from gui.control_center.control_center_config import ControlCenterConfig

logger = logging.getLogger(__name__)


class ControlCenterNavigation(QTabWidget):
    """Tab navigation widget for Control Center modules"""
    
    # Signals
    module_changed = pyqtSignal(str)  # Emits module ID when tab changes
    module_refresh_requested = pyqtSignal(str)  # Emits module ID to refresh
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._modules = {}
        self._module_widgets = {}
        
        # Configure tab widget
        self._setup_ui()
        self._setup_shortcuts()
        self._setup_connections()
        
        logger.info("Control Center Navigation initialized")
    
    def _setup_ui(self):
        """Setup UI components"""
        # Tab position and style
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.setMovable(False)
        self.setTabsClosable(False)
        self.setDocumentMode(True)
        
        # Icon size
        self.setIconSize(QSize(24, 24))
        
        # Apply custom styling
        self._apply_styles()
    
    def _apply_styles(self):
        """Apply custom tab styling"""
        tab_style = f"""
            QTabWidget::pane {{
                border: 1px solid {GUIConfig.COLORS['border']};
                background-color: {GUIConfig.COLORS['bg_primary']};
                border-top: 2px solid {GUIConfig.COLORS['primary']};
            }}
            
            QTabBar::tab {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_secondary']};
                padding: 12px 20px;
                margin-right: 2px;
                border: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 150px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {GUIConfig.COLORS['primary']};
                color: {GUIConfig.COLORS['text_primary']};
                font-weight: bold;
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {GUIConfig.COLORS['bg_tertiary']};
                color: {GUIConfig.COLORS['text_primary']};
            }}
            
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
        """
        self.setStyleSheet(tab_style)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts for tab switching"""
        modules = ControlCenterConfig.MODULES
        
        for module_id, module_config in modules.items():
            shortcut_key = module_config.get('shortcut')
            if shortcut_key:
                shortcut = QShortcut(QKeySequence(shortcut_key), self)
                shortcut.activated.connect(
                    lambda mid=module_id: self._activate_module(mid)
                )
                logger.debug(f"Shortcut {shortcut_key} registered for module {module_id}")
    
    def _setup_connections(self):
        """Setup signal connections"""
        self.currentChanged.connect(self._on_tab_changed)
        self.tabBarDoubleClicked.connect(self._on_tab_double_clicked)
    
    def add_module(self, module_id: str, widget: QWidget):
        """Add a module tab"""
        config = ControlCenterConfig.get_module_config(module_id)
        
        if not config:
            logger.error(f"Module config not found for: {module_id}")
            return
        
        # Get module details
        name = config.get('name', module_id.upper())
        tooltip = config.get('tooltip', '')
        icon_name = config.get('icon', 'default')
        
        # Load icon if available
        icon_path = GUIConfig.get_icon_path(icon_name)
        icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()
        
        # Add tab
        index = self.addTab(widget, icon, name)
        self.setTabToolTip(index, tooltip)
        
        # Enable context menu on tab bar (set once)
        if not hasattr(self, '_context_menu_enabled'):
            self.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.tabBar().customContextMenuRequested.connect(self.show_module_context_menu)
            self._context_menu_enabled = True
        
        # Store references
        self._modules[module_id] = config
        self._module_widgets[module_id] = widget
        
        logger.info(f"Module added: {module_id} - {name}")
    
    def remove_module(self, module_id: str):
        """Remove a module tab"""
        if module_id in self._module_widgets:
            widget = self._module_widgets[module_id]
            index = self.indexOf(widget)
            if index >= 0:
                self.removeTab(index)
                del self._module_widgets[module_id]
                del self._modules[module_id]
                logger.info(f"Module removed: {module_id}")
    
    def get_current_module_id(self) -> Optional[str]:
        """Get currently active module ID"""
        current_widget = self.currentWidget()
        for module_id, widget in self._module_widgets.items():
            if widget == current_widget:
                return module_id
        return None
    
    def set_active_module(self, module_id: str):
        """Set active module by ID"""
        if module_id in self._module_widgets:
            widget = self._module_widgets[module_id]
            index = self.indexOf(widget)
            if index >= 0:
                self.setCurrentIndex(index)
                logger.info(f"Active module set to: {module_id}")
    
    def _activate_module(self, module_id: str):
        """Activate module (used by shortcuts)"""
        self.set_active_module(module_id)
    
    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        module_id = self.get_current_module_id()
        if module_id:
            logger.info(f"Module changed to: {module_id}")
            self.module_changed.emit(module_id)
    
    def _on_tab_double_clicked(self, index: int):
        """Handle tab double-click (optional refresh)"""
        widget = self.widget(index)
        for module_id, mod_widget in self._module_widgets.items():
            if mod_widget == widget:
                logger.info(f"Module refresh requested: {module_id}")
                self.module_refresh_requested.emit(module_id)
                break
    
    def show_module_context_menu(self, position):
        """Show context menu for tab"""
        tab_bar = self.tabBar()
        index = tab_bar.tabAt(position)
        
        if index < 0:
            return
        
        # Get module ID for this tab
        widget = self.widget(index)
        module_id = None
        for mid, w in self._module_widgets.items():
            if w == widget:
                module_id = mid
                break
        
        if not module_id:
            return
        
        # Create context menu
        menu = QMenu(self)
        menu.setStyleSheet(GUIConfig.get_default_stylesheet())
        
        # Refresh action
        refresh_action = QAction("Refresh Module", self)
        refresh_action.triggered.connect(
            lambda: self.module_refresh_requested.emit(module_id)
        )
        menu.addAction(refresh_action)
        
        menu.addSeparator()
        
        # Module info action
        info_action = QAction("Module Info", self)
        info_action.triggered.connect(
            lambda: self._show_module_info(module_id)
        )
        menu.addAction(info_action)
        
        # Show menu
        menu.exec(tab_bar.mapToGlobal(position))
    
    def _show_module_info(self, module_id: str):
        """Show module information dialog"""
        config = self._modules.get(module_id, {})
        
        info_text = f"""
        <h3>{config.get('title', 'Module')}</h3>
        <p><b>ID:</b> {module_id}</p>
        <p><b>Description:</b> {config.get('description', 'No description')}</p>
        <p><b>Shortcut:</b> {config.get('shortcut', 'None')}</p>
        <p><b>Update Interval:</b> {ControlCenterConfig.get_update_interval(module_id) / 1000}s</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Module Information")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet(GUIConfig.get_default_stylesheet())
        msg.exec()
    
    def get_module_count(self) -> int:
        """Get number of modules"""
        return len(self._modules)
    
    def get_module_list(self) -> list:
        """Get list of module IDs"""
        return list(self._modules.keys())
    
    def refresh_current_module(self):
        """Refresh currently active module"""
        module_id = self.get_current_module_id()
        if module_id:
            self.module_refresh_requested.emit(module_id)
