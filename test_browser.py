#!/usr/bin/env python3
"""
Test script for the Klar Browser render engine
"""
import sys
from PyQt6.QtWidgets import QApplication
from browser_window import BrowserWindow
from PyQt6.QtCore import QTimer


def test_browser():
    """Test the browser by loading a sample page"""
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    
    # Automatically load example.com after 1 second
    def load_example():
        print("Loading example.com...")
        window.address_bar.setText("example.com")
        window.navigate()
        
        # Take a screenshot after 3 seconds
        QTimer.singleShot(3000, lambda: take_screenshot(window))
    
    def take_screenshot(window):
        print("Taking screenshot...")
        pixmap = window.grab()
        pixmap.save("/tmp/klar_browser_screenshot.png")
        print("Screenshot saved to /tmp/klar_browser_screenshot.png")
        
        # Close after taking screenshot
        QTimer.singleShot(1000, app.quit)
    
    QTimer.singleShot(1000, load_example)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_browser()
