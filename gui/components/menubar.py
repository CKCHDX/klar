"""
Menu Bar Component
Application menu bar with standard menus
"""

from typing import Optional, Callable, Dict
from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction, QKeySequence
from gui.kse_gui_config import GUIConfig
import logging

logger = logging.getLogger(__name__)


class MenuBar(QMenuBar):
    """Application menu bar component"""
    
    # Signals
    menu_action_triggered = pyqtSignal(str)  # Action name
    
    def __init__(self, parent=None):
        """
        Initialize menu bar
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.actions_dict = {}
        
        self._setup_menus()
        self._apply_styles()
        
        logger.debug("MenuBar created")
    
    def _setup_menus(self):
        """Setup menu bar menus"""
        # File menu
        self.file_menu = self.addMenu("&File")
        self._add_file_menu_actions()
        
        # Edit menu
        self.edit_menu = self.addMenu("&Edit")
        self._add_edit_menu_actions()
        
        # View menu
        self.view_menu = self.addMenu("&View")
        self._add_view_menu_actions()
        
        # Tools menu
        self.tools_menu = self.addMenu("&Tools")
        self._add_tools_menu_actions()
        
        # Help menu
        self.help_menu = self.addMenu("&Help")
        self._add_help_menu_actions()
    
    def _add_file_menu_actions(self):
        """Add File menu actions"""
        # New
        new_action = self._create_action(
            "New",
            "new",
            "Ctrl+N",
            "Create new item"
        )
        self.file_menu.addAction(new_action)
        
        # Open
        open_action = self._create_action(
            "Open...",
            "open",
            "Ctrl+O",
            "Open file"
        )
        self.file_menu.addAction(open_action)
        
        # Save
        save_action = self._create_action(
            "Save",
            "save",
            "Ctrl+S",
            "Save file"
        )
        self.file_menu.addAction(save_action)
        
        # Save As
        save_as_action = self._create_action(
            "Save As...",
            "save_as",
            "Ctrl+Shift+S",
            "Save file as"
        )
        self.file_menu.addAction(save_as_action)
        
        self.file_menu.addSeparator()
        
        # Import
        import_action = self._create_action(
            "Import...",
            "import",
            "",
            "Import data"
        )
        self.file_menu.addAction(import_action)
        
        # Export
        export_action = self._create_action(
            "Export...",
            "export",
            "Ctrl+E",
            "Export data"
        )
        self.file_menu.addAction(export_action)
        
        self.file_menu.addSeparator()
        
        # Settings
        settings_action = self._create_action(
            "Settings...",
            "settings",
            "Ctrl+,",
            "Open settings"
        )
        self.file_menu.addAction(settings_action)
        
        self.file_menu.addSeparator()
        
        # Exit
        exit_action = self._create_action(
            "Exit",
            "exit",
            "Ctrl+Q",
            "Exit application"
        )
        self.file_menu.addAction(exit_action)
    
    def _add_edit_menu_actions(self):
        """Add Edit menu actions"""
        # Undo
        undo_action = self._create_action(
            "Undo",
            "undo",
            "Ctrl+Z",
            "Undo last action"
        )
        self.edit_menu.addAction(undo_action)
        
        # Redo
        redo_action = self._create_action(
            "Redo",
            "redo",
            "Ctrl+Y",
            "Redo action"
        )
        self.edit_menu.addAction(redo_action)
        
        self.edit_menu.addSeparator()
        
        # Cut
        cut_action = self._create_action(
            "Cut",
            "cut",
            "Ctrl+X",
            "Cut selection"
        )
        self.edit_menu.addAction(cut_action)
        
        # Copy
        copy_action = self._create_action(
            "Copy",
            "copy",
            "Ctrl+C",
            "Copy selection"
        )
        self.edit_menu.addAction(copy_action)
        
        # Paste
        paste_action = self._create_action(
            "Paste",
            "paste",
            "Ctrl+V",
            "Paste from clipboard"
        )
        self.edit_menu.addAction(paste_action)
        
        self.edit_menu.addSeparator()
        
        # Select All
        select_all_action = self._create_action(
            "Select All",
            "select_all",
            "Ctrl+A",
            "Select all"
        )
        self.edit_menu.addAction(select_all_action)
        
        self.edit_menu.addSeparator()
        
        # Find
        find_action = self._create_action(
            "Find...",
            "find",
            "Ctrl+F",
            "Find text"
        )
        self.edit_menu.addAction(find_action)
    
    def _add_view_menu_actions(self):
        """Add View menu actions"""
        # Refresh
        refresh_action = self._create_action(
            "Refresh",
            "refresh",
            "F5",
            "Refresh view"
        )
        self.view_menu.addAction(refresh_action)
        
        self.view_menu.addSeparator()
        
        # Toggle Sidebar
        sidebar_action = self._create_action(
            "Toggle Sidebar",
            "toggle_sidebar",
            "Ctrl+B",
            "Show/hide sidebar"
        )
        sidebar_action.setCheckable(True)
        sidebar_action.setChecked(True)
        self.view_menu.addAction(sidebar_action)
        
        # Toggle Toolbar
        toolbar_action = self._create_action(
            "Toggle Toolbar",
            "toggle_toolbar",
            "",
            "Show/hide toolbar"
        )
        toolbar_action.setCheckable(True)
        toolbar_action.setChecked(True)
        self.view_menu.addAction(toolbar_action)
        
        # Toggle Status Bar
        statusbar_action = self._create_action(
            "Toggle Status Bar",
            "toggle_statusbar",
            "",
            "Show/hide status bar"
        )
        statusbar_action.setCheckable(True)
        statusbar_action.setChecked(True)
        self.view_menu.addAction(statusbar_action)
        
        self.view_menu.addSeparator()
        
        # Fullscreen
        fullscreen_action = self._create_action(
            "Fullscreen",
            "fullscreen",
            "F11",
            "Toggle fullscreen"
        )
        fullscreen_action.setCheckable(True)
        self.view_menu.addAction(fullscreen_action)
    
    def _add_tools_menu_actions(self):
        """Add Tools menu actions"""
        # Snapshots
        snapshot_action = self._create_action(
            "Manage Snapshots...",
            "manage_snapshots",
            "",
            "Manage system snapshots"
        )
        self.tools_menu.addAction(snapshot_action)
        
        # Domains
        domains_action = self._create_action(
            "Select Domains...",
            "select_domains",
            "",
            "Select active domains"
        )
        self.tools_menu.addAction(domains_action)
        
        self.tools_menu.addSeparator()
        
        # Clear Logs
        clear_logs_action = self._create_action(
            "Clear Logs",
            "clear_logs",
            "",
            "Clear application logs"
        )
        self.tools_menu.addAction(clear_logs_action)
        
        # Clear Cache
        clear_cache_action = self._create_action(
            "Clear Cache",
            "clear_cache",
            "",
            "Clear application cache"
        )
        self.tools_menu.addAction(clear_cache_action)
    
    def _add_help_menu_actions(self):
        """Add Help menu actions"""
        # Documentation
        docs_action = self._create_action(
            "Documentation",
            "documentation",
            "F1",
            "Open documentation"
        )
        self.help_menu.addAction(docs_action)
        
        # Quick Start
        quickstart_action = self._create_action(
            "Quick Start Guide",
            "quickstart",
            "",
            "View quick start guide"
        )
        self.help_menu.addAction(quickstart_action)
        
        self.help_menu.addSeparator()
        
        # Check Updates
        updates_action = self._create_action(
            "Check for Updates",
            "check_updates",
            "",
            "Check for software updates"
        )
        self.help_menu.addAction(updates_action)
        
        self.help_menu.addSeparator()
        
        # About
        about_action = self._create_action(
            "About",
            "about",
            "",
            "About this application"
        )
        self.help_menu.addAction(about_action)
    
    def _create_action(
        self,
        text: str,
        name: str,
        shortcut: str = "",
        tooltip: str = ""
    ) -> QAction:
        """
        Create a menu action
        
        Args:
            text: Action text
            name: Action name (internal)
            shortcut: Keyboard shortcut
            tooltip: Tooltip text
            
        Returns:
            Created QAction
        """
        action = QAction(text, self)
        
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        
        if tooltip:
            action.setStatusTip(tooltip)
            action.setToolTip(tooltip)
        
        action.triggered.connect(lambda: self._on_action_triggered(name))
        self.actions_dict[name] = action
        
        return action
    
    def _on_action_triggered(self, name: str):
        """Handle action triggered"""
        self.menu_action_triggered.emit(name)
        logger.debug(f"Menu action triggered: {name}")
    
    def _apply_styles(self):
        """Apply styling to menu bar"""
        self.setStyleSheet(f"""
            QMenuBar {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
                border-bottom: 1px solid {GUIConfig.COLORS['border']};
                padding: 4px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 4px 8px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {GUIConfig.COLORS['primary']};
            }}
            QMenuBar::item:pressed {{
                background-color: {GUIConfig.COLORS['secondary']};
            }}
            QMenu {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {GUIConfig.COLORS['primary']};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {GUIConfig.COLORS['border']};
                margin: 4px 8px;
            }}
        """)
    
    def get_action(self, name: str) -> Optional[QAction]:
        """
        Get action by name
        
        Args:
            name: Action name
            
        Returns:
            QAction or None
        """
        return self.actions_dict.get(name)
    
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
