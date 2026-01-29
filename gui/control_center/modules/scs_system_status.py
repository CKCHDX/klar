"""
SYSTEM CONTROL STATUS (SCS)
Component health monitoring and system metrics dashboard
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
from gui.control_center.control_center_api_client import ControlCenterAPIClient

logger = logging.getLogger(__name__)


class ComponentHealthTable(QFrame):
    """Component health status table"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Component Health Status")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Health table
        self.health_table = QTableWidget()
        self.health_table.setStyleSheet(Styles.get_table_style())
        self.health_table.setColumnCount(5)
        self.health_table.setHorizontalHeaderLabels([
            'Component', 'Status', 'Health', 'Last Check', 'Message'
        ])
        self.health_table.setColumnWidth(0, 150)
        self.health_table.setColumnWidth(1, 100)
        self.health_table.setColumnWidth(2, 100)
        self.health_table.setColumnWidth(3, 150)
        self.health_table.setColumnWidth(4, 300)
        self.health_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.health_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.health_table)
        
        # Initialize with default components
        self._init_components()
    
    def _init_components(self):
        """Initialize component rows"""
        components = [
            'Crawler',
            'Indexer',
            'Search Engine',
            'API Server',
            'Cache System',
            'Storage Backend'
        ]
        
        self.health_table.setRowCount(len(components))
        
        for i, component in enumerate(components):
            # Component name
            name_item = QTableWidgetItem(component)
            name_item.setFont(QFont(GUIConfig.FONTS['family'], GUIConfig.get_font_size('normal'), QFont.Weight.Bold))
            self.health_table.setItem(i, 0, name_item)
            
            # Status
            status_item = QTableWidgetItem("Unknown")
            self.health_table.setItem(i, 1, status_item)
            
            # Health
            health_item = QTableWidgetItem("--")
            self.health_table.setItem(i, 2, health_item)
            
            # Last check
            check_item = QTableWidgetItem("--")
            self.health_table.setItem(i, 3, check_item)
            
            # Message
            msg_item = QTableWidgetItem("Initializing...")
            self.health_table.setItem(i, 4, msg_item)
    
    def update_component(self, component: str, status: str, health: str, message: str = ""):
        """Update component status"""
        # Find component row
        for i in range(self.health_table.rowCount()):
            item = self.health_table.item(i, 0)
            if item and item.text() == component:
                # Update status
                status_item = self.health_table.item(i, 1)
                status_item.setText(status)
                status_color = GUIConfig.get_status_color(status)
                status_item.setForeground(QColor(status_color))
                
                # Update health
                health_item = self.health_table.item(i, 2)
                health_item.setText(health)
                from gui.control_center.control_center_config import ControlCenterConfig
                health_color = ControlCenterConfig.get_health_color(health)
                health_item.setForeground(QColor(health_color))
                
                # Update timestamp
                check_item = self.health_table.item(i, 3)
                check_item.setText(datetime.now().strftime("%H:%M:%S"))
                
                # Update message
                msg_item = self.health_table.item(i, 4)
                msg_item.setText(message or "Operating normally")
                break


