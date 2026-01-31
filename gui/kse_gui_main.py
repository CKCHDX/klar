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

try:
    from gui.control_center.control_center_main import ControlCenterMain as ControlCenter
    CONTROL_CENTER_AVAILABLE = True
except ImportError:
    CONTROL_CENTER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Control Center module not available")

from kse.core.kse_config import ConfigManager
from kse.core.kse_logger import setup_logging
from PyQt6.QtCore import QThread

logger = logging.getLogger(__name__)


class FlaskServerThread(QThread):
    """Background thread to run Flask server"""
    
    def __init__(self):
        super().__init__()
        self.daemon = True  # Make it a daemon thread
        
    def run(self):
        """Run Flask server in background"""
        try:
            logger.info("Starting Flask server in background...")
            from kse.server.kse_server import create_app
            from kse.core.kse_config import ConfigManager
            
            config_manager = ConfigManager()
            host = config_manager.get("server.host", "0.0.0.0")
            port = config_manager.get("server.port", 5000)
            
            app = create_app()
            logger.info(f"Flask server initialized, running on {host}:{port}")
            
            app.run(
                host=host,
                port=port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            logger.error(f"Flask server error: {e}", exc_info=True)


class KSEApplication:
    """Main KSE GUI Application"""
    
    def __init__(self):
        """Initialize application"""
        self.app: Optional[QApplication] = None
        self.main_window = None
        self.flask_server_thread: Optional[FlaskServerThread] = None
        
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
            
            # Enable high DPI scaling (must be set before QApplication creation)
            # Note: These should be set via environment variables or before QApplication
            # Keeping here for documentation but moving to environment setup recommended
            # self.app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
            # self.app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
            
            # Start Flask server in background
            logger.info("Starting Flask server background thread...")
            self.flask_server_thread = FlaskServerThread()
            self.flask_server_thread.start()
            
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}", exc_info=True)
            return False
    
    def check_first_run(self) -> bool:
        """Check if this is the first run (needs setup)"""
        try:
            from kse.core.kse_state_manager import StateManager
            from pathlib import Path
            
            # Try to find data directory
            config_manager = ConfigManager()
            config = config_manager.config
            
            if hasattr(config, 'data_dir'):
                data_dir = Path(config.data_dir)
            else:
                data_dir = Path.cwd() / 'data'
            
            # Check if critical storage folders are missing
            storage_dir = data_dir / 'storage'
            state_dir = data_dir / 'state'
            
            if not storage_dir.exists() or not state_dir.exists():
                logger.info("Critical storage or state directories missing - resetting setup")
                # Reset the setup_completed flag in config
                config_manager.set("gui.setup_completed", False)
                config_manager.save_config()
                # Reset StateManager
                state_manager = StateManager(state_dir)
                state_manager.reset_setup()
                logger.info("Setup will re-run on next startup")
                return True
            
            # First check StateManager (server-side tracking)
            try:
                state_manager = StateManager(state_dir)
                if not state_manager.is_first_run():
                    logger.info("Setup already completed (StateManager)")
                    return False
            except Exception as e:
                logger.debug(f"StateManager check failed: {e}")
            
            # Check config file
            if hasattr(config, 'gui') and hasattr(config.gui, 'setup_completed'):
                is_completed = config.gui.setup_completed
                if is_completed:
                    logger.info("Setup already completed (config)")
                    return False
            
            # Check if index exists
            if hasattr(config, 'base_dir'):
                base_dir = Path(config.base_dir)
            elif hasattr(config, 'storage_dir'):
                base_dir = Path(config.storage_dir).parent
            else:
                base_dir = Path.cwd() / 'data'
            
            storage_path = base_dir / 'storage' / 'index'
            index_file = storage_path / 'inverted_index.pkl'
            
            if index_file.exists():
                logger.info("Index file exists, assuming setup complete")
                return False
            
            logger.info("First run detected - will show setup wizard")
            return True
            
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
            if not CONTROL_CENTER_AVAILABLE:
                logger.warning("Control Center not available, showing message")
                QMessageBox.information(
                    None,
                    "Setup Complete",
                    "Setup has been completed successfully!\n\n"
                    "The Control Center module is not yet available.\n"
                    "You can start the KSE server manually."
                )
                return
            
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
