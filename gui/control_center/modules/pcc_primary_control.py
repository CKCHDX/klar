"""
PRIMARY CONTROL CENTER (PCC)
System overview dashboard with real-time metrics and quick actions
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QProgressBar, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
from gui.control_center.control_center_api_client import ControlCenterAPIClient

logger = logging.getLogger(__name__)


class StatusTile(QFrame):
    """Status tile widget for displaying metrics"""
    
    def __init__(self, title: str, icon: str = ""):
        super().__init__()
        self.setStyleSheet(Styles.get_metric_card_style())
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_secondary']};
                font-size: {GUIConfig.get_font_size('small')}pt;
                font-weight: bold;
            }}
        """)
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel("--")
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_primary']};
                font-size: {GUIConfig.get_font_size('header')}pt;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.value_label)
        
        # Status/subtitle
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_secondary']};
                font-size: {GUIConfig.get_font_size('small')}pt;
            }}
        """)
        layout.addWidget(self.status_label)
        
        # Progress bar (optional)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(4)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {GUIConfig.COLORS['primary']};
                border-radius: 2px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
    
    def update_value(self, value: str, status: str = "", progress: int = 0, color: str = None):
        """Update tile values"""
        self.value_label.setText(value)
        self.status_label.setText(status)
        self.progress_bar.setValue(progress)
        
        if color:
            self.value_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: {GUIConfig.get_font_size('header')}pt;
                    font-weight: bold;
                }}
            """)


