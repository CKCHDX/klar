"""
Import Dialog
Data import dialog supporting CSV and JSON formats
"""

from typing import Optional, Dict, Any, List, Callable
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QComboBox, QLineEdit, QFileDialog,
                              QGroupBox, QCheckBox, QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
import logging
import json
import csv

logger = logging.getLogger(__name__)


class ImportDialog(QDialog):
    """Data import dialog"""
    
    # Signals
    import_started = pyqtSignal()
    import_completed = pyqtSignal(object)  # imported data
    import_failed = pyqtSignal(str)  # error message
    
    IMPORT_FORMATS = ['CSV', 'JSON', 'XML', 'TEXT']
    
    def __init__(
        self,
        title: str = "Import Data",
        allowed_formats: Optional[List[str]] = None,
        parent=None
    ):
        """
        Initialize import dialog
        
        Args:
            title: Dialog title
            allowed_formats: List of allowed formats (default: all)
            parent: Parent widget
        """
        super().__init__(parent)
        self.allowed_formats = allowed_formats or self.IMPORT_FORMATS
        self.imported_data = None
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(600, 500)
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug("ImportDialog created")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Import Data")
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['header'])
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # File selection
        file_group = QGroupBox("Source File")
        file_layout = QVBoxLayout(file_group)
        
        file_select_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select file to import...")
        self.file_path_edit.textChanged.connect(self._on_file_changed)
        file_select_layout.addWidget(self.file_path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_select_layout.addWidget(browse_btn)
        
        file_layout.addLayout(file_select_layout)
        layout.addWidget(file_group)
        
        # Format selection
        format_group = QGroupBox("Import Format")
        format_layout = QHBoxLayout(format_group)
        
        format_layout.addWidget(QLabel("Format:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(self.allowed_formats)
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        format_layout.addWidget(self.format_combo)
        
        format_layout.addStretch()
        layout.addWidget(format_group)
        
        # Import options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.has_headers_check = QCheckBox("First row contains headers (CSV only)")
        self.has_headers_check.setChecked(True)
        options_layout.addWidget(self.has_headers_check)
        
        self.validate_check = QCheckBox("Validate data before import")
        self.validate_check.setChecked(True)
        options_layout.addWidget(self.validate_check)
        
        self.merge_check = QCheckBox("Merge with existing data")
        options_layout.addWidget(self.merge_check)
        
        layout.addWidget(options_group)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setPlainText("Select file to see preview...")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self._import_data)
        self.import_button.setDefault(True)
        self.import_button.setEnabled(False)
        button_layout.addWidget(self.import_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
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
    
    def _browse_file(self):
        """Browse for input file"""
        filters = []
        for fmt in self.allowed_formats:
            ext = fmt.lower()
            filters.append(f"{fmt} Files (*.{ext})")
        
        file_filter = ";;".join(filters) + ";;All Files (*.*)"
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Import File",
            "",
            file_filter
        )
        
        if filename:
            self.file_path_edit.setText(filename)
    
    def _on_file_changed(self, file_path: str):
        """Handle file path change"""
        self.import_button.setEnabled(bool(file_path))
        if file_path:
            self._update_preview()
    
    def _on_format_changed(self, format_type: str):
        """Handle format change"""
        if self.file_path_edit.text():
            self._update_preview()
    
    def _update_preview(self):
        """Update import preview"""
        try:
            file_path = self.file_path_edit.text()
            if not file_path:
                return
            
            format_type = self.format_combo.currentText()
            preview_text = self._generate_preview(file_path, format_type)
            
            self.preview_text.setPlainText(preview_text[:500] + "\n..." if len(preview_text) > 500 else preview_text)
            self.status_label.setText("Ready to import")
            self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['success']};")
            
        except Exception as e:
            self.preview_text.setPlainText(f"Preview error: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['error']};")
            logger.error(f"Preview error: {e}")
    
    def _generate_preview(self, file_path: str, format_type: str) -> str:
        """Generate preview of file content"""
        if format_type == 'CSV':
            return self._preview_csv(file_path)
        elif format_type == 'JSON':
            return self._preview_json(file_path)
        elif format_type == 'XML':
            return self._preview_xml(file_path)
        elif format_type == 'TEXT':
            return self._preview_text(file_path)
        return "Unknown format"
    
    def _preview_csv(self, file_path: str) -> str:
        """Preview CSV file"""
        with open(file_path, 'r') as f:
            lines = []
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i >= 10:  # Preview first 10 rows
                    break
                lines.append(','.join(row))
            return '\n'.join(lines)
    
    def _preview_json(self, file_path: str) -> str:
        """Preview JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
            preview_data = data[:5] if isinstance(data, list) else data
            return json.dumps(preview_data, indent=2)
    
    def _preview_xml(self, file_path: str) -> str:
        """Preview XML file"""
        with open(file_path, 'r') as f:
            lines = f.readlines()[:20]  # First 20 lines
            return ''.join(lines)
    
    def _preview_text(self, file_path: str) -> str:
        """Preview text file"""
        with open(file_path, 'r') as f:
            lines = f.readlines()[:20]
            return ''.join(lines)
    
    def _import_data(self):
        """Perform data import"""
        try:
            file_path = self.file_path_edit.text()
            if not file_path:
                return
            
            self.import_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            self.status_label.setText("Importing...")
            self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['info']};")
            
            self.import_started.emit()
            
            format_type = self.format_combo.currentText()
            
            # Perform import based on format
            if format_type == 'CSV':
                self.imported_data = self._import_csv(file_path)
            elif format_type == 'JSON':
                self.imported_data = self._import_json(file_path)
            elif format_type == 'XML':
                self.imported_data = self._import_xml(file_path)
            elif format_type == 'TEXT':
                self.imported_data = self._import_text(file_path)
            
            # Validate if requested
            if self.validate_check.isChecked():
                self._validate_data()
            
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.status_label.setText("Import completed successfully")
            self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['success']};")
            
            self.import_completed.emit(self.imported_data)
            logger.info(f"Data imported from {file_path}")
            
            self.accept()
            
        except Exception as e:
            self.status_label.setText(f"Import failed: {str(e)}")
            self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['error']};")
            self.import_failed.emit(str(e))
            logger.error(f"Import error: {e}")
        
        finally:
            self.import_button.setEnabled(True)
            if self.progress_bar.maximum() == 0:
                self.progress_bar.setRange(0, 100)
    
    def _import_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Import from CSV"""
        data = []
        with open(file_path, 'r') as f:
            if self.has_headers_check.isChecked():
                reader = csv.DictReader(f)
                data = list(reader)
            else:
                reader = csv.reader(f)
                data = [row for row in reader]
        return data
    
    def _import_json(self, file_path: str) -> Any:
        """Import from JSON"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _import_xml(self, file_path: str) -> str:
        """Import from XML"""
        with open(file_path, 'r') as f:
            return f.read()
    
    def _import_text(self, file_path: str) -> List[str]:
        """Import from text file"""
        with open(file_path, 'r') as f:
            return f.readlines()
    
    def _validate_data(self):
        """Validate imported data"""
        if not self.imported_data:
            raise ValueError("No data imported")
        
        # Basic validation
        if isinstance(self.imported_data, list) and len(self.imported_data) == 0:
            raise ValueError("Imported data is empty")
    
    def get_imported_data(self) -> Any:
        """Get imported data"""
        return self.imported_data
    
    @staticmethod
    def import_data(
        title: str = "Import Data",
        allowed_formats: Optional[List[str]] = None,
        parent=None
    ) -> Optional[Any]:
        """
        Static method to show dialog and get imported data
        
        Args:
            title: Dialog title
            allowed_formats: List of allowed formats
            parent: Parent widget
            
        Returns:
            Imported data or None if cancelled
        """
        dialog = ImportDialog(title, allowed_formats, parent)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_imported_data()
        return None
