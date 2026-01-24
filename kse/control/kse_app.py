"""
KSE Control Application

Main application entry point for the Klar Search Engine Control Center.
"""

import sys
import logging
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from kse.core import KSELogger
from kse.database import KSEDatabase
from .kse_main_window import KSEMainWindow

logger = KSELogger.get_logger(__name__)


class KSEControlApplication(QApplication):
    """Main application class for KSE Control Center."""
    
    def __init__(self, args: list, db_connection: Optional[KSEDatabase] = None):
        """
        Initialize application.
        
        Args:
            args: Command line arguments
            db_connection: Optional database connection
        """
        super().__init__(args)
        
        self.db = db_connection
        self.main_window = None
        
        # Set application properties
        self.setApplicationName("Klar Search Engine Control Center")
        self.setApplicationVersion("1.0.0")
        self.setStyle('Fusion')  # Modern style
        
        logger.info("KSEControlApplication initialized")
    
    def run(self) -> int:
        """
        Run the application.
        
        Returns:
            Application exit code
        """
        try:
            # Create main window
            self.main_window = KSEMainWindow(self.db)
            self.main_window.show()
            
            logger.info("Application started")
            
            # Run event loop
            return self.exec()
        
        except Exception as e:
            logger.error(f"Application error: {e}")
            QMessageBox.critical(
                None,
                "Application Error",
                f"An error occurred: {str(e)}"
            )
            return 1


def create_app(db_connection: Optional[KSEDatabase] = None) -> KSEControlApplication:
    """
    Create and configure the application.
    
    Args:
        db_connection: Optional database connection
        
    Returns:
        Application instance
    """
    app = KSEControlApplication(sys.argv, db_connection)
    return app


def main():
    """
    Main entry point.
    """
    try:
        # Initialize database
        db = KSEDatabase()
        
        # Create and run application
        app = create_app(db)
        sys.exit(app.run())
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
