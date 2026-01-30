#!/usr/bin/env python3
"""
Klar Browser - Main Entry Point
A custom web browser with a built-from-scratch render engine
"""
import sys
from PyQt6.QtWidgets import QApplication
from browser_window import BrowserWindow


def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Klar Browser")
    app.setOrganizationName("Klar")
    
    # Create and show main window
    window = BrowserWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
