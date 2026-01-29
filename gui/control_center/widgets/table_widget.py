"""
Table Widget
Enhanced sortable table with search and filtering capabilities
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QLineEdit, QPushButton, QLabel,
                              QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging

logger = logging.getLogger(__name__)


class TableWidget(QWidget):
    """Enhanced sortable table widget"""
    
    # Signals
    row_selected = pyqtSignal(int)  # Row index
    row_double_clicked = pyqtSignal(int)
    cell_changed = pyqtSignal(int, int, str)  # row, column, value
    selection_changed = pyqtSignal(list)  # List of selected row indices
    
    def __init__(
        self,
        headers: List[str],
        sortable: bool = True,
        searchable: bool = True,
        editable: bool = False,
        parent=None
    ):
        """
        Initialize table widget
        
        Args:
            headers: Column headers
            sortable: Enable sorting
            searchable: Enable search
            editable: Enable cell editing
            parent: Parent widget
        """
        super().__init__(parent)
        self.headers = headers
        self.sortable = sortable
        self.searchable = searchable
        self.editable = editable
        self.data_cache = []  # Store original data for filtering
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug(f"TableWidget created with {len(headers)} columns")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Toolbar
        if self.searchable:
            toolbar = QHBoxLayout()
            toolbar.setSpacing(8)
            
            # Search box
            self.search_box = QLineEdit()
            self.search_box.setPlaceholderText("Search...")
            self.search_box.textChanged.connect(self._on_search)
            toolbar.addWidget(self.search_box)
            
            # Clear search button
            clear_btn = QPushButton("Clear")
            clear_btn.clicked.connect(self._clear_search)
            clear_btn.setFixedWidth(80)
            toolbar.addWidget(clear_btn)
            
            # Row count label
            self.row_count_label = QLabel("Rows: 0")
            self.row_count_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
            toolbar.addWidget(self.row_count_label)
            
            layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        
        # Table properties
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        if self.sortable:
            self.table.setSortingEnabled(True)
        
        if not self.editable:
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Resize columns
        header = self.table.horizontalHeader()
        for i in range(len(self.headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        # Connect signals
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        if self.editable:
            self.table.cellChanged.connect(self._on_cell_changed)
        
        layout.addWidget(self.table)
    
    def _apply_styles(self):
        """Apply styling to the widget"""
        self.table.setStyleSheet(Styles.get_table_style())
        
        if self.searchable:
            self.search_box.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {GUIConfig.COLORS['bg_secondary']};
                    color: {GUIConfig.COLORS['text_primary']};
                    border: 1px solid {GUIConfig.COLORS['border']};
                    border-radius: 4px;
                    padding: 6px;
                }}
            """)
    
    def add_row(self, data: List[Any]):
        """
        Add a row to the table
        
        Args:
            data: List of cell values
        """
        try:
            if len(data) != len(self.headers):
                logger.warning(f"Row data length ({len(data)}) doesn't match headers ({len(self.headers)})")
                return
            
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_position, col, item)
            
            self.data_cache.append(data)
            self._update_row_count()
            
            logger.debug(f"Row added at position {row_position}")
        except Exception as e:
            logger.error(f"Error adding row: {e}")
    
    def add_rows(self, rows: List[List[Any]]):
        """Add multiple rows"""
        for row in rows:
            self.add_row(row)
    
    def set_data(self, data: List[List[Any]]):
        """
        Set all table data at once
        
        Args:
            data: List of rows
        """
        self.clear()
        self.add_rows(data)
    
    def get_row(self, row: int) -> List[str]:
        """
        Get data from a specific row
        
        Args:
            row: Row index
            
        Returns:
            List of cell values
        """
        if row < 0 or row >= self.table.rowCount():
            return []
        
        return [
            self.table.item(row, col).text() if self.table.item(row, col) else ""
            for col in range(self.table.columnCount())
        ]
    
    def get_selected_row(self) -> Optional[int]:
        """Get currently selected row index"""
        selected = self.table.selectedItems()
        if selected:
            return selected[0].row()
        return None
    
    def get_selected_data(self) -> Optional[List[str]]:
        """Get data from selected row"""
        row = self.get_selected_row()
        if row is not None:
            return self.get_row(row)
        return None
    
    def remove_row(self, row: int):
        """Remove a row"""
        if 0 <= row < self.table.rowCount():
            self.table.removeRow(row)
            if row < len(self.data_cache):
                self.data_cache.pop(row)
            self._update_row_count()
    
    def clear(self):
        """Clear all rows"""
        self.table.setRowCount(0)
        self.data_cache.clear()
        self._update_row_count()
    
    def set_cell_color(self, row: int, col: int, color: str):
        """
        Set cell background color
        
        Args:
            row: Row index
            col: Column index
            color: Color hex code
        """
        item = self.table.item(row, col)
        if item:
            item.setBackground(QColor(color))
    
    def set_row_color(self, row: int, color: str):
        """
        Set entire row background color
        
        Args:
            row: Row index
            color: Color hex code
        """
        for col in range(self.table.columnCount()):
            self.set_cell_color(row, col, color)
    
    def _on_search(self, text: str):
        """Handle search text change"""
        text = text.lower()
        
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            
            self.table.setRowHidden(row, not match)
        
        self._update_row_count()
    
    def _clear_search(self):
        """Clear search"""
        if hasattr(self, 'search_box'):
            self.search_box.clear()
    
    def _on_selection_changed(self):
        """Handle selection change"""
        selected_rows = list(set([item.row() for item in self.table.selectedItems()]))
        self.selection_changed.emit(selected_rows)
        
        if selected_rows:
            self.row_selected.emit(selected_rows[0])
    
    def _on_cell_double_clicked(self, row: int, col: int):
        """Handle cell double click"""
        self.row_double_clicked.emit(row)
    
    def _on_cell_changed(self, row: int, col: int):
        """Handle cell change"""
        item = self.table.item(row, col)
        if item:
            self.cell_changed.emit(row, col, item.text())
    
    def _update_row_count(self):
        """Update row count label"""
        if hasattr(self, 'row_count_label'):
            visible_rows = sum(1 for row in range(self.table.rowCount()) 
                             if not self.table.isRowHidden(row))
            total_rows = self.table.rowCount()
            
            if visible_rows != total_rows:
                self.row_count_label.setText(f"Rows: {visible_rows}/{total_rows}")
            else:
                self.row_count_label.setText(f"Rows: {total_rows}")
    
    def get_row_count(self) -> int:
        """Get total row count"""
        return self.table.rowCount()
    
    def export_to_csv(self, filename: str):
        """
        Export table data to CSV
        
        Args:
            filename: Output file path
        """
        try:
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write headers
                writer.writerow(self.headers)
                
                # Write data
                for row in range(self.table.rowCount()):
                    if not self.table.isRowHidden(row):
                        writer.writerow(self.get_row(row))
            
            logger.info(f"Table exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting table: {e}")
