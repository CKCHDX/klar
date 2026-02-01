"""
Enhanced Domain Management Dialog
Allows adding/removing domains after initial setup with re-crawl support
"""

from typing import List, Dict, Optional, Set
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, 
    QGroupBox, QMessageBox, QProgressBar, QTextEdit, QTabWidget, QWidget,
    QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
import logging

logger = logging.getLogger(__name__)


class ReCrawlWorker(QThread):
    """Worker thread for re-crawling domains"""
    
    progress = pyqtSignal(int, str)  # Progress percentage, status message
    finished = pyqtSignal(bool, str)  # Success, message
    
    def __init__(self, domains: List[str], crawl_config: Dict):
        super().__init__()
        self.domains = domains
        self.crawl_config = crawl_config
        self._is_running = True
    
    def run(self):
        """Execute re-crawl"""
        try:
            logger.info(f"Starting re-crawl for {len(self.domains)} domains")
            self.progress.emit(10, "Initializing crawler...")
            
            # Import crawler components
            from kse.crawler.kse_crawler_core import CrawlerCore
            from kse.storage.kse_storage_manager import StorageManager
            from kse.core.kse_config import ConfigManager
            
            self.progress.emit(20, "Loading configuration...")
            
            # Initialize storage
            config_manager = ConfigManager()
            storage_manager = StorageManager(config_manager.config)
            
            self.progress.emit(30, "Creating crawler instance...")
            
            # Create crawler with configuration
            crawler = CrawlerCore(
                storage_manager=storage_manager,
                allowed_domains=self.domains,
                user_agent=self.crawl_config.get('user_agent', 'KlarBot/3.0'),
                crawl_delay=self.crawl_config.get('crawl_delay', 1.0),
                crawl_depth=self.crawl_config.get('crawl_depth', 100),
                respect_robots=self.crawl_config.get('respect_robots', True),
                dynamic_speed=self.crawl_config.get('dynamic_speed', True),
                max_workers=self.crawl_config.get('max_workers', 5)
            )
            
            self.progress.emit(40, "Starting domain crawl...")
            
            # Crawl domains (with multi-threading if enabled)
            results = crawler.crawl_all_domains(use_threading=True)
            
            self.progress.emit(80, "Updating search index...")
            
            # Re-index the crawled pages
            from kse.indexing.kse_indexer_pipeline import IndexerPipeline
            indexer = IndexerPipeline(storage_manager)
            
            pages = crawler.get_crawled_pages()
            indexer.index_pages(pages)
            
            self.progress.emit(95, "Saving index...")
            indexer.save_index()
            
            self.progress.emit(100, "Completed!")
            
            success_count = sum(1 for r in results.values() if r.get('status') == 'completed')
            message = f"Successfully crawled {success_count}/{len(self.domains)} domains"
            
            self.finished.emit(True, message)
            
        except Exception as e:
            logger.error(f"Re-crawl failed: {e}", exc_info=True)
            self.finished.emit(False, f"Error: {str(e)}")
    
    def stop(self):
        """Stop the re-crawl"""
        self._is_running = False


