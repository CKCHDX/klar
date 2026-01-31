"""
Phase 1: Storage Configuration
Storage path selection, domain configuration, and crawl settings
"""

import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QSpinBox, QComboBox, QListWidget,
    QGroupBox, QMessageBox, QCheckBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles

logger = logging.getLogger(__name__)


class Phase1StorageConfig(QWizardPage):
    """Phase 1: Storage and domain configuration wizard page"""
    
    # Signals
    config_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """Initialize storage configuration page"""
        super().__init__(parent)
        
        self.setTitle("Phase 1: Storage Configuration")
        self.setSubTitle("Configure storage paths, select domains to crawl, and set crawl parameters")
        
        # Configuration data
        self.storage_path = Path("./data").resolve()
        self.selected_domains: List[Dict] = []
        self.all_domains: List[Dict] = []
        self.crawl_depth = 2
        self.crawl_speed = "medium"
        
        # Setup UI
        self._init_ui()
        self._load_domains()
        
        # Register fields for validation
        self.registerField("storage_path*", self.storage_path_input)
        self.registerField("crawl_depth", self.depth_spinbox)
        
        logger.info("Phase 1 (Storage Config) initialized")
    
    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Storage Path Section
        storage_group = self._create_storage_section()
        layout.addWidget(storage_group)
        
        # Domain Selection Section
        domain_group = self._create_domain_section()
        layout.addWidget(domain_group)
        
        # Crawl Settings Section
        crawl_group = self._create_crawl_settings_section()
        layout.addWidget(crawl_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _create_storage_section(self) -> QGroupBox:
        """Create storage path configuration section"""
        group = QGroupBox("Storage Configuration")
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
        
        # Description
        desc_label = QLabel("Select the directory where crawled data will be stored:")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Path input row
        path_layout = QHBoxLayout()
        
        self.storage_path_input = QLineEdit()
        self.storage_path_input.setText(str(self.storage_path))
        self.storage_path_input.setPlaceholderText("Enter or browse for storage directory...")
        self.storage_path_input.textChanged.connect(self._validate_storage_path)
        path_layout.addWidget(self.storage_path_input, 3)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setStyleSheet(Styles.get_button_style())
        browse_btn.clicked.connect(self._browse_storage_path)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # Status label
        self.storage_status_label = QLabel("✓ Valid storage path")
        self.storage_status_label.setStyleSheet(Styles.get_status_label_style('running'))
        layout.addWidget(self.storage_status_label)
        
        group.setLayout(layout)
        return group
    
    def _create_domain_section(self) -> QGroupBox:
        """Create domain selection section"""
        group = QGroupBox("Domain Selection")
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
        
        # Description
        desc_label = QLabel("Select Swedish domains to crawl (Ctrl+Click for multiple):")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.setStyleSheet(Styles.get_button_style(size='small'))
        select_all_btn.clicked.connect(self._select_all_domains)
        btn_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setStyleSheet(Styles.get_button_style(size='small'))
        deselect_all_btn.clicked.connect(self._deselect_all_domains)
        btn_layout.addWidget(deselect_all_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Domain list
        self.domain_list = QListWidget()
        self.domain_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.domain_list.itemSelectionChanged.connect(self._on_domain_selection_changed)
        self.domain_list.setMinimumHeight(200)
        layout.addWidget(self.domain_list)
        
        # Selection count label
        self.selection_label = QLabel("0 domains selected")
        self.selection_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addWidget(self.selection_label)
        
        group.setLayout(layout)
        return group
    
    def _create_crawl_settings_section(self) -> QGroupBox:
        """Create crawl settings section"""
        group = QGroupBox("Crawl Settings")
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
        
        # Crawl depth
        depth_layout = QHBoxLayout()
        depth_label = QLabel("Crawl Depth (pages per domain):")
        depth_label.setMinimumWidth(200)
        depth_layout.addWidget(depth_label)
        
        self.depth_spinbox = QSpinBox()
        self.depth_spinbox.setRange(1, 1000)
        self.depth_spinbox.setValue(self.crawl_depth)
        self.depth_spinbox.setSuffix(" pages")
        self.depth_spinbox.valueChanged.connect(self._on_depth_changed)
        depth_layout.addWidget(self.depth_spinbox)
        
        depth_info = QLabel("(1-50=test, 50-200=moderate, 200+=comprehensive)")
        depth_info.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        depth_layout.addWidget(depth_info)
        depth_layout.addStretch()
        
        layout.addLayout(depth_layout)
        
        # Add unlimited crawl checkbox
        self.unlimited_crawl_checkbox = QCheckBox("Crawl entire domain (unlimited pages)")
        self.unlimited_crawl_checkbox.setChecked(False)
        self.unlimited_crawl_checkbox.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
        self.unlimited_crawl_checkbox.stateChanged.connect(self._on_unlimited_changed)
        layout.addWidget(self.unlimited_crawl_checkbox)
        
        # Crawl speed
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Base Crawl Speed:")
        speed_label.setMinimumWidth(200)
        speed_layout.addWidget(speed_label)
        
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["Slow (5s/page)", "Medium (2s/page)", "Fast (1s/page)", "Dynamic (auto-adjust)"])
        self.speed_combo.setCurrentText("Dynamic (auto-adjust)")
        self.speed_combo.currentTextChanged.connect(self._on_speed_changed)
        speed_layout.addWidget(self.speed_combo)
        
        speed_info = QLabel("(dynamic adjusts based on robots.txt)")
        speed_info.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        speed_layout.addWidget(speed_info)
        speed_layout.addStretch()
        
        layout.addLayout(speed_layout)
        
        # Respect robots.txt checkbox
        self.robots_checkbox = QCheckBox("Respect robots.txt rules")
        self.robots_checkbox.setChecked(True)
        self.robots_checkbox.setStyleSheet(f"color: {GUIConfig.COLORS['text_primary']};")
        layout.addWidget(self.robots_checkbox)
        
        group.setLayout(layout)
        return group
    
    def _load_domains(self):
        """Load domains from configuration file"""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "swedish_domains.json"
            
            if not config_path.exists():
                logger.error(f"Domains file not found: {config_path}")
                QMessageBox.warning(
                    self,
                    "Configuration Error",
                    f"Could not find domains configuration file:\n{config_path}"
                )
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.all_domains = data.get('domains', [])
            
            # Populate domain list
            self.domain_list.clear()
            for domain in self.all_domains:
                category_icon = {
                    'news': '📰',
                    'government': '🏛️',
                    'education': '🎓',
                    'reference': '📚'
                }.get(domain.get('category', ''), '🌐')
                
                display_text = f"{category_icon} {domain['name']} ({domain['domain']}) - Priority {domain['priority']}"
                self.domain_list.addItem(display_text)
            
            logger.info(f"Loaded {len(self.all_domains)} domains")
            
        except Exception as e:
            logger.error(f"Failed to load domains: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load domains configuration:\n{str(e)}"
            )
    
    def _browse_storage_path(self):
        """Open directory browser for storage path"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Storage Directory",
            str(self.storage_path),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.storage_path_input.setText(directory)
    
    def _validate_storage_path(self, path_text: str):
        """Validate storage path"""
        if not path_text:
            self.storage_status_label.setText("⚠ Storage path is required")
            self.storage_status_label.setStyleSheet(Styles.get_status_label_style('warning'))
            return False
        
        path = Path(path_text)
        
        try:
            # Check if path exists or can be created
            if not path.exists():
                # Test if we can create it (but don't actually create yet)
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created storage directory: {path}")
                self.storage_status_label.setText("✓ Storage path created")
                self.storage_status_label.setStyleSheet(Styles.get_status_label_style('running'))
            else:
                self.storage_status_label.setText("✓ Valid storage path")
                self.storage_status_label.setStyleSheet(Styles.get_status_label_style('running'))
            
            self.storage_path = path
            return True
            
        except Exception as e:
            self.storage_status_label.setText(f"✗ Invalid path: {str(e)}")
            self.storage_status_label.setStyleSheet(Styles.get_status_label_style('stopped'))
            return False
    
    def _select_all_domains(self):
        """Select all domains in the list"""
        self.domain_list.selectAll()
    
    def _deselect_all_domains(self):
        """Deselect all domains"""
        self.domain_list.clearSelection()
    
    def _on_domain_selection_changed(self):
        """Handle domain selection change"""
        selected_indices = [self.domain_list.row(item) for item in self.domain_list.selectedItems()]
        self.selected_domains = [self.all_domains[i] for i in selected_indices]
        
        count = len(self.selected_domains)
        self.selection_label.setText(f"{count} domain{'s' if count != 1 else ''} selected")
        
        # Update validation
        self.completeChanged.emit()
    
    def _on_depth_changed(self, value: int):
        """Handle crawl depth change"""
        self.crawl_depth = value
        logger.debug(f"Crawl depth changed to: {value}")
    
    def _on_unlimited_changed(self, state: int):
        """Handle unlimited crawl checkbox change"""
        if state == 2:  # Checked
            self.depth_spinbox.setEnabled(False)
            self.crawl_depth = -1  # -1 indicates unlimited
            logger.debug("Unlimited crawl enabled")
        else:
            self.depth_spinbox.setEnabled(True)
            self.crawl_depth = self.depth_spinbox.value()
            logger.debug(f"Crawl depth set to: {self.crawl_depth}")
    
    def _on_speed_changed(self, text: str):
        """Handle crawl speed change"""
        if "Slow" in text:
            self.crawl_speed = "slow"
        elif "Fast" in text:
            self.crawl_speed = "fast"
        elif "Dynamic" in text:
            self.crawl_speed = "dynamic"
        else:
            self.crawl_speed = "medium"
        
        logger.debug(f"Crawl speed changed to: {self.crawl_speed}")
    
    def isComplete(self) -> bool:
        """Validate page completion"""
        # Check storage path
        if not self.storage_path_input.text():
            return False
        
        # Check at least one domain selected
        if not self.selected_domains:
            return False
        
        return True
    
    def validatePage(self) -> bool:
        """Validate page before moving to next"""
        if not self.selected_domains:
            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select at least one domain to crawl."
            )
            return False
        
        # Final validation of storage path
        if not self._validate_storage_path(self.storage_path_input.text()):
            QMessageBox.critical(
                self,
                "Invalid Path",
                "The storage path is invalid or cannot be created."
            )
            return False
        
        logger.info(f"Phase 1 validated: {len(self.selected_domains)} domains, depth={self.crawl_depth}")
        return True
    
    def get_configuration(self) -> Dict:
        """Get current configuration"""
        # Map speed to delay
        speed_to_delay = {
            'slow': 5.0,
            'medium': 2.0,
            'fast': 1.0,
            'dynamic': 2.0  # Default for dynamic, will be adjusted per domain
        }
        
        # Maximum pages for unlimited crawl (safety limit)
        MAX_UNLIMITED_CRAWL_PAGES = 10000
        
        # Use safety limit for unlimited crawl
        crawl_depth = MAX_UNLIMITED_CRAWL_PAGES if self.crawl_depth == -1 else self.crawl_depth
        
        return {
            'storage_path': str(self.storage_path),
            'domains': self.selected_domains,
            'crawl_depth': crawl_depth,
            'crawl_speed': self.crawl_speed,
            'crawl_delay': speed_to_delay[self.crawl_speed],
            'respect_robots': self.robots_checkbox.isChecked(),
            'dynamic_speed': self.crawl_speed == 'dynamic',
            'force_ignore_robots_on_zero': True
        }