class StorageStatistics(QFrame):
    """Storage statistics display"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_metric_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Storage Statistics")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Stats grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(12)
        
        # Index size
        stats_layout.addWidget(self._create_label("Index Size:"), 0, 0)
        self.index_size_label = self._create_value_label("0 GB")
        stats_layout.addWidget(self.index_size_label, 0, 1)
        
        # Cache size
        stats_layout.addWidget(self._create_label("Cache Size:"), 1, 0)
        self.cache_size_label = self._create_value_label("0 MB")
        stats_layout.addWidget(self.cache_size_label, 1, 1)
        
        # Disk usage
        stats_layout.addWidget(self._create_label("Disk Usage:"), 2, 0)
        self.disk_usage_label = self._create_value_label("0%")
        stats_layout.addWidget(self.disk_usage_label, 2, 1)
        
        # Document count
        stats_layout.addWidget(self._create_label("Documents:"), 3, 0)
        self.doc_count_label = self._create_value_label("0")
        stats_layout.addWidget(self.doc_count_label, 3, 1)
        
        layout.addLayout(stats_layout)
        
        # Progress bars
        self.disk_progress = self._create_progress_bar("Disk")
        layout.addWidget(self.disk_progress)
        
        self.cache_progress = self._create_progress_bar("Cache")
        layout.addWidget(self.cache_progress)
    
    def _create_label(self, text: str) -> QLabel:
        """Create label"""
        label = QLabel(text)
        label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        return label
    
    def _create_value_label(self, text: str) -> QLabel:
        """Create value label"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['primary']};
                font-size: {GUIConfig.get_font_size('large')}pt;
                font-weight: bold;
            }}
        """)
        return label
    
    def _create_progress_bar(self, name: str) -> QFrame:
        """Create progress bar with label"""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 4, 0, 4)
        
        label = QLabel(f"{name}:")
        label.setFixedWidth(60)
        layout.addWidget(label)
        
        progress = QProgressBar()
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {GUIConfig.COLORS['primary']};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress)
        
        setattr(self, f"{name.lower()}_bar", progress)
        return frame
    
    def update_stats(self, data: Dict[str, Any]):
        """Update storage statistics"""
        # Index size
        index_size = data.get('index_size', 0)
        self.index_size_label.setText(f"{index_size:.2f} GB")
        
        # Cache size
        cache_size = data.get('cache_size', 0)
        self.cache_size_label.setText(f"{cache_size:.2f} MB")
        
        # Disk usage
        disk_percent = data.get('disk_usage_percent', 0)
        self.disk_usage_label.setText(f"{disk_percent:.1f}%")
        self.disk_bar.setValue(int(disk_percent))
        
        # Cache usage
        cache_percent = data.get('cache_usage_percent', 0)
        self.cache_bar.setValue(int(cache_percent))
        
        # Document count
        doc_count = data.get('document_count', 0)
        self.doc_count_label.setText(f"{doc_count:,}")


class MetricGauge(QFrame):
    """Circular gauge widget for metrics"""
    
    def __init__(self, title: str, unit: str = ""):
        super().__init__()
        self.setStyleSheet(Styles.get_metric_card_style())
        self.setFixedSize(180, 180)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_secondary']};
                font-size: {GUIConfig.get_font_size('small')}pt;
            }}
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['primary']};
                font-size: {GUIConfig.get_font_size('header')}pt;
                font-weight: bold;
            }}
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Unit
        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet(f"""
                QLabel {{
                    color: {GUIConfig.COLORS['text_secondary']};
                    font-size: {GUIConfig.get_font_size('small')}pt;
                }}
            """)
            unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(unit_label)
        
        # Progress circle
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setMaximumHeight(8)
        layout.addWidget(self.progress)
    
    def update_value(self, value: float, max_value: float = 100):
        """Update gauge value"""
        self.value_label.setText(f"{value:.1f}")
        percent = int((value / max_value) * 100) if max_value > 0 else 0
        self.progress.setValue(percent)


class AlertPanel(QFrame):
    """Alert and warning display panel"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("System Alerts")
        title.setStyleSheet(Styles.get_title_style('medium'))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.alert_count_label = QLabel("0 alerts")
        self.alert_count_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        header_layout.addWidget(self.alert_count_label)
        
        layout.addLayout(header_layout)
        
        # Alerts table
        self.alerts_table = QTableWidget()
        self.alerts_table.setStyleSheet(Styles.get_table_style())
        self.alerts_table.setColumnCount(4)
        self.alerts_table.setHorizontalHeaderLabels(['Time', 'Severity', 'Component', 'Message'])
        self.alerts_table.setColumnWidth(0, 100)
        self.alerts_table.setColumnWidth(1, 80)
        self.alerts_table.setColumnWidth(2, 120)
        self.alerts_table.setColumnWidth(3, 400)
        self.alerts_table.setMaximumHeight(150)
        self.alerts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.alerts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.alerts_table)
    
    def add_alert(self, severity: str, component: str, message: str):
        """Add alert to panel"""
        row = self.alerts_table.rowCount()
        self.alerts_table.insertRow(row)
        
        # Time
        time_item = QTableWidgetItem(datetime.now().strftime("%H:%M:%S"))
        self.alerts_table.setItem(row, 0, time_item)
        
        # Severity
        severity_item = QTableWidgetItem(severity.upper())
        severity_colors = {
            'CRITICAL': GUIConfig.COLORS['error'],
            'WARNING': GUIConfig.COLORS['warning'],
            'INFO': GUIConfig.COLORS['info'],
        }
        severity_item.setForeground(QColor(severity_colors.get(severity.upper(), GUIConfig.COLORS['text_primary'])))
        self.alerts_table.setItem(row, 1, severity_item)
        
        # Component
        comp_item = QTableWidgetItem(component)
        self.alerts_table.setItem(row, 2, comp_item)
        
        # Message
        msg_item = QTableWidgetItem(message)
        self.alerts_table.setItem(row, 3, msg_item)
        
        # Update count
        self.alert_count_label.setText(f"{row + 1} alert(s)")
        
        # Scroll to bottom
        self.alerts_table.scrollToBottom()


