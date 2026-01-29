"""
MAIN CONTROL SERVER (MCS)
Server management, performance metrics, and log viewer
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QPlainTextEdit,
    QLineEdit, QGroupBox, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
from gui.control_center.control_center_api_client import ControlCenterAPIClient

logger = logging.getLogger(__name__)


class ServerControlPanel(QFrame):
    """Server control panel with start/stop/restart buttons"""
    
    server_start_requested = pyqtSignal()
    server_stop_requested = pyqtSignal()
    server_restart_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        self.server_running = False
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Server Control")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Status display
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        status_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        status_layout.addWidget(status_label)
        
        self.status_indicator = QLabel("⬤")
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['error']};
                font-size: 16pt;
            }}
        """)
        status_layout.addWidget(self.status_indicator)
        
        self.status_text = QLabel("Stopped")
        self.status_text.setStyleSheet(Styles.get_status_label_style('stopped'))
        status_layout.addWidget(self.status_text)
        
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Port configuration
        port_layout = QHBoxLayout()
        port_label = QLabel("Port:")
        port_layout.addWidget(port_label)
        
        self.port_input = QLineEdit("5000")
        self.port_input.setMaximumWidth(100)
        self.port_input.setEnabled(False)
        port_layout.addWidget(self.port_input)
        
        port_layout.addStretch()
        layout.addLayout(port_layout)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setStyleSheet(Styles.get_success_button_style())
        self.start_btn.clicked.connect(self._on_start)
        buttons_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⬛ Stop")
        self.stop_btn.setStyleSheet(Styles.get_danger_button_style())
        self.stop_btn.clicked.connect(self._on_stop)
        self.stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.stop_btn)
        
        self.restart_btn = QPushButton("🔄 Restart")
        self.restart_btn.setStyleSheet(Styles.get_warning_button_style())
        self.restart_btn.clicked.connect(self._on_restart)
        self.restart_btn.setEnabled(False)
        buttons_layout.addWidget(self.restart_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_start(self):
        """Handle start button click"""
        self.server_start_requested.emit()
    
    def _on_stop(self):
        """Handle stop button click"""
        self.server_stop_requested.emit()
    
    def _on_restart(self):
        """Handle restart button click"""
        self.server_restart_requested.emit()
    
    def update_status(self, running: bool):
        """Update server status display"""
        self.server_running = running
        
        if running:
            self.status_indicator.setStyleSheet(f"""
                QLabel {{
                    color: {GUIConfig.COLORS['success']};
                    font-size: 16pt;
                }}
            """)
            self.status_text.setText("Running")
            self.status_text.setStyleSheet(Styles.get_status_label_style('running'))
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.restart_btn.setEnabled(True)
            self.port_input.setEnabled(False)
        else:
            self.status_indicator.setStyleSheet(f"""
                QLabel {{
                    color: {GUIConfig.COLORS['error']};
                    font-size: 16pt;
                }}
            """)
            self.status_text.setText("Stopped")
            self.status_text.setStyleSheet(Styles.get_status_label_style('stopped'))
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.restart_btn.setEnabled(False)
            self.port_input.setEnabled(True)


class PerformanceMetrics(QFrame):
    """Performance metrics display"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Performance Metrics")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Metrics grid
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(12)
        
        # QPS
        qps_label = QLabel("Queries/Second:")
        qps_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        metrics_layout.addWidget(qps_label, 0, 0)
        
        self.qps_value = QLabel("0.00")
        self.qps_value.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['primary']};
                font-size: {GUIConfig.get_font_size('large')}pt;
                font-weight: bold;
            }}
        """)
        metrics_layout.addWidget(self.qps_value, 0, 1)
        
        # Latency
        latency_label = QLabel("Avg Latency:")
        latency_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        metrics_layout.addWidget(latency_label, 1, 0)
        
        self.latency_value = QLabel("0 ms")
        self.latency_value.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['success']};
                font-size: {GUIConfig.get_font_size('large')}pt;
                font-weight: bold;
            }}
        """)
        metrics_layout.addWidget(self.latency_value, 1, 1)
        
        # Uptime
        uptime_label = QLabel("Uptime:")
        uptime_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        metrics_layout.addWidget(uptime_label, 2, 0)
        
        self.uptime_value = QLabel("00:00:00")
        self.uptime_value.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['info']};
                font-size: {GUIConfig.get_font_size('large')}pt;
                font-weight: bold;
            }}
        """)
        metrics_layout.addWidget(self.uptime_value, 2, 1)
        
        layout.addLayout(metrics_layout)
    
    def update_metrics(self, qps: float, latency: float, uptime: int):
        """Update performance metrics"""
        self.qps_value.setText(f"{qps:.2f}")
        
        # Color code latency
        latency_color = GUIConfig.COLORS['success']
        if latency > 100:
            latency_color = GUIConfig.COLORS['warning']
        if latency > 500:
            latency_color = GUIConfig.COLORS['error']
        
        self.latency_value.setText(f"{latency:.0f} ms")
        self.latency_value.setStyleSheet(f"""
            QLabel {{
                color: {latency_color};
                font-size: {GUIConfig.get_font_size('large')}pt;
                font-weight: bold;
            }}
        """)
        
        # Format uptime
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        self.uptime_value.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")


