"""
AUXILIARY CONTROL CENTER (ACC)
System maintenance, diagnostics, and optimization tools
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QTextEdit, QProgressBar,
    QGroupBox, QCheckBox, QSpinBox, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
from gui.control_center.control_center_api_client import ControlCenterAPIClient

logger = logging.getLogger(__name__)


class IndexRebuildPanel(QFrame):
    """Index rebuild panel with progress tracking"""
    
    rebuild_requested = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        self.is_rebuilding = False
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Index Rebuild")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Options
        options_group = QGroupBox("Rebuild Options")
        options_layout = QVBoxLayout(options_group)
        
        self.full_rebuild_check = QCheckBox("Full rebuild (delete and recreate)")
        self.full_rebuild_check.setChecked(False)
        options_layout.addWidget(self.full_rebuild_check)
        
        self.optimize_check = QCheckBox("Optimize after rebuild")
        self.optimize_check.setChecked(True)
        options_layout.addWidget(self.optimize_check)
        
        self.verify_check = QCheckBox("Verify data integrity")
        self.verify_check.setChecked(True)
        options_layout.addWidget(self.verify_check)
        
        layout.addWidget(options_group)
        
        # Progress
        progress_layout = QVBoxLayout()
        
        self.progress_label = QLabel("Ready to rebuild")
        self.progress_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
                text-align: center;
                height: 24px;
            }}
            QProgressBar::chunk {{
                background-color: {GUIConfig.COLORS['success']};
                border-radius: 3px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addLayout(progress_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start Rebuild")
        self.start_btn.setStyleSheet(Styles.get_button_style())
        self.start_btn.clicked.connect(self._on_start)
        buttons_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("⬛ Cancel")
        self.cancel_btn.setStyleSheet(Styles.get_danger_button_style())
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.setEnabled(False)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_start(self):
        """Handle start rebuild"""
        options = {
            'full_rebuild': self.full_rebuild_check.isChecked(),
            'optimize': self.optimize_check.isChecked(),
            'verify': self.verify_check.isChecked()
        }
        
        self.is_rebuilding = True
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_label.setText("Rebuilding index...")
        self.progress_bar.setValue(0)
        
        self.rebuild_requested.emit(options)
    
    def _on_cancel(self):
        """Handle cancel rebuild"""
        self.is_rebuilding = False
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_label.setText("Rebuild cancelled")
    
    def update_progress(self, progress: int, message: str = ""):
        """Update rebuild progress"""
        self.progress_bar.setValue(progress)
        if message:
            self.progress_label.setText(message)
        
        if progress >= 100:
            self.is_rebuilding = False
            self.start_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            self.progress_label.setText("Rebuild completed successfully")


class DataCleanupPanel(QFrame):
    """Data cleanup and optimization tools"""
    
    cleanup_requested = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Data Cleanup & Optimization")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Cleanup options
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(8)
        
        # Clear cache
        self.clear_cache_btn = QPushButton("🗑️ Clear Search Cache")
        self.clear_cache_btn.setStyleSheet(Styles.get_button_style())
        self.clear_cache_btn.clicked.connect(lambda: self.cleanup_requested.emit('cache'))
        buttons_layout.addWidget(self.clear_cache_btn, 0, 0)
        
        # Clear logs
        self.clear_logs_btn = QPushButton("📄 Clear Old Logs")
        self.clear_logs_btn.setStyleSheet(Styles.get_button_style())
        self.clear_logs_btn.clicked.connect(lambda: self.cleanup_requested.emit('logs'))
        buttons_layout.addWidget(self.clear_logs_btn, 0, 1)
        
        # Compact database
        self.compact_db_btn = QPushButton("💾 Compact Database")
        self.compact_db_btn.setStyleSheet(Styles.get_button_style())
        self.compact_db_btn.clicked.connect(lambda: self.cleanup_requested.emit('database'))
        buttons_layout.addWidget(self.compact_db_btn, 1, 0)
        
        # Optimize index
        self.optimize_idx_btn = QPushButton("⚡ Optimize Index")
        self.optimize_idx_btn.setStyleSheet(Styles.get_button_style())
        self.optimize_idx_btn.clicked.connect(lambda: self.cleanup_requested.emit('index'))
        buttons_layout.addWidget(self.optimize_idx_btn, 1, 1)
        
        # Remove duplicates
        self.remove_dups_btn = QPushButton("🔍 Remove Duplicates")
        self.remove_dups_btn.setStyleSheet(Styles.get_button_style())
        self.remove_dups_btn.clicked.connect(lambda: self.cleanup_requested.emit('duplicates'))
        buttons_layout.addWidget(self.remove_dups_btn, 2, 0)
        
        # Vacuum storage
        self.vacuum_btn = QPushButton("🧹 Vacuum Storage")
        self.vacuum_btn.setStyleSheet(Styles.get_button_style())
        self.vacuum_btn.clicked.connect(lambda: self.cleanup_requested.emit('vacuum'))
        buttons_layout.addWidget(self.vacuum_btn, 2, 1)
        
        layout.addLayout(buttons_layout)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addWidget(self.status_label)
    
    def update_status(self, message: str):
        """Update status message"""
        self.status_label.setText(message)


class ConsistencyChecker(QFrame):
    """Data consistency checker with reporting"""
    
    check_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Consistency Checker")
        title.setStyleSheet(Styles.get_title_style('medium'))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.check_btn = QPushButton("🔍 Run Check")
        self.check_btn.setStyleSheet(Styles.get_button_style())
        self.check_btn.clicked.connect(self._on_check)
        header_layout.addWidget(self.check_btn)
        
        layout.addLayout(header_layout)
        
        # Report area
        self.report_text = QTextEdit()
        self.report_text.setStyleSheet(Styles.get_log_viewer_style())
        self.report_text.setReadOnly(True)
        self.report_text.setMaximumHeight(200)
        self.report_text.setPlaceholderText("Consistency check results will appear here...")
        
        layout.addWidget(self.report_text)
    
    def _on_check(self):
        """Handle check request"""
        self.report_text.clear()
        self.report_text.append("Running consistency checks...\n")
        self.check_btn.setEnabled(False)
        self.check_requested.emit()
    
    def update_report(self, report: str):
        """Update consistency report"""
        self.report_text.append(report)
        self.check_btn.setEnabled(True)


class LogRotationControl(QFrame):
    """Log rotation controls"""
    
    rotate_requested = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Log Rotation")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Settings
        settings_layout = QGridLayout()
        
        # Max size
        settings_layout.addWidget(QLabel("Max Log Size (MB):"), 0, 0)
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(1, 1000)
        self.max_size_spin.setValue(100)
        settings_layout.addWidget(self.max_size_spin, 0, 1)
        
        # Max age
        settings_layout.addWidget(QLabel("Max Age (days):"), 1, 0)
        self.max_age_spin = QSpinBox()
        self.max_age_spin.setRange(1, 365)
        self.max_age_spin.setValue(30)
        settings_layout.addWidget(self.max_age_spin, 1, 1)
        
        # Backup count
        settings_layout.addWidget(QLabel("Backup Count:"), 2, 0)
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setRange(1, 50)
        self.backup_count_spin.setValue(5)
        settings_layout.addWidget(self.backup_count_spin, 2, 1)
        
        layout.addLayout(settings_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.rotate_now_btn = QPushButton("🔄 Rotate Now")
        self.rotate_now_btn.setStyleSheet(Styles.get_button_style())
        self.rotate_now_btn.clicked.connect(self._on_rotate)
        buttons_layout.addWidget(self.rotate_now_btn)
        
        self.apply_btn = QPushButton("💾 Apply Settings")
        self.apply_btn.setStyleSheet(Styles.get_button_style())
        self.apply_btn.clicked.connect(self._on_apply)
        buttons_layout.addWidget(self.apply_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_rotate(self):
        """Handle rotate now"""
        self.rotate_requested.emit({'action': 'rotate'})
    
    def _on_apply(self):
        """Handle apply settings"""
        settings = {
            'action': 'apply',
            'max_size_mb': self.max_size_spin.value(),
            'max_age_days': self.max_age_spin.value(),
            'backup_count': self.backup_count_spin.value()
        }
        self.rotate_requested.emit(settings)


class DiagnosticsPanel(QFrame):
    """System diagnostics panel"""
    
    diagnostics_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("System Diagnostics")
        title.setStyleSheet(Styles.get_title_style('medium'))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.run_btn = QPushButton("🔧 Run Diagnostics")
        self.run_btn.setStyleSheet(Styles.get_button_style())
        self.run_btn.clicked.connect(self._on_run)
        header_layout.addWidget(self.run_btn)
        
        layout.addLayout(header_layout)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setStyleSheet(Styles.get_log_viewer_style())
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        self.results_text.setPlaceholderText("Diagnostics results will appear here...")
        
        layout.addWidget(self.results_text)
    
    def _on_run(self):
        """Handle run diagnostics"""
        self.results_text.clear()
        self.results_text.append("Running system diagnostics...\n")
        self.run_btn.setEnabled(False)
        self.diagnostics_requested.emit()
    
    def update_results(self, results: str):
        """Update diagnostics results"""
        self.results_text.append(results)
        self.run_btn.setEnabled(True)


class ACCAuxiliaryControl(QWidget):
    """Auxiliary Control Center - Maintenance & Diagnostics"""
    
    def __init__(self, api_client: ControlCenterAPIClient):
        super().__init__()
        self.api_client = api_client
        self.update_timer = QTimer()
        self.update_timer.setInterval(30000)  # 30 seconds
        self.update_timer.timeout.connect(self.refresh_data)
        
        self._setup_ui()
        self._connect_signals()
        
        logger.info("ACC Auxiliary Control initialized")
    
    def _setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        title = QLabel("System Maintenance & Diagnostics")
        title.setStyleSheet(Styles.get_title_style('header'))
        main_layout.addWidget(title)
        
        # Index rebuild panel
        self.rebuild_panel = IndexRebuildPanel()
        main_layout.addWidget(self.rebuild_panel)
        
        # Data cleanup panel
        self.cleanup_panel = DataCleanupPanel()
        main_layout.addWidget(self.cleanup_panel)
        
        # Middle row: Consistency checker and log rotation
        middle_layout = QHBoxLayout()
        
        self.consistency_checker = ConsistencyChecker()
        middle_layout.addWidget(self.consistency_checker)
        
        self.log_rotation = LogRotationControl()
        middle_layout.addWidget(self.log_rotation)
        
        main_layout.addLayout(middle_layout)
        
        # Diagnostics panel
        self.diagnostics_panel = DiagnosticsPanel()
        main_layout.addWidget(self.diagnostics_panel)
        
        main_layout.addStretch()
    
    def _connect_signals(self):
        """Connect signals"""
        self.rebuild_panel.rebuild_requested.connect(self._on_rebuild_index)
        self.cleanup_panel.cleanup_requested.connect(self._on_cleanup)
        self.consistency_checker.check_requested.connect(self._on_consistency_check)
        self.log_rotation.rotate_requested.connect(self._on_log_rotation)
        self.diagnostics_panel.diagnostics_requested.connect(self._on_run_diagnostics)
    
    def showEvent(self, event):
        """Handle widget show event"""
        super().showEvent(event)
        self.start_updates()
    
    def hideEvent(self, event):
        """Handle widget hide event"""
        super().hideEvent(event)
        self.stop_updates()
    
    def start_updates(self):
        """Start automatic updates"""
        if not self.update_timer.isActive():
            self.update_timer.start()
            logger.info("ACC updates started")
    
    def stop_updates(self):
        """Stop automatic updates"""
        if self.update_timer.isActive():
            self.update_timer.stop()
            logger.info("ACC updates stopped")
    
    def refresh_data(self):
        """Refresh auxiliary data"""
        try:
            # Periodic status checks
            pass
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
    
    def _on_rebuild_index(self, options: Dict[str, Any]):
        """Handle index rebuild request"""
        logger.info(f"Index rebuild requested with options: {options}")
        # Simulate progress
        QTimer.singleShot(1000, lambda: self.rebuild_panel.update_progress(25, "Scanning documents..."))
        QTimer.singleShot(2000, lambda: self.rebuild_panel.update_progress(50, "Building index..."))
        QTimer.singleShot(3000, lambda: self.rebuild_panel.update_progress(75, "Optimizing..."))
        QTimer.singleShot(4000, lambda: self.rebuild_panel.update_progress(100, "Completed"))
    
    def _on_cleanup(self, cleanup_type: str):
        """Handle cleanup request"""
        logger.info(f"Cleanup requested: {cleanup_type}")
        self.cleanup_panel.update_status(f"Running {cleanup_type} cleanup...")
        
        # Simulate cleanup
        QTimer.singleShot(2000, lambda: self.cleanup_panel.update_status(
            f"{cleanup_type.capitalize()} cleanup completed successfully"
        ))
    
    def _on_consistency_check(self):
        """Handle consistency check request"""
        logger.info("Consistency check requested")
        
        # Simulate check results
        report = """
