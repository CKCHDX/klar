"""
Export Dialog
Data export dialog supporting CSV and JSON formats
"""

from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QComboBox, QLineEdit, QFileDialog,
                              QGroupBox, QCheckBox, QFormLayout, QProgressBar,
                              QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
import logging
import json
import csv
from pathlib import Path

logger = logging.getLogger(__name__)


class ExportDialog(QDialog):
    """Data export dialog"""
    
    # Signals
    export_started = pyqtSignal()
    export_completed = pyqtSignal(str)  # filename
    export_failed = pyqtSignal(str)  # error message
    
    EXPORT_FORMATS = ['CSV', 'JSON', 'XML', 'TEXT']
    
    def __init__(
        self,
        data: Any,
        default_filename: str = "export",
        title: str = "Export Data",
        parent=None
    ):
        """
        Initialize export dialog
        
        Args:
            data: Data to export
            default_filename: Default filename (without extension)
            title: Dialog title
            parent: Parent widget
        """
        super().__init__(parent)
        self.data = data
        self.default_filename = default_filename
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(600, 400)
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug("ExportDialog created")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Export Data")
        title_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['header'])
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Format selection
        format_group = QGroupBox("Export Format")
        format_layout = QFormLayout(format_group)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(self.EXPORT_FORMATS)
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        format_layout.addRow("Format:", self.format_combo)
        
        layout.addWidget(format_group)
        
        # File selection
        file_group = QGroupBox("Output File")
        file_layout = QVBoxLayout(file_group)
        
        file_select_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select output file...")
        file_select_layout.addWidget(self.file_path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_select_layout.addWidget(browse_btn)
        
        file_layout.addLayout(file_select_layout)
        layout.addWidget(file_group)
        
        # Export options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.include_headers_check = QCheckBox("Include headers (CSV only)")
        self.include_headers_check.setChecked(True)
        options_layout.addWidget(self.include_headers_check)
        
        self.pretty_print_check = QCheckBox("Pretty print (JSON only)")
        self.pretty_print_check.setChecked(True)
        options_layout.addWidget(self.pretty_print_check)
        
        self.open_after_check = QCheckBox("Open file after export")
        options_layout.addWidget(self.open_after_check)
        
        layout.addWidget(options_group)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setPlainText("Select format and file to see preview...")
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
        
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self._export_data)
        self.export_button.setDefault(True)
        button_layout.addWidget(self.export_button)
        
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
    
    def _on_format_changed(self, format_type: str):
        """Handle format change"""
        self._update_preview()
    
    def _browse_file(self):
        """Browse for output file"""
        format_type = self.format_combo.currentText()
        
        filters = {
            'CSV': "CSV Files (*.csv)",
            'JSON': "JSON Files (*.json)",
            'XML': "XML Files (*.xml)",
            'TEXT': "Text Files (*.txt)",
        }
        
        file_filter = filters.get(format_type, "All Files (*.*)")
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Export File",
            self.default_filename,
            file_filter
        )
        
        if filename:
            self.file_path_edit.setText(filename)
            self._update_preview()
    
    def _update_preview(self):
        """Update export preview"""
        try:
            format_type = self.format_combo.currentText()
            preview_text = self._generate_preview(format_type)
            self.preview_text.setPlainText(preview_text[:500] + "\n..." if len(preview_text) > 500 else preview_text)
        except Exception as e:
            self.preview_text.setPlainText(f"Preview error: {str(e)}")
            logger.error(f"Preview error: {e}")
    
    def _generate_preview(self, format_type: str) -> str:
        """Generate preview of exported data"""
        if format_type == 'CSV':
            return self._to_csv_preview()
        elif format_type == 'JSON':
            return self._to_json_preview()
        elif format_type == 'XML':
            return self._to_xml_preview()
        elif format_type == 'TEXT':
            return self._to_text_preview()
        return "Unknown format"
    
    def _to_csv_preview(self) -> str:
        """Generate CSV preview"""
        if isinstance(self.data, list):
            if not self.data:
                return "No data"
            
            # Assume list of dicts
            if isinstance(self.data[0], dict):
                lines = []
                if self.include_headers_check.isChecked():
                    lines.append(','.join(self.data[0].keys()))
                for row in self.data[:5]:  # Preview first 5 rows
                    lines.append(','.join(str(v) for v in row.values()))
                return '\n'.join(lines)
        
        return str(self.data)
    
    def _to_json_preview(self) -> str:
        """Generate JSON preview"""
        indent = 2 if self.pretty_print_check.isChecked() else None
        
        if isinstance(self.data, (list, dict)):
            preview_data = self.data[:5] if isinstance(self.data, list) else self.data
            return json.dumps(preview_data, indent=indent)
        
        return json.dumps({"data": str(self.data)}, indent=indent)
    
    def _to_xml_preview(self) -> str:
        """Generate XML preview"""
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<export>\n'
        
        if isinstance(self.data, list):
            for item in self.data[:5]:
                xml += '  <item>\n'
                if isinstance(item, dict):
                    for key, value in item.items():
                        xml += f'    <{key}>{value}</{key}>\n'
                xml += '  </item>\n'
        
        xml += '</export>'
        return xml
    
    def _to_text_preview(self) -> str:
        """Generate text preview"""
        if isinstance(self.data, list):
            return '\n'.join(str(item) for item in self.data[:10])
        return str(self.data)
    
    def _export_data(self):
        """Perform data export"""
        try:
            file_path = self.file_path_edit.text()
            if not file_path:
                self.status_label.setText("Please select output file")
                self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['error']};")
                return
            
            self.export_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            self.status_label.setText("Exporting...")
            self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['info']};")
            
            self.export_started.emit()
            
            format_type = self.format_combo.currentText()
            
            # Perform export based on format
            if format_type == 'CSV':
                self._export_csv(file_path)
            elif format_type == 'JSON':
                self._export_json(file_path)
            elif format_type == 'XML':
                self._export_xml(file_path)
            elif format_type == 'TEXT':
                self._export_text(file_path)
            
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.status_label.setText(f"Export completed: {file_path}")
            self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['success']};")
            
            self.export_completed.emit(file_path)
            
            if self.open_after_check.isChecked():
                self._open_file(file_path)
            
            logger.info(f"Data exported to {file_path}")
            
        except Exception as e:
            self.status_label.setText(f"Export failed: {str(e)}")
            self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['error']};")
            self.export_failed.emit(str(e))
            logger.error(f"Export error: {e}")
        
        finally:
            self.export_button.setEnabled(True)
            if self.progress_bar.maximum() == 0:
                self.progress_bar.setRange(0, 100)
    
    def _export_csv(self, file_path: str):
        """Export as CSV"""
        with open(file_path, 'w', newline='') as f:
            if isinstance(self.data, list) and self.data and isinstance(self.data[0], dict):
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                if self.include_headers_check.isChecked():
                    writer.writeheader()
                writer.writerows(self.data)
            else:
                writer = csv.writer(f)
                writer.writerow([str(self.data)])
    
    def _export_json(self, file_path: str):
        """Export as JSON"""
        with open(file_path, 'w') as f:
            indent = 2 if self.pretty_print_check.isChecked() else None
            json.dump(self.data, f, indent=indent)
    
    def _export_xml(self, file_path: str):
        """Export as XML"""
        content = self._to_xml_preview()  # Use full data
        with open(file_path, 'w') as f:
            f.write(content)
    
    def _export_text(self, file_path: str):
        """Export as text"""
        with open(file_path, 'w') as f:
            if isinstance(self.data, list):
                f.write('\n'.join(str(item) for item in self.data))
            else:
                f.write(str(self.data))
    
    def _open_file(self, file_path: str):
        """Open file with default application"""
        import os
        import platform
        
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{file_path}"')
            else:  # Linux
                os.system(f'xdg-open "{file_path}"')
        except Exception as e:
            logger.error(f"Error opening file: {e}")
