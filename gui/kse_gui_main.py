"""
KSE GUI Main Entry Point
Launches the KSE GUI application with Setup Wizard or Control Center
"""

import sys
import logging
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtGui import QIcon
    from PyQt6.QtCore import Qt
except ImportError:
    print("ERROR: PyQt6 is not installed!")
    print("Install with: pip install PyQt6")
    sys.exit(1)

from gui.kse_gui_config import GUIConfig
from gui.setup_wizard.setup_wizard_main import SetupWizard
from gui.control_center.control_center_main import ControlCenter
from kse.core.kse_config import ConfigManager
from kse.core.kse_logger import setup_logging

logger = logging.getLogger(__name__)


class KSEApplication:
    """Main KSE GUI Application"""
    
    def __init__(self):
        """Initialize application"""
        self.app: Optional[QApplication] = None
        self.main_window = None
        
    def initialize(self) -> bool:
        """Initialize the application"""
        try:
            # Setup logging
            setup_logging()
            logger.info("Starting KSE GUI Application")
            
            # Create QApplication
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Klar Search Engine")
            self.app.setApplicationVersion("3.0.0")
            self.app.setOrganizationName("Oscyra")
            
            # Set application icon
            icon_path = GUIConfig.get_icon_path('app_icon')
            if icon_path.exists():
                self.app.setWindowIcon(QIcon(str(icon_path)))
            
            # Apply dark theme
            self.app.setStyleSheet(GUIConfig.get_default_stylesheet())
            
            # Enable high DPI scaling
            self.app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
            self.app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
            
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}", exc_info=True)
            return False
    
    def check_first_run(self) -> bool:
        """Check if this is the first run (needs setup)"""
        try:
            config_manager = ConfigManager()
            config = config_manager.config
            
            # Check if setup has been completed
            if hasattr(config, 'gui') and hasattr(config.gui, 'setup_completed'):
                return not config.gui.setup_completed
            
            # Check if index exists
            storage_path = Path(config.storage.base_path) / 'storage' / 'index'
            index_file = storage_path / 'inverted_index.pkl'
            
            return not index_file.exists()
            
        except Exception as e:
            logger.warning(f"Could not determine first run status: {e}")
            return True  # Default to first run
    
    def show_setup_wizard(self):
        """Show the setup wizard"""
        try:
            logger.info("Launching Setup Wizard")
            self.main_window = SetupWizard()
            self.main_window.setup_completed.connect(self.on_setup_completed)
            self.main_window.show()
        except Exception as e:
            logger.error(f"Failed to show setup wizard: {e}", exc_info=True)
            self.show_error("Setup Wizard Error", 
                          f"Failed to launch setup wizard:\n{str(e)}")
    
    def show_control_center(self):
        """Show the control center"""
        try:
            logger.info("Launching Control Center")
            self.main_window = ControlCenter()
            self.main_window.show()
        except Exception as e:
            logger.error(f"Failed to show control center: {e}", exc_info=True)
            self.show_error("Control Center Error",
                          f"Failed to launch control center:\n{str(e)}")
    
    def on_setup_completed(self):
        """Handle setup completion"""
        logger.info("Setup completed, launching Control Center")
        
        # Close setup wizard
        if self.main_window:
            self.main_window.close()
        
        # Show control center
        self.show_control_center()
    
    def show_error(self, title: str, message: str):
        """Show error dialog"""
        QMessageBox.critical(None, title, message)
    
    def run(self) -> int:
        """Run the application"""
        try:
            # Initialize application
            if not self.initialize():
                self.show_error("Initialization Error",
                              "Failed to initialize the application.")
                return 1
            
            # Check if this is first run
            is_first_run = self.check_first_run()
            
            if is_first_run:
                logger.info("First run detected, showing Setup Wizard")
                self.show_setup_wizard()
            else:
                logger.info("System already configured, showing Control Center")
                self.show_control_center()
            
            # Start event loop
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            self.show_error("Application Error",
                          f"An unexpected error occurred:\n{str(e)}")
            return 1


def main():
    """Main entry point"""
    app = KSEApplication()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
