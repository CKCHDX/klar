"""
Phase 2: Crawl Control
Real-time web crawling control with progress monitoring and live logging
"""

import logging
import time
from typing import Dict, List, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QPlainTextEdit, QGroupBox, QMessageBox, QFrame,
    QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QTextCursor

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
from kse.crawler.kse_crawler_core import CrawlerCore
from kse.storage.kse_storage_manager import StorageManager

logger = logging.getLogger(__name__)


class CrawlerThread(QThread):
    """Worker thread for web crawling operations"""
    
    # Signals
    progress_updated = pyqtSignal(int, int)  # current, total
    domain_completed = pyqtSignal(str, dict)  # domain, stats
    log_message = pyqtSignal(str, str)  # level, message
    crawl_completed = pyqtSignal(dict)  # final stats
    error_occurred = pyqtSignal(str)  # error message
    
    def __init__(self, config: Dict):
        """Initialize crawler thread"""
        super().__init__()
        self.config = config
        self.crawler: Optional[CrawlerCore] = None
        self.is_running = False
        self.is_paused = False
        self._stop_requested = False
        
        # Statistics
        self.total_domains = 0
        self.domains_completed = 0
        self.total_pages = 0
        self.total_errors = 0
        self.start_time = 0
    
    def run(self):
        """Execute crawling in background thread"""
        try:
            self.is_running = True
            self._stop_requested = False
            self.start_time = time.time()
            
            self.log_message.emit('info', "Initializing crawler...")
            
            # Initialize storage manager
            storage_path = Path(self.config['storage_path'])
            storage_manager = StorageManager(storage_path)
            
            # Get domains to crawl
            domains = self.config['domains']
            self.total_domains = len(domains)
            
            # Initialize crawler
            domain_list = [d['domain'] for d in domains]
            self.crawler = CrawlerCore(
                storage_manager=storage_manager,
                allowed_domains=domain_list,
                user_agent="KSE/3.0 (Klar Search Engine)",
                crawl_delay=self.config.get('crawl_delay', 2.0),
                timeout=10,
                max_retries=3,
                crawl_depth=self.config.get('crawl_depth', 50),
                respect_robots=self.config.get('respect_robots', True),
                dynamic_speed=self.config.get('dynamic_speed', False)
            )
            
            self.log_message.emit('success', f"Crawler initialized for {self.total_domains} domains")
            
            # Crawl each domain
            for idx, domain_info in enumerate(domains):
                if self._stop_requested:
                    self.log_message.emit('warning', "Crawl stopped by user")
                    break
                
                # Handle pause
                while self.is_paused and not self._stop_requested:
                    time.sleep(0.5)
                
                if self._stop_requested:
                    break
                
                domain = domain_info['domain']
                self.log_message.emit('info', f"Starting crawl of {domain}...")
                
                try:
                    # Crawl domain
                    stats = self.crawler.crawl_domain(domain)
                    
                    # Update statistics
                    self.domains_completed += 1
                    self.total_pages += stats.get('pages_crawled', 0)
                    self.total_errors += stats.get('pages_failed', 0)
                    
                    # Emit progress
                    self.progress_updated.emit(self.domains_completed, self.total_domains)
                    self.domain_completed.emit(domain, stats)
                    
                    self.log_message.emit(
                        'success',
                        f"✓ {domain}: {stats.get('pages_crawled', 0)} pages crawled"
                    )
                    
                except Exception as e:
                    self.log_message.emit('error', f"✗ Failed to crawl {domain}: {str(e)}")
                    self.total_errors += 1
                    logger.error(f"Domain crawl failed: {domain}", exc_info=True)
            
            # Crawling complete
            elapsed_time = time.time() - self.start_time
            final_stats = {
                'domains_crawled': self.domains_completed,
                'total_domains': self.total_domains,
                'pages_indexed': self.total_pages,
                'errors': self.total_errors,
                'elapsed_time': elapsed_time,
                'pages_per_second': self.total_pages / elapsed_time if elapsed_time > 0 else 0
            }
            
            # Index the crawled pages
            if self.crawler and self.total_pages > 0:
                self.log_message.emit('info', "Indexing crawled pages...")
                try:
                    from kse.indexing.kse_indexer_pipeline import IndexerPipeline
                    from kse.nlp.kse_nlp_core import NLPCore
                    
                    # Initialize indexer
                    nlp_core = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
                    indexer = IndexerPipeline(storage_manager, nlp_core)
                    
                    # Get crawled pages
                    pages = self.crawler.get_crawled_pages()
                    
                    # Index pages
                    index_stats = indexer.index_pages(pages)
                    
                    self.log_message.emit(
                        'success',
                        f"✓ Indexed {index_stats['pages_indexed']} pages"
                    )
                    
                    # Update stats with actual indexed count
                    final_stats['pages_indexed'] = index_stats['pages_indexed']
                    final_stats['pages_crawled'] = self.total_pages
                    final_stats['total_terms'] = index_stats['total_terms']
                    
                except Exception as e:
                    self.log_message.emit('error', f"Failed to index pages: {str(e)}")
                    logger.error(f"Indexing failed: {e}", exc_info=True)
                    # Set indexed count to 0 on failure
                    final_stats['pages_indexed'] = 0
                    final_stats['pages_crawled'] = self.total_pages
            
            if not self._stop_requested:
                self.log_message.emit('success', "✓ Crawling and indexing completed successfully!")
            
            self.crawl_completed.emit(final_stats)
            
        except Exception as e:
            error_msg = f"Crawler error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.log_message.emit('error', error_msg)
            self.error_occurred.emit(error_msg)
        
        finally:
            self.is_running = False
    
    def pause(self):
        """Pause crawling"""
        self.is_paused = True
        self.log_message.emit('warning', "Crawling paused")
    
    def resume(self):
        """Resume crawling"""
        self.is_paused = False
        self.log_message.emit('info', "Crawling resumed")
    
    def stop(self):
        """Stop crawling"""
        self._stop_requested = True
        self.is_paused = False
        self.log_message.emit('warning', "Stopping crawler...")