class EventTimeline(QFrame):
    """Event timeline widget"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Recent Events")
        title.setStyleSheet(Styles.get_title_style('medium'))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(Styles.get_button_style(size='small'))
        clear_btn.clicked.connect(self.clear_events)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Event table
        self.event_table = QTableWidget()
        self.event_table.setStyleSheet(Styles.get_table_style())
        self.event_table.setColumnCount(4)
        self.event_table.setHorizontalHeaderLabels(['Time', 'Type', 'Message', 'Status'])
        self.event_table.horizontalHeader().setStretchLastSection(False)
        self.event_table.setColumnWidth(0, 120)
        self.event_table.setColumnWidth(1, 100)
        self.event_table.setColumnWidth(2, 400)
        self.event_table.setColumnWidth(3, 80)
        self.event_table.setMaximumHeight(200)
        self.event_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.event_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.event_table)
    
    def add_event(self, event_type: str, message: str, status: str = "INFO"):
        """Add event to timeline"""
        row = self.event_table.rowCount()
        if row >= 50:
            self.event_table.removeRow(0)
            row = 49
        
        self.event_table.insertRow(row)
        
        # Time
        time_item = QTableWidgetItem(datetime.now().strftime("%H:%M:%S"))
        self.event_table.setItem(row, 0, time_item)
        
        # Type
        type_item = QTableWidgetItem(event_type)
        self.event_table.setItem(row, 1, type_item)
        
        # Message
        msg_item = QTableWidgetItem(message)
        self.event_table.setItem(row, 2, msg_item)
        
        # Status
        status_item = QTableWidgetItem(status)
        if status == "ERROR":
            status_item.setForeground(GUIConfig.COLORS['error'])
        elif status == "WARNING":
            status_item.setForeground(GUIConfig.COLORS['warning'])
        elif status == "SUCCESS":
            status_item.setForeground(GUIConfig.COLORS['success'])
        self.event_table.setItem(row, 3, status_item)
        
        # Scroll to bottom
        self.event_table.scrollToBottom()
    
    def clear_events(self):
        """Clear all events"""
        self.event_table.setRowCount(0)


class PCCPrimaryControl(QWidget):
    """Primary Control Center - System Overview Dashboard"""
    
    refresh_requested = pyqtSignal()
    
    def __init__(self, api_client: ControlCenterAPIClient):
        super().__init__()
        self.api_client = api_client
        self.update_timer = QTimer()
        self.update_timer.setInterval(2000)  # 2 seconds
        self.update_timer.timeout.connect(self.refresh_data)
        
        self._setup_ui()
        self._connect_signals()
        
        logger.info("PCC Primary Control initialized")
    
    def _setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("System Overview Dashboard")
        title.setStyleSheet(Styles.get_title_style('header'))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Last updated label
        self.last_updated_label = QLabel("Last updated: --")
        self.last_updated_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_secondary']};
                font-size: {GUIConfig.get_font_size('small')}pt;
            }}
        """)
        header_layout.addWidget(self.last_updated_label)
        
        main_layout.addLayout(header_layout)
        
        # Status tiles
        tiles_layout = QGridLayout()
        tiles_layout.setSpacing(12)
        
        self.cpu_tile = StatusTile("CPU Usage")
        tiles_layout.addWidget(self.cpu_tile, 0, 0)
        
        self.ram_tile = StatusTile("Memory Usage")
        tiles_layout.addWidget(self.ram_tile, 0, 1)
        
        self.disk_tile = StatusTile("Disk Usage")
        tiles_layout.addWidget(self.disk_tile, 0, 2)
        
        self.index_tile = StatusTile("Index Size")
        tiles_layout.addWidget(self.index_tile, 0, 3)
        
        main_layout.addLayout(tiles_layout)
        
        # Quick actions
        actions_frame = QFrame()
        actions_frame.setStyleSheet(Styles.get_card_style())
        actions_layout = QHBoxLayout(actions_frame)
        
        actions_title = QLabel("Quick Actions")
        actions_title.setStyleSheet(Styles.get_title_style('medium'))
        actions_layout.addWidget(actions_title)
        actions_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet(Styles.get_button_style())
        self.refresh_btn.clicked.connect(self.refresh_data)
        actions_layout.addWidget(self.refresh_btn)
        
        self.clear_cache_btn = QPushButton("🗑️ Clear Cache")
        self.clear_cache_btn.setStyleSheet(Styles.get_button_style())
        self.clear_cache_btn.clicked.connect(self._clear_cache)
        actions_layout.addWidget(self.clear_cache_btn)
        
        self.rebuild_index_btn = QPushButton("⚙️ Rebuild Index")
        self.rebuild_index_btn.setStyleSheet(Styles.get_button_style())
        self.rebuild_index_btn.clicked.connect(self._rebuild_index)
        actions_layout.addWidget(self.rebuild_index_btn)
        
        main_layout.addWidget(actions_frame)
        
        # Event timeline
        self.event_timeline = EventTimeline()
        main_layout.addWidget(self.event_timeline)
        
        main_layout.addStretch()
    
    def _connect_signals(self):
        """Connect API client signals"""
        self.api_client.health_check_completed.connect(self._on_health_update)
        self.api_client.stats_received.connect(self._on_stats_update)
        self.api_client.error_occurred.connect(self._on_error)
    
    def showEvent(self, event):
        """Handle widget show event"""
        super().showEvent(event)
        self.start_updates()
        self.refresh_data()
    
    def hideEvent(self, event):
        """Handle widget hide event"""
        super().hideEvent(event)
        self.stop_updates()
    
    def start_updates(self):
        """Start automatic updates"""
        if not self.update_timer.isActive():
            self.update_timer.start()
            logger.info("PCC updates started")
    
    def stop_updates(self):
        """Stop automatic updates"""
        if self.update_timer.isActive():
            self.update_timer.stop()
            logger.info("PCC updates stopped")
    
    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            self.api_client.check_health()
            self.api_client.get_stats()
            self.last_updated_label.setText(
                f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
            )
            self.refresh_requested.emit()
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            self.event_timeline.add_event("System", f"Refresh failed: {e}", "ERROR")
    
    def _on_health_update(self, data: Dict[str, Any]):
        """Handle health check update"""
        try:
            status = data.get('status', 'unknown')
            self.event_timeline.add_event(
                "Health", f"System health: {status}", "SUCCESS" if status == "healthy" else "WARNING"
            )
        except Exception as e:
            logger.error(f"Error processing health update: {e}")
    
    def _on_stats_update(self, data: Dict[str, Any]):
        """Handle stats update"""
        try:
            # Update CPU tile
            cpu_usage = data.get('cpu_usage', 0)
            cpu_color = GUIConfig.COLORS['success'] if cpu_usage < 70 else GUIConfig.COLORS['warning']
            if cpu_usage > 90:
                cpu_color = GUIConfig.COLORS['error']
            self.cpu_tile.update_value(
                f"{cpu_usage:.1f}%",
                "Available" if cpu_usage < 70 else "High Load",
                int(cpu_usage),
                cpu_color
            )
            
            # Update RAM tile
            ram_usage = data.get('memory_usage', 0)
            ram_total = data.get('memory_total', 0)
            ram_percent = (ram_usage / ram_total * 100) if ram_total > 0 else 0
            ram_color = GUIConfig.COLORS['success'] if ram_percent < 70 else GUIConfig.COLORS['warning']
            if ram_percent > 90:
                ram_color = GUIConfig.COLORS['error']
            self.ram_tile.update_value(
                f"{ram_percent:.1f}%",
                f"{ram_usage:.1f} GB / {ram_total:.1f} GB",
                int(ram_percent),
                ram_color
            )
            
            # Update Disk tile
            disk_usage = data.get('disk_usage', 0)
            disk_total = data.get('disk_total', 0)
            disk_percent = (disk_usage / disk_total * 100) if disk_total > 0 else 0
            disk_color = GUIConfig.COLORS['success'] if disk_percent < 80 else GUIConfig.COLORS['warning']
            if disk_percent > 95:
                disk_color = GUIConfig.COLORS['error']
            self.disk_tile.update_value(
                f"{disk_percent:.1f}%",
                f"{disk_usage:.1f} GB / {disk_total:.1f} GB",
                int(disk_percent),
                disk_color
            )
            
            # Update Index tile
            index_size = data.get('index_size', 0)
            doc_count = data.get('document_count', 0)
            self.index_tile.update_value(
                f"{index_size:.2f} GB",
                f"{doc_count:,} documents",
                0,
                GUIConfig.COLORS['info']
            )
            
        except Exception as e:
            logger.error(f"Error processing stats update: {e}")
    
    def _on_error(self, error: str):
        """Handle API error"""
        self.event_timeline.add_event("Error", error, "ERROR")
    
    def _clear_cache(self):
        """Clear cache"""
        try:
            self.api_client.clear_cache()
            self.event_timeline.add_event("Cache", "Cache cleared successfully", "SUCCESS")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            self.event_timeline.add_event("Cache", f"Failed to clear cache: {e}", "ERROR")
    
    def _rebuild_index(self):
        """Rebuild index"""
        self.event_timeline.add_event("Index", "Index rebuild started", "INFO")
        # This would trigger index rebuild through API
