"""
Snapshot Dialog
Snapshot management dialog for saving and loading system states
"""

from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QListWidget, QListWidgetItem, QLineEdit,
                              QTextEdit, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class SnapshotDialog(QDialog):
    """Snapshot management dialog"""
    
    # Signals
    snapshot_created = pyqtSignal(dict)  # Snapshot data
    snapshot_loaded = pyqtSignal(dict)  # Snapshot data
    snapshot_deleted = pyqtSignal(str)  # Snapshot ID
    
    def __init__(
        self,
        snapshots: Optional[List[Dict[str, Any]]] = None,
        title: str = "Manage Snapshots",
        parent=None
    ):
        """
        Initialize snapshot dialog
        
        Args:
            snapshots: List of existing snapshots
            title: Dialog title
            parent: Parent widget
        """
        super().__init__(parent)
        self.snapshots = snapshots or []
        self.selected_snapshot = None
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(700, 600)
        
        self._setup_ui()
        self._apply_styles()
        self._load_snapshots()
        
        logger.debug("SnapshotDialog created")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("System Snapshots")
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['header'])
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Create, load, or delete system state snapshots")
        desc_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addWidget(desc_label)
        
        # Main content layout
        content_layout = QHBoxLayout()
        
        # Snapshot list (left side)
        list_group = QGroupBox("Available Snapshots")
        list_layout = QVBoxLayout(list_group)
        
        self.snapshot_list = QListWidget()
        self.snapshot_list.itemSelectionChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self.snapshot_list)
        
        # List action buttons
        list_actions = QHBoxLayout()
        
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self._load_snapshot)
        self.load_button.setEnabled(False)
        list_actions.addWidget(self.load_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_snapshot)
        self.delete_button.setEnabled(False)
        list_actions.addWidget(self.delete_button)
        
        list_layout.addLayout(list_actions)
        
        content_layout.addWidget(list_group, 2)
        
        # Details/Create (right side)
        details_group = QGroupBox("Snapshot Details")
        details_layout = QVBoxLayout(details_group)
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter snapshot name...")
        name_layout.addWidget(self.name_edit)
        details_layout.addLayout(name_layout)
        
        # Description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Enter snapshot description...")
        self.desc_edit.setMaximumHeight(100)
        desc_layout.addWidget(self.desc_edit)
        details_layout.addLayout(desc_layout)
        
        # Info display
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setPlaceholderText("Select a snapshot to view details...")
        self.info_text.setMaximumHeight(150)
        details_layout.addWidget(self.info_text)
        
        # Create button
        self.create_button = QPushButton("Create Snapshot")
        self.create_button.clicked.connect(self._create_snapshot)
        details_layout.addWidget(self.create_button)
        
        content_layout.addWidget(details_group, 3)
        
        layout.addLayout(content_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
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
    
    def _load_snapshots(self):
        """Load snapshots into list"""
        self.snapshot_list.clear()
        
        for snapshot in sorted(self.snapshots, key=lambda x: x.get('timestamp', ''), reverse=True):
            name = snapshot.get('name', 'Unnamed')
            timestamp = snapshot.get('timestamp', '')
            
            item = QListWidgetItem(f"{name} - {timestamp}")
            item.setData(Qt.ItemDataRole.UserRole, snapshot)
            self.snapshot_list.addItem(item)
    
    def _on_selection_changed(self):
        """Handle snapshot selection change"""
        selected_items = self.snapshot_list.selectedItems()
        
        if selected_items:
            item = selected_items[0]
            self.selected_snapshot = item.data(Qt.ItemDataRole.UserRole)
            
            self.load_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            
            # Display snapshot info
            self._display_snapshot_info(self.selected_snapshot)
        else:
            self.selected_snapshot = None
            self.load_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.info_text.clear()
    
    def _display_snapshot_info(self, snapshot: Dict[str, Any]):
        """Display snapshot information"""
        info = f"""
<b>Name:</b> {snapshot.get('name', 'N/A')}<br>
<b>Created:</b> {snapshot.get('timestamp', 'N/A')}<br>
<b>Description:</b> {snapshot.get('description', 'No description')}<br>
<br>
<b>Data Size:</b> {len(str(snapshot.get('data', {})))} bytes<br>
<b>ID:</b> {snapshot.get('id', 'N/A')}
        """.strip()
        
        self.info_text.setHtml(info)
    
    def _create_snapshot(self):
        """Create a new snapshot"""
        name = self.name_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a snapshot name")
            return
        
        # Create snapshot data
        snapshot = {
            'id': datetime.now().strftime("%Y%m%d%H%M%S"),
            'name': name,
            'description': description,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data': {}  # Will be populated by caller
        }
        
        self.snapshots.append(snapshot)
        self._load_snapshots()
        
        # Clear inputs
        self.name_edit.clear()
        self.desc_edit.clear()
        
        self.snapshot_created.emit(snapshot)
        logger.info(f"Snapshot created: {name}")
        
        QMessageBox.information(self, "Success", f"Snapshot '{name}' created successfully")
    
    def _load_snapshot(self):
        """Load selected snapshot"""
        if not self.selected_snapshot:
            return
        
        name = self.selected_snapshot.get('name', 'Unnamed')
        
        from gui.control_center.dialogs.confirmation_dialog import ConfirmationDialog
        confirmed, _ = ConfirmationDialog.ask(
            "Load Snapshot",
            f"Are you sure you want to load snapshot '{name}'?\n\n"
            "This will restore the system to this saved state.",
            'warning',
            parent=self
        )
        
        if confirmed:
            self.snapshot_loaded.emit(self.selected_snapshot)
            logger.info(f"Snapshot loaded: {name}")
            self.accept()
    
    def _delete_snapshot(self):
        """Delete selected snapshot"""
        if not self.selected_snapshot:
            return
        
        name = self.selected_snapshot.get('name', 'Unnamed')
        snapshot_id = self.selected_snapshot.get('id')
        
        from gui.control_center.dialogs.confirmation_dialog import ConfirmationDialog
        confirmed, _ = ConfirmationDialog.ask(
            "Delete Snapshot",
            f"Are you sure you want to delete snapshot '{name}'?",
            'danger',
            "Delete",
            parent=self
        )
        
        if confirmed:
            self.snapshots = [s for s in self.snapshots if s.get('id') != snapshot_id]
            self._load_snapshots()
            
            self.snapshot_deleted.emit(snapshot_id)
            logger.info(f"Snapshot deleted: {name}")
            
            QMessageBox.information(self, "Deleted", f"Snapshot '{name}' deleted")
    
    def get_snapshots(self) -> List[Dict[str, Any]]:
        """Get current list of snapshots"""
        return self.snapshots
    
    @staticmethod
    def manage_snapshots(
        snapshots: Optional[List[Dict[str, Any]]] = None,
        parent=None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Static method to show snapshot management dialog
        
        Args:
            snapshots: List of existing snapshots
            parent: Parent widget
            
        Returns:
            Updated list of snapshots or None if cancelled
        """
        dialog = SnapshotDialog(snapshots, parent=parent)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_snapshots()
        return None