class Phase2CrawlControl(QWizardPage):
    """Phase 2: Crawl control and monitoring wizard page"""
    
    # Signals
    crawl_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """Initialize crawl control page"""
        super().__init__(parent)
        
        self.setTitle("Phase 2: Web Crawling")
        self.setSubTitle("Start crawling and monitor progress in real-time")
        
        # State
        self.crawler_thread: Optional[CrawlerThread] = None
        self.is_crawling = False
        self.is_paused = False
        self.crawl_stats: Dict = {}
        
        # Setup UI
        self._init_ui()
        
        # Timer for UI updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_stats_display)
        
        logger.info("Phase 2 (Crawl Control) initialized")
    
    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Control buttons
        control_layout = self._create_control_section()
        layout.addLayout(control_layout)
        
        # Progress section
        progress_group = self._create_progress_section()
        layout.addWidget(progress_group)
        
        # Statistics section
        stats_group = self._create_stats_section()
        layout.addWidget(stats_group)
        
        # Log viewer section
        log_group = self._create_log_section()
        layout.addWidget(log_group, 1)  # Give more space to logs
        
        self.setLayout(layout)
    
    def _create_control_section(self) -> QHBoxLayout:
        """Create control buttons section"""
        layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start Crawling")
        self.start_btn.setStyleSheet(Styles.get_success_button_style())
        self.start_btn.clicked.connect(self._start_crawling)
        layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setStyleSheet(Styles.get_warning_button_style())
        self.pause_btn.clicked.connect(self._pause_crawling)
        self.pause_btn.setEnabled(False)
        layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setStyleSheet(Styles.get_danger_button_style())
        self.stop_btn.clicked.connect(self._stop_crawling)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("Ready to start")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_secondary']};
                font-size: {GUIConfig.get_font_size('medium')}pt;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        layout.addWidget(self.status_label)
        
        return layout
    
    def _create_progress_section(self) -> QGroupBox:
        """Create progress tracking section"""
        group = QGroupBox("Progress")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {GUIConfig.get_font_size('medium')}pt;
                font-weight: bold;
                color: {GUIConfig.COLORS['primary']};
                border: 2px solid {GUIConfig.COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/%m domains (%p%)")
        layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("0 of 0 domains crawled")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addWidget(self.progress_label)
        
        group.setLayout(layout)
        return group
    
    def _create_stats_section(self) -> QGroupBox:
        """Create statistics display section"""
        group = QGroupBox("Statistics")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {GUIConfig.get_font_size('medium')}pt;
                font-weight: bold;
                color: {GUIConfig.COLORS['primary']};
                border: 2px solid {GUIConfig.COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QGridLayout()
        
        # Create metric cards
        self.pages_label = self._create_metric_card("Pages Indexed", "0")
        self.errors_label = self._create_metric_card("Errors", "0")
        self.speed_label = self._create_metric_card("Speed", "0 p/s")
        self.time_label = self._create_metric_card("Elapsed", "0:00")
        
        layout.addWidget(self.pages_label, 0, 0)
        layout.addWidget(self.errors_label, 0, 1)
        layout.addWidget(self.speed_label, 0, 2)
        layout.addWidget(self.time_label, 0, 3)
        
        group.setLayout(layout)
        return group
    
    def _create_metric_card(self, title: str, value: str) -> QFrame:
        """Create a metric display card"""
        frame = QFrame()
        frame.setStyleSheet(Styles.get_metric_card_style())
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_secondary']};
                font-size: {GUIConfig.get_font_size('small')}pt;
            }}
        """)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['primary']};
                font-size: {GUIConfig.get_font_size('header')}pt;
                font-weight: bold;
            }}
        """)
        value_label.setObjectName(f"value_{title}")
        layout.addWidget(value_label)
        
        frame.setLayout(layout)
        return frame
    
    def _create_log_section(self) -> QGroupBox:
        """Create log viewer section"""
        group = QGroupBox("Crawler Log")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {GUIConfig.get_font_size('medium')}pt;
                font-weight: bold;
                color: {GUIConfig.COLORS['primary']};
                border: 2px solid {GUIConfig.COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Log viewer
        self.log_viewer = QPlainTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet(Styles.get_log_viewer_style())
        self.log_viewer.setMaximumBlockCount(1000)  # Limit log size
        layout.addWidget(self.log_viewer)
        
        # Clear log button
        clear_btn = QPushButton("Clear Log")
        clear_btn.setStyleSheet(Styles.get_button_style(size='small'))
        clear_btn.clicked.connect(self.log_viewer.clear)
        layout.addWidget(clear_btn)
        
        group.setLayout(layout)
        return group
    
    def _start_crawling(self):
        """Start the crawling process"""
        # Get configuration from Phase 1
        wizard = self.wizard()
        if not wizard:
            return
        
        phase1 = wizard.page(0)
        if not phase1:
            QMessageBox.warning(self, "Error", "Cannot access Phase 1 configuration")
            return
        
        config = phase1.get_configuration()
        
        # Confirm start
        domain_count = len(config['domains'])
        reply = QMessageBox.question(
            self,
            "Start Crawling",
            f"Start crawling {domain_count} domains?\n\n"
            f"Crawl depth: {config['crawl_depth']} pages per domain\n"
            f"Speed: {config['crawl_speed']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Initialize and start crawler thread
        self.crawler_thread = CrawlerThread(config)
        self.crawler_thread.progress_updated.connect(self._on_progress_updated)
        self.crawler_thread.domain_completed.connect(self._on_domain_completed)
        self.crawler_thread.log_message.connect(self._on_log_message)
        self.crawler_thread.crawl_completed.connect(self._on_crawl_completed)
        self.crawler_thread.error_occurred.connect(self._on_error)
        
        # Update UI
        self.is_crawling = True
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("🟢 Crawling...")
        self.status_label.setStyleSheet(Styles.get_status_label_style('running'))
        
        # Reset progress
        self.progress_bar.setMaximum(domain_count)
        self.progress_bar.setValue(0)
        
        # Start thread and timer
        self.crawler_thread.start()
        self.update_timer.start(1000)  # Update every second
        
        self._log("Started crawling process")
        logger.info("Crawling started")
    
    def _pause_crawling(self):
        """Pause/resume crawling"""
        if not self.crawler_thread:
            return
        
        if self.is_paused:
            self.crawler_thread.resume()
            self.is_paused = False
            self.pause_btn.setText("⏸ Pause")
            self.status_label.setText("🟢 Crawling...")
            self._log("Crawling resumed")
        else:
            self.crawler_thread.pause()
            self.is_paused = True
            self.pause_btn.setText("▶ Resume")
            self.status_label.setText("🟡 Paused")
            self.status_label.setStyleSheet(Styles.get_status_label_style('warning'))
            self._log("Crawling paused")
    
    def _stop_crawling(self):
        """Stop the crawling process"""
        if not self.crawler_thread:
            return
        
        reply = QMessageBox.question(
            self,
            "Stop Crawling",
            "Are you sure you want to stop crawling?\n\nProgress will be saved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.crawler_thread.stop()
            self.status_label.setText("🔴 Stopping...")
            self.status_label.setStyleSheet(Styles.get_status_label_style('stopped'))
    
    def _on_progress_updated(self, current: int, total: int):
        """Handle progress update"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"{current} of {total} domains crawled")
    
    def _on_domain_completed(self, domain: str, stats: Dict):
        """Handle domain completion"""
        pages = stats.get('pages_crawled', 0)
        self._log(f"✓ Completed: {domain} ({pages} pages)")
    
    def _on_log_message(self, level: str, message: str):
        """Handle log message from crawler"""
        self._log(message, level)
    
    def _on_crawl_completed(self, stats: Dict):
        """Handle crawl completion"""
        self.crawl_stats = stats
        self.is_crawling = False
        
        # Stop timer
        self.update_timer.stop()
        
        # Update UI
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("✓ Completed")
        self.status_label.setStyleSheet(Styles.get_status_label_style('running'))
        
        # Show completion message
        elapsed = stats.get('elapsed_time', 0)
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        message = (
            f"Crawling completed!\n\n"
            f"Domains crawled: {stats.get('domains_crawled', 0)}/{stats.get('total_domains', 0)}\n"
            f"Pages crawled: {stats.get('pages_crawled', 0)}\n"
            f"Pages indexed: {stats.get('pages_indexed', 0)}\n"
            f"Terms indexed: {stats.get('total_terms', 0)}\n"
            f"Errors: {stats.get('errors', 0)}\n"
            f"Time: {minutes}m {seconds}s\n"
            f"Speed: {stats.get('pages_per_second', 0):.2f} pages/sec"
        )
        
        QMessageBox.information(self, "Crawl Complete", message)
        
        # Enable next button
        self.completeChanged.emit()
        self.crawl_completed.emit(stats)
        
        logger.info(f"Crawling completed: {stats}")
    
    def _on_error(self, error_msg: str):
        """Handle crawler error"""
        self.is_crawling = False
        self.update_timer.stop()
        
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("✗ Error")
        self.status_label.setStyleSheet(Styles.get_status_label_style('stopped'))
        
        QMessageBox.critical(self, "Crawler Error", f"An error occurred:\n\n{error_msg}")
    
    def _update_stats_display(self):
        """Update statistics display"""
        if not self.crawler_thread or not self.crawler_thread.isRunning():
            return
        
        # Update stats from thread
        thread = self.crawler_thread
        
        # Pages
        pages_value = self.pages_label.findChild(QLabel, "value_Pages Indexed")
        if pages_value:
            pages_value.setText(str(thread.total_pages))
        
        # Errors
        errors_value = self.errors_label.findChild(QLabel, "value_Errors")
        if errors_value:
            errors_value.setText(str(thread.total_errors))
        
        # Speed
        elapsed = time.time() - thread.start_time
        speed = thread.total_pages / elapsed if elapsed > 0 else 0
        speed_value = self.speed_label.findChild(QLabel, "value_Speed")
        if speed_value:
            speed_value.setText(f"{speed:.2f} p/s")
        
        # Time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        time_value = self.time_label.findChild(QLabel, "value_Elapsed")
        if time_value:
            time_value.setText(f"{minutes}:{seconds:02d}")
    
    def _log(self, message: str, level: str = 'info'):
        """Add message to log viewer"""
        # Color-code based on level
        color_map = {
            'info': GUIConfig.COLORS['text_primary'],
            'success': GUIConfig.COLORS['success'],
            'warning': GUIConfig.COLORS['warning'],
            'error': GUIConfig.COLORS['error']
        }
        
        color = color_map.get(level, GUIConfig.COLORS['text_primary'])
        timestamp = time.strftime('%H:%M:%S')
        
        # Append to log (plain text, as HTML styling is complex in QPlainTextEdit)
        self.log_viewer.appendPlainText(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        self.log_viewer.moveCursor(QTextCursor.MoveOperation.End)
    
    def isComplete(self) -> bool:
        """Check if page is complete (crawling finished)"""
        return bool(self.crawl_stats and not self.is_crawling)
    
    def cleanupPage(self):
        """Cleanup when leaving page"""
        if self.crawler_thread and self.crawler_thread.isRunning():
            self.crawler_thread.stop()
            # Wait max 5 seconds for graceful shutdown
            if not self.crawler_thread.wait(5000):
                logger.warning("Crawler thread did not stop within timeout")
        
        if self.update_timer.isActive():
            self.update_timer.stop()
