"""
Domain Selection Dialog
Multi-select domain picker dialog
"""

from typing import List, Dict, Optional, Set
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                              QListWidgetItem, QPushButton, QLabel, QLineEdit,
                              QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging

logger = logging.getLogger(__name__)


class DomainSelectionDialog(QDialog):
    """Multi-select domain picker dialog"""
    
    # Signals
    domains_selected = pyqtSignal(list)  # List of selected domains
    
    def __init__(
        self,
        available_domains: List[str],
        selected_domains: Optional[List[str]] = None,
        title: str = "Select Domains",
        allow_multi_select: bool = True,
        parent=None
    ):
        """
        Initialize domain selection dialog
        
        Args:
            available_domains: List of available domain names
            selected_domains: Initially selected domains
            title: Dialog title
            allow_multi_select: Allow multiple selection
            parent: Parent widget
        """
        super().__init__(parent)
        self.available_domains = available_domains
        self.selected_domains = set(selected_domains or [])
        self.allow_multi_select = allow_multi_select
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(500, 600)
        
        self._setup_ui()
        self._apply_styles()
        self._load_domains()
        
        logger.debug(f"DomainSelectionDialog created with {len(available_domains)} domains")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Select one or more domains" if self.allow_multi_select else "Select a domain")
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['title'])
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter domains...")
        self.search_box.textChanged.connect(self._filter_domains)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Domain list
        list_group = QGroupBox("Available Domains")
        list_layout = QVBoxLayout(list_group)
        
        self.domain_list = QListWidget()
        if self.allow_multi_select:
            self.domain_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        else:
            self.domain_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        
        list_layout.addWidget(self.domain_list)
        layout.addWidget(list_group)
        
        # Selection controls
        if self.allow_multi_select:
            controls_layout = QHBoxLayout()
            
            select_all_btn = QPushButton("Select All")
            select_all_btn.clicked.connect(self._select_all)
            controls_layout.addWidget(select_all_btn)
            
            clear_all_btn = QPushButton("Clear All")
            clear_all_btn.clicked.connect(self._clear_all)
            controls_layout.addWidget(clear_all_btn)
            
            controls_layout.addStretch()
            layout.addLayout(controls_layout)
        
        # Selection info
        self.info_label = QLabel(self._get_info_text())
        self.info_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addWidget(self.info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect selection change
        self.domain_list.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _apply_styles(self):
        """Apply styling to the dialog"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {GUIConfig.COLORS['bg_primary']};
            }}
            QLabel {{
                color: {GUIConfig.COLORS['text_primary']};
            }}
            QGroupBox {{
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                color: {GUIConfig.COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {GUIConfig.COLORS['primary']};
            }}
        """)
    
    def _load_domains(self):
        """Load domains into the list"""
        self.domain_list.clear()
        
        for domain in sorted(self.available_domains):
            item = QListWidgetItem(domain)
            item.setCheckState(
                Qt.CheckState.Checked if domain in self.selected_domains
                else Qt.CheckState.Unchecked
            )
            self.domain_list.addItem(item)
            
            if domain in self.selected_domains:
                item.setSelected(True)
    
    def _filter_domains(self, text: str):
        """Filter domains based on search text"""
        text = text.lower()
        
        for i in range(self.domain_list.count()):
            item = self.domain_list.item(i)
            match = text in item.text().lower()
            item.setHidden(not match)
        
        self._update_info()
    
    def _select_all(self):
        """Select all visible domains"""
        for i in range(self.domain_list.count()):
            item = self.domain_list.item(i)
            if not item.isHidden():
                item.setSelected(True)
    
    def _clear_all(self):
        """Clear all selections"""
        self.domain_list.clearSelection()
    
    def _on_selection_changed(self):
        """Handle selection change"""
        self._update_info()
    
    def _update_info(self):
        """Update info label"""
        self.info_label.setText(self._get_info_text())
    
    def _get_info_text(self) -> str:
        """Get info label text"""
        selected_count = len(self.domain_list.selectedItems())
        visible_count = sum(1 for i in range(self.domain_list.count())
                          if not self.domain_list.item(i).isHidden())
        total_count = self.domain_list.count()
        
        if visible_count != total_count:
            return f"Selected: {selected_count} | Showing: {visible_count}/{total_count}"
        else:
            return f"Selected: {selected_count} | Total: {total_count}"
    
    def get_selected_domains(self) -> List[str]:
        """
        Get list of selected domains
        
        Returns:
            List of selected domain names
        """
        return [item.text() for item in self.domain_list.selectedItems()]
    
    def accept(self):
        """Handle OK button"""
        selected = self.get_selected_domains()
        self.domains_selected.emit(selected)
        logger.info(f"Domains selected: {len(selected)}")
        super().accept()
    
    @staticmethod
    def get_domains(
        available_domains: List[str],
        selected_domains: Optional[List[str]] = None,
        title: str = "Select Domains",
        allow_multi_select: bool = True,
        parent=None
    ) -> Optional[List[str]]:
        """
        Static method to show dialog and get selected domains
        
        Args:
            available_domains: List of available domains
            selected_domains: Initially selected domains
            title: Dialog title
            allow_multi_select: Allow multiple selection
            parent: Parent widget
            
        Returns:
            List of selected domains or None if cancelled
        """
        dialog = DomainSelectionDialog(
            available_domains,
            selected_domains,
            title,
            allow_multi_select,
            parent
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_selected_domains()
        return None