Checking index integrity... OK
Checking database consistency... OK
Checking file references... 3 orphaned files found
Checking duplicate entries... OK
Checking metadata... OK

Summary:
- Total documents: 12,450
- Total issues: 3
- Status: HEALTHY (with minor issues)
        """
        
        QTimer.singleShot(2000, lambda: self.consistency_checker.update_report(report))
    
    def _on_log_rotation(self, settings: Dict[str, Any]):
        """Handle log rotation request"""
        logger.info(f"Log rotation requested: {settings}")
        # Log rotation logic would go here
    
    def _on_run_diagnostics(self):
        """Handle diagnostics request"""
        logger.info("System diagnostics requested")
        
        # Simulate diagnostics
        results = f"""
System Diagnostics Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

[✓] CPU: Available cores: 8, Load average: 2.3
[✓] Memory: 8.5 GB used / 16 GB total (53%)
[✓] Disk: 125 GB used / 500 GB total (25%)
[✓] Network: Connection to backend: OK
[✓] Index: 12,450 documents indexed
[✓] Cache: 256 MB / 512 MB (50%)
[!] Log files: 3 files exceeding 100 MB
[✓] Database: Consistent and optimized

Overall Status: HEALTHY
Recommendations: Consider rotating large log files
        """
        
        QTimer.singleShot(2000, lambda: self.diagnostics_panel.update_results(results))
