"""
Setup Wizard Main Window
Interactive setup wizard for KSE configuration (Phases 1-3)
"""

import logging
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QLabel, QPushButton,
    QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
from gui.setup_wizard.phase_1_storage_config import Phase1StorageConfig
from gui.setup_wizard.phase_2_crawl_control import Phase2CrawlControl
from gui.setup_wizard.phase_3_server_bootstrap import Phase3ServerBootstrap
from kse.core.kse_config import ConfigManager

logger = logging.getLogger(__name__)


class SetupWizard(QWizard):
    """Setup Wizard for KSE initial configuration"""
    
    # Signal emitted when setup is completed
    setup_completed = pyqtSignal()
    
    # Page IDs
    PAGE_STORAGE = 0
    PAGE_CRAWL = 1
    PAGE_SERVER = 2
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize Setup Wizard"""
        super().__init__(parent)
        
        self.config_manager = ConfigManager()
        
        # Setup window
        self.setWindowTitle("KSE Setup Wizard")
        self.setWindowIcon(QIcon(str(GUIConfig.get_icon_path('app_icon'))))
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage)
        self.setOption(QWizard.WizardOption.HaveHelpButton, False)
        
        # Set window size
        self.setFixedSize(900, 700)
        
        # Apply stylesheet
        self.setStyleSheet(GUIConfig.get_default_stylesheet())
        
        # Add pages
        self._add_pages()
        
        # Connect signals
        self.currentIdChanged.connect(self._on_page_changed)
        self.finished.connect(self._on_finished)
        
        logger.info("Setup Wizard initialized")
    
    def _add_pages(self):
        """Add wizard pages"""
        # Page 1: Storage Configuration
        self.page_storage = Phase1StorageConfig()
        self.setPage(self.PAGE_STORAGE, self.page_storage)
        
        # Page 2: Crawl Control
        self.page_crawl = Phase2CrawlControl()
        self.setPage(self.PAGE_CRAWL, self.page_crawl)
        
        # Page 3: Server Bootstrap
        self.page_server = Phase3ServerBootstrap()
        self.setPage(self.PAGE_SERVER, self.page_server)
        
        # Set start page
        self.setStartId(self.PAGE_STORAGE)
    
    def _on_page_changed(self, page_id: int):
        """Handle page change"""
        logger.info(f"Wizard page changed to: {page_id}")
        
        # Customize buttons based on page
        if page_id == self.PAGE_STORAGE:
            self.setButtonText(QWizard.WizardButton.NextButton, "Next →")
        elif page_id == self.PAGE_CRAWL:
            self.setButtonText(QWizard.WizardButton.NextButton, "Next →")
        elif page_id == self.PAGE_SERVER:
            self.setButtonText(QWizard.WizardButton.FinishButton, "Launch Control Center")
    
    def _on_finished(self, result: int):
        """Handle wizard completion"""
        if result == QWizard.DialogCode.Accepted:
            logger.info("Setup wizard completed successfully")
            
            # Save completion status
            try:
                self._save_completion_status()
                self.setup_completed.emit()
            except Exception as e:
                logger.error(f"Failed to save completion status: {e}")
                QMessageBox.warning(
                    self,
                    "Setup Warning",
                    f"Setup completed but failed to save status:\n{str(e)}"
                )
        else:
            logger.info("Setup wizard cancelled")
    
    def _save_completion_status(self):
        """Save setup completion status"""
        # Update configuration to mark setup as completed
        config = self.config_manager.config
        
        # Add GUI section if it doesn't exist
        if not hasattr(config, 'gui'):
            from types import SimpleNamespace
            config.gui = SimpleNamespace()
        
        config.gui.setup_completed = True
        
        # Save configuration
        self.config_manager.save_config()
        logger.info("Setup completion status saved")


class WelcomePage(QWizardPage):
    """Welcome page for setup wizard"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize welcome page"""
        super().__init__(parent)
        
        self.setTitle("Welcome to Klar Search Engine")
        self.setSubTitle("This wizard will help you set up KSE in 3 easy steps")
        
        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Welcome message
        welcome_text = QLabel(
            "<h2>🔍 Welcome to KSE Setup!</h2>"
            "<p>This wizard will guide you through:</p>"
            "<ul>"
            "<li><b>Phase 1:</b> Storage configuration and domain selection</li>"
            "<li><b>Phase 2:</b> Web crawling and indexing</li>"
            "<li><b>Phase 3:</b> Server bootstrap and verification</li>"
            "</ul>"
            "<p>The process should take about 10-15 minutes depending on the number of domains.</p>"
            "<p><b>Note:</b> You can stop and resume the setup at any time.</p>"
        )
        welcome_text.setWordWrap(True)
        welcome_text.setStyleSheet("QLabel { padding: 20px; }")
        
        layout.addWidget(welcome_text)
        layout.addStretch()
        
        self.setLayout(layout)