class DomainManagementDialog(QDialog):
    """Enhanced domain management with add/remove and re-crawl capabilities"""
    
    # Signals
    domains_updated = pyqtSignal(list)  # Updated domain list
    
    def __init__(self, current_domains: List[str], parent=None):
        """
        Initialize domain management dialog
        
        Args:
            current_domains: Currently configured domains
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_domains = list(current_domains)
        self.modified = False
        self.recrawl_worker = None
        
        self.setWindowTitle("Domain Management - Klar Search Engine")
        self.setModal(True)
        self.resize(800, 700)
        
        self._setup_ui()
        self._apply_styles()
        self._load_domains()
        
        logger.info(f"Domain Management Dialog opened with {len(current_domains)} domains")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Manage Search Domains")
        title_font = QFont(GUIConfig.FONTS['family'], 18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Info label
        info_label = QLabel(
            "Add or remove domains to crawl. Changes require re-indexing which will "
            "temporarily stop the search server."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addWidget(info_label)
        
        # Tab widget for different management options
        self.tabs = QTabWidget()
        
        # Tab 1: Domain List Management
        domains_tab = self._create_domains_tab()
        self.tabs.addTab(domains_tab, "Domain List")
        
        # Tab 2: Crawl Configuration
        config_tab = self._create_config_tab()
        self.tabs.addTab(config_tab, "Crawl Settings")
        
        # Tab 3: Re-Crawl Progress
        progress_tab = self._create_progress_tab()
        self.tabs.addTab(progress_tab, "Re-Crawl Progress")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.status_label = QLabel(self._get_status_text())
        self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addWidget(self.status_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_button = QPushButton("Apply Changes & Re-Crawl")
        self.apply_button.clicked.connect(self._apply_changes)
        self.apply_button.setEnabled(False)
        button_layout.addWidget(self.apply_button)
        
        self.save_button = QPushButton("Save Without Re-Crawl")
        self.save_button.clicked.connect(self._save_without_recrawl)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _create_domains_tab(self) -> QWidget:
        """Create the domains management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Add domain section
        add_group = QGroupBox("Add New Domain")
        add_layout = QHBoxLayout(add_group)
        
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Enter domain (e.g., example.com)")
        add_layout.addWidget(self.domain_input)
        
        add_button = QPushButton("Add Domain")
        add_button.clicked.connect(self._add_domain)
        add_layout.addWidget(add_button)
        
        layout.addWidget(add_group)
        
        # Current domains section
        domains_group = QGroupBox("Current Domains")
        domains_layout = QVBoxLayout(domains_group)
        
        self.domain_list = QListWidget()
        self.domain_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        domains_layout.addWidget(self.domain_list)
        
        # Domain list controls
        controls_layout = QHBoxLayout()
        
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self._remove_selected_domains)
        controls_layout.addWidget(remove_button)
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self._clear_all_domains)
        controls_layout.addWidget(clear_button)
        
        controls_layout.addStretch()
        
        import_button = QPushButton("Import from File")
        import_button.clicked.connect(self._import_domains)
        controls_layout.addWidget(import_button)
        
        export_button = QPushButton("Export to File")
        export_button.clicked.connect(self._export_domains)
        controls_layout.addWidget(export_button)
        
        domains_layout.addLayout(controls_layout)
        
        layout.addWidget(domains_group)
        
        return tab
    
    def _create_config_tab(self) -> QWidget:
        """Create the crawl configuration tab"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(12)
        
        # Crawl depth
        self.crawl_depth_spin = QSpinBox()
        self.crawl_depth_spin.setRange(10, 10000)
        self.crawl_depth_spin.setValue(100)
        self.crawl_depth_spin.setSuffix(" pages per domain")
        layout.addRow("Crawl Depth:", self.crawl_depth_spin)
        
        # Crawl delay
        self.crawl_delay_spin = QDoubleSpinBox()
        self.crawl_delay_spin.setRange(0.1, 10.0)
        self.crawl_delay_spin.setValue(1.0)
        self.crawl_delay_spin.setSingleStep(0.1)
        self.crawl_delay_spin.setSuffix(" seconds")
        layout.addRow("Crawl Delay:", self.crawl_delay_spin)
        
        # Max workers (threads)
        self.max_workers_spin = QSpinBox()
        self.max_workers_spin.setRange(1, 20)
        self.max_workers_spin.setValue(5)
        self.max_workers_spin.setSuffix(" workers")
        layout.addRow("Parallel Workers:", self.max_workers_spin)
        
        # Respect robots.txt
        self.respect_robots_check = QCheckBox("Respect robots.txt")
        self.respect_robots_check.setChecked(True)
        layout.addRow("Robots.txt:", self.respect_robots_check)
        
        # Dynamic speed
        self.dynamic_speed_check = QCheckBox("Use dynamic crawl speed from robots.txt")
        self.dynamic_speed_check.setChecked(True)
        layout.addRow("Dynamic Speed:", self.dynamic_speed_check)
        
        # Info text
        info_text = QLabel(
            "<b>Note:</b> Multi-threaded crawling (parallel workers) significantly "
            "speeds up large crawls. Recommended: 5-10 workers for enterprise use."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addRow("", info_text)
        
        return tab
    
    def _create_progress_tab(self) -> QWidget:
        """Create the re-crawl progress tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Progress bar
        progress_group = QGroupBox("Crawl Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_status = QLabel("Ready to crawl")
        self.progress_status.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        progress_layout.addWidget(self.progress_status)
        
        layout.addWidget(progress_group)
        
        # Log output
        log_group = QGroupBox("Crawl Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(300)
        log_layout.addWidget(self.log_output)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        return tab
    
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
        """Load current domains into the list"""
        self.domain_list.clear()
        for domain in sorted(self.current_domains):
            self.domain_list.addItem(QListWidgetItem(domain))
        self._update_status()
    
    def _add_domain(self):
        """Add a new domain"""
        domain = self.domain_input.text().strip().lower()
        
        if not domain:
            QMessageBox.warning(self, "Invalid Input", "Please enter a domain name.")
            return
        
        # Basic validation
        if ' ' in domain:
            QMessageBox.warning(self, "Invalid Domain", "Domain cannot contain spaces.")
            return
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if already exists
        if domain in self.current_domains:
            QMessageBox.information(self, "Duplicate", f"Domain '{domain}' is already in the list.")
            return
        
        # Add to list
        self.current_domains.append(domain)
        self.domain_list.addItem(QListWidgetItem(domain))
        self.domain_input.clear()
        
        self.modified = True
        self._update_status()
        
        logger.info(f"Added domain: {domain}")
    
    def _remove_selected_domains(self):
        """Remove selected domains"""
        selected_items = self.domain_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select domains to remove.")
            return
        
        # Confirm removal
        domains_to_remove = [item.text() for item in selected_items]
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove {len(domains_to_remove)} domain(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for domain in domains_to_remove:
                self.current_domains.remove(domain)
            
            for item in selected_items:
                self.domain_list.takeItem(self.domain_list.row(item))
            
            self.modified = True
            self._update_status()
            
            logger.info(f"Removed {len(domains_to_remove)} domains")
    
    def _clear_all_domains(self):
        """Clear all domains"""
        if not self.current_domains:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Remove ALL domains? This will require adding new ones.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_domains.clear()
            self.domain_list.clear()
            self.modified = True
            self._update_status()
            logger.info("Cleared all domains")
    
    def _import_domains(self):
        """Import domains from a file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Domains",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    domains = [line.strip().lower() for line in f if line.strip()]
                
                added_count = 0
                for domain in domains:
                    if domain and domain not in self.current_domains:
                        self.current_domains.append(domain)
                        self.domain_list.addItem(QListWidgetItem(domain))
                        added_count += 1
                
                if added_count > 0:
                    self.modified = True
                    self._update_status()
                
                QMessageBox.information(
                    self,
                    "Import Complete",
                    f"Imported {added_count} new domain(s)."
                )
                
                logger.info(f"Imported {added_count} domains from {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import: {str(e)}")
                logger.error(f"Domain import failed: {e}")
    
    def _export_domains(self):
        """Export domains to a file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Domains",
            "domains.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    for domain in sorted(self.current_domains):
                        f.write(f"{domain}\n")
                
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Exported {len(self.current_domains)} domain(s)."
                )
                
                logger.info(f"Exported {len(self.current_domains)} domains to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
                logger.error(f"Domain export failed: {e}")
    
    def _update_status(self):
        """Update status label and button states"""
        self.status_label.setText(self._get_status_text())
        self.apply_button.setEnabled(self.modified and len(self.current_domains) > 0)
        self.save_button.setEnabled(self.modified and len(self.current_domains) > 0)
    
    def _get_status_text(self) -> str:
        """Get status text"""
        status = f"Total Domains: {len(self.current_domains)}"
        if self.modified:
            status += " (Modified - unsaved changes)"
        return status
    
    def _save_without_recrawl(self):
        """Save domain changes without re-crawling"""
        if not self.current_domains:
            QMessageBox.warning(
                self,
                "No Domains",
                "You must have at least one domain configured."
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Save Without Re-Crawl",
            "Save domain changes without re-crawling?\n\n"
            "The search index will be outdated until you perform a manual crawl.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._save_domains()
            self.domains_updated.emit(self.current_domains)
            self.accept()
    
    def _apply_changes(self):
        """Apply changes and start re-crawl"""
        if not self.current_domains:
            QMessageBox.warning(
                self,
                "No Domains",
                "You must have at least one domain configured."
            )
            return
        
        # Confirm re-crawl
        reply = QMessageBox.question(
            self,
            "Confirm Re-Crawl",
            f"Re-crawl {len(self.current_domains)} domain(s)?\n\n"
            "This will:\n"
            "• Stop the search server temporarily\n"
            "• Crawl all domains with current settings\n"
            "• Rebuild the search index\n"
            "• Restart the server\n\n"
            f"Estimated time: {self._estimate_crawl_time()} minutes",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._start_recrawl()
    
    def _estimate_crawl_time(self) -> int:
        """Estimate crawl time in minutes"""
        depth = self.crawl_depth_spin.value()
        workers = self.max_workers_spin.value()
        delay = self.crawl_delay_spin.value()
        domains = len(self.current_domains)
        
        # Simple estimation: (domains * depth * delay) / (workers * 60)
        # Assumes average crawl time with overhead
        estimated_seconds = (domains * depth * delay) / workers
        return max(1, int(estimated_seconds / 60))
    
    def _start_recrawl(self):
        """Start the re-crawl process"""
        # Switch to progress tab
        self.tabs.setCurrentIndex(2)
        
        # Disable buttons
        self.apply_button.setEnabled(False)
        self.save_button.setEnabled(False)
        
        # Prepare crawl configuration
        crawl_config = {
            'crawl_depth': self.crawl_depth_spin.value(),
            'crawl_delay': self.crawl_delay_spin.value(),
            'max_workers': self.max_workers_spin.value(),
            'respect_robots': self.respect_robots_check.isChecked(),
            'dynamic_speed': self.dynamic_speed_check.isChecked(),
            'user_agent': 'KlarBot/3.0 (Enterprise Swedish Search Engine)'
        }
        
        # Create and start worker
        self.recrawl_worker = ReCrawlWorker(self.current_domains, crawl_config)
        self.recrawl_worker.progress.connect(self._on_crawl_progress)
        self.recrawl_worker.finished.connect(self._on_crawl_finished)
        self.recrawl_worker.start()
        
        self.log_output.append(f"Starting re-crawl of {len(self.current_domains)} domains...")
        self.log_output.append(f"Configuration: {crawl_config}")
        self.log_output.append("-" * 50)
    
    def _on_crawl_progress(self, percent: int, status: str):
        """Handle crawl progress update"""
        self.progress_bar.setValue(percent)
        self.progress_status.setText(status)
        self.log_output.append(f"[{percent}%] {status}")
    
    def _on_crawl_finished(self, success: bool, message: str):
        """Handle crawl completion"""
        self.log_output.append("-" * 50)
        self.log_output.append(f"Re-crawl {'completed' if success else 'failed'}: {message}")
        
        if success:
            self._save_domains()
            QMessageBox.information(
                self,
                "Re-Crawl Complete",
                f"{message}\n\nThe search index has been updated."
            )
            self.domains_updated.emit(self.current_domains)
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Re-Crawl Failed",
                f"{message}\n\nPlease check the logs for details."
            )
            # Re-enable buttons
            self.apply_button.setEnabled(True)
            self.save_button.setEnabled(True)
    
    def _save_domains(self):
        """Save domain configuration to config file"""
        try:
            from kse.core.kse_config import ConfigManager
            
            config_manager = ConfigManager()
            config_manager.set("crawler.allowed_domains", self.current_domains)
            config_manager.save_config()
            
            logger.info(f"Saved {len(self.current_domains)} domains to configuration")
            
        except Exception as e:
            logger.error(f"Failed to save domains: {e}")
            QMessageBox.warning(
                self,
                "Save Warning",
                f"Failed to save configuration: {str(e)}"
            )
    
    def get_domains(self) -> List[str]:
        """Get the current domain list"""
        return self.current_domains.copy()