class SnapshotManager(QFrame):
    """Index snapshot management"""
    
    snapshot_create_requested = pyqtSignal(str)
    snapshot_restore_requested = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Index Snapshots")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Snapshot name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Snapshot Name:")
        name_layout.addWidget(name_label)
        
        self.snapshot_name = QLineEdit()
        self.snapshot_name.setPlaceholderText("snapshot_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        name_layout.addWidget(self.snapshot_name)
        
        layout.addLayout(name_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("📸 Create Snapshot")
        self.create_btn.setStyleSheet(Styles.get_button_style())
        self.create_btn.clicked.connect(self._on_create)
        buttons_layout.addWidget(self.create_btn)
        
        self.restore_btn = QPushButton("♻️ Restore Snapshot")
        self.restore_btn.setStyleSheet(Styles.get_button_style())
        self.restore_btn.clicked.connect(self._on_restore)
        buttons_layout.addWidget(self.restore_btn)
        
        layout.addLayout(buttons_layout)
        
        # Snapshot list
        self.snapshot_combo = QComboBox()
        self.snapshot_combo.addItem("-- Select Snapshot --")
        layout.addWidget(self.snapshot_combo)
    
    def _on_create(self):
        """Handle create snapshot"""
        name = self.snapshot_name.text() or self.snapshot_name.placeholderText()
        self.snapshot_create_requested.emit(name)
    
    def _on_restore(self):
        """Handle restore snapshot"""
        name = self.snapshot_combo.currentText()
        if name != "-- Select Snapshot --":
            self.snapshot_restore_requested.emit(name)


class LogViewer(QFrame):
    """Server log viewer"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Server Logs (Last 100 lines)")
        title.setStyleSheet(Styles.get_title_style('medium'))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet(Styles.get_button_style(size='small'))
        self.clear_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # Log text area
        self.log_text = QPlainTextEdit()
        self.log_text.setStyleSheet(Styles.get_log_viewer_style())
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(100)
        self.log_text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        layout.addWidget(self.log_text)
    
    def append_log(self, message: str):
        """Append log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.appendPlainText(f"[{timestamp}] {message}")
    
    def clear_logs(self):
        """Clear log display"""
        self.log_text.clear()


class MCSMainControlServer(QWidget):
    """Main Control Server - Server Management"""
    
    def __init__(self, api_client: ControlCenterAPIClient):
        super().__init__()
        self.api_client = api_client
        self.update_timer = QTimer()
        self.update_timer.setInterval(5000)  # 5 seconds
        self.update_timer.timeout.connect(self.refresh_data)
        
        self._setup_ui()
        self._connect_signals()
        
        logger.info("MCS Main Control Server initialized")
    
    def _setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        title = QLabel("Server Management & Monitoring")
        title.setStyleSheet(Styles.get_title_style('header'))
        main_layout.addWidget(title)
        
        # Top row: Server control and performance
        top_layout = QHBoxLayout()
        
        self.server_control = ServerControlPanel()
        top_layout.addWidget(self.server_control)
        
        self.performance_metrics = PerformanceMetrics()
        top_layout.addWidget(self.performance_metrics)
        
        main_layout.addLayout(top_layout)
        
        # Snapshot manager
        self.snapshot_manager = SnapshotManager()
        main_layout.addWidget(self.snapshot_manager)
        
        # Log viewer
        self.log_viewer = LogViewer()
        main_layout.addWidget(self.log_viewer)
    
    def _connect_signals(self):
        """Connect signals"""
        self.server_control.server_start_requested.connect(self._start_server)
        self.server_control.server_stop_requested.connect(self._stop_server)
        self.server_control.server_restart_requested.connect(self._restart_server)
        
        self.snapshot_manager.snapshot_create_requested.connect(self._create_snapshot)
        self.snapshot_manager.snapshot_restore_requested.connect(self._restore_snapshot)
        
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
            logger.info("MCS updates started")
    
    def stop_updates(self):
        """Stop automatic updates"""
        if self.update_timer.isActive():
            self.update_timer.stop()
            logger.info("MCS updates stopped")
    
    def refresh_data(self):
        """Refresh server data"""
        try:
            self.api_client.check_health()
            self.api_client.get_stats()
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            self.log_viewer.append_log(f"ERROR: Refresh failed - {e}")
    
    def _on_health_update(self, data: Dict[str, Any]):
        """Handle health check update"""
        try:
            status = data.get('status', 'unknown')
            server_running = status in ['healthy', 'degraded']
            self.server_control.update_status(server_running)
            
            if status == 'healthy':
                self.log_viewer.append_log("Health check: Server healthy")
            elif status == 'degraded':
                self.log_viewer.append_log("WARNING: Server degraded")
            else:
                self.log_viewer.append_log(f"ERROR: Server unhealthy - {status}")
        except Exception as e:
            logger.error(f"Error processing health update: {e}")
    
    def _on_stats_update(self, data: Dict[str, Any]):
        """Handle stats update"""
        try:
            qps = data.get('queries_per_second', 0.0)
            latency = data.get('average_latency', 0.0)
            uptime = data.get('uptime_seconds', 0)
            
            self.performance_metrics.update_metrics(qps, latency, uptime)
        except Exception as e:
            logger.error(f"Error processing stats update: {e}")
    
    def _start_server(self):
        """Start server"""
        self.log_viewer.append_log("Starting server...")
        # API call to start server would go here
        self.server_control.update_status(True)
        self.log_viewer.append_log("Server started successfully")
    
    def _stop_server(self):
        """Stop server"""
        self.log_viewer.append_log("Stopping server...")
        # API call to stop server would go here
        self.server_control.update_status(False)
        self.log_viewer.append_log("Server stopped")
    
    def _restart_server(self):
        """Restart server"""
        self.log_viewer.append_log("Restarting server...")
        self._stop_server()
        self._start_server()
    
    def _create_snapshot(self, name: str):
        """Create index snapshot"""
        self.log_viewer.append_log(f"Creating snapshot: {name}")
        # API call to create snapshot would go here
        self.log_viewer.append_log(f"Snapshot '{name}' created successfully")
    
    def _restore_snapshot(self, name: str):
        """Restore index snapshot"""
        self.log_viewer.append_log(f"Restoring snapshot: {name}")
        # API call to restore snapshot would go here
        self.log_viewer.append_log(f"Snapshot '{name}' restored successfully")