class SCSSystemStatus(QWidget):
    """System Control Status - Component Health Monitoring"""
    
    def __init__(self, api_client: ControlCenterAPIClient):
        super().__init__()
        self.api_client = api_client
        self.update_timer = QTimer()
        self.update_timer.setInterval(10000)  # 10 seconds
        self.update_timer.timeout.connect(self.refresh_data)
        
        self._setup_ui()
        self._connect_signals()
        
        logger.info("SCS System Status initialized")
    
    def _setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        title = QLabel("System Health & Status Dashboard")
        title.setStyleSheet(Styles.get_title_style('header'))
        main_layout.addWidget(title)
        
        # Component health table
        self.health_table = ComponentHealthTable()
        main_layout.addWidget(self.health_table)
        
        # Middle row: Storage stats and gauges
        middle_layout = QHBoxLayout()
        
        self.storage_stats = StorageStatistics()
        middle_layout.addWidget(self.storage_stats)
        
        # Metrics gauges
        gauges_layout = QHBoxLayout()
        self.cpu_gauge = MetricGauge("CPU Usage", "%")
        gauges_layout.addWidget(self.cpu_gauge)
        
        self.memory_gauge = MetricGauge("Memory", "%")
        gauges_layout.addWidget(self.memory_gauge)
        
        self.qps_gauge = MetricGauge("QPS", "q/s")
        gauges_layout.addWidget(self.qps_gauge)
        
        middle_layout.addLayout(gauges_layout)
        main_layout.addLayout(middle_layout)
        
        # Alert panel
        self.alert_panel = AlertPanel()
        main_layout.addWidget(self.alert_panel)
    
    def _connect_signals(self):
        """Connect signals"""
        self.api_client.health_check_completed.connect(self._on_health_update)
        self.api_client.stats_received.connect(self._on_stats_update)
    
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
            logger.info("SCS updates started")
    
    def stop_updates(self):
        """Stop automatic updates"""
        if self.update_timer.isActive():
            self.update_timer.stop()
            logger.info("SCS updates stopped")
    
    def refresh_data(self):
        """Refresh system data"""
        try:
            self.api_client.check_health()
            self.api_client.get_stats()
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            self.alert_panel.add_alert("ERROR", "System", f"Refresh failed: {e}")
    
    def _on_health_update(self, data: Dict[str, Any]):
        """Handle health check update"""
        try:
            # Update component health
            components = data.get('components', {})
            for component, status_data in components.items():
                status = status_data.get('status', 'unknown')
                health = status_data.get('health', 'unknown')
                message = status_data.get('message', '')
                self.health_table.update_component(component, status, health, message)
                
                # Add alert if unhealthy
                if health in ['unhealthy', 'degraded']:
                    self.alert_panel.add_alert('WARNING', component, f"{component} is {health}")
        except Exception as e:
            logger.error(f"Error processing health update: {e}")
    
    def _on_stats_update(self, data: Dict[str, Any]):
        """Handle stats update"""
        try:
            # Update storage statistics
            self.storage_stats.update_stats(data)
            
            # Update gauges
            cpu_usage = data.get('cpu_usage', 0)
            self.cpu_gauge.update_value(cpu_usage, 100)
            
            memory_percent = data.get('memory_percent', 0)
            self.memory_gauge.update_value(memory_percent, 100)
            
            qps = data.get('queries_per_second', 0)
            self.qps_gauge.update_value(qps, 100)
            
            # Check for alerts
            if cpu_usage > 90:
                self.alert_panel.add_alert('CRITICAL', 'CPU', f'CPU usage critical: {cpu_usage:.1f}%')
            elif cpu_usage > 70:
                self.alert_panel.add_alert('WARNING', 'CPU', f'CPU usage high: {cpu_usage:.1f}%')
            
            if memory_percent > 90:
                self.alert_panel.add_alert('CRITICAL', 'Memory', f'Memory usage critical: {memory_percent:.1f}%')
            
        except Exception as e:
            logger.error(f"Error processing stats update: {e}")
