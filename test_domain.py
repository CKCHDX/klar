#!/usr/bin/env python3
"""
Test the render engine with a real domain (example.com)
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from browser_window import BrowserWindow


def main():
    """Test loading a real domain"""
    app = QApplication(sys.argv)
    
    window = BrowserWindow()
    window.show()
    
    def load_domain():
        print("Loading example.com...")
        window.address_bar.setText("example.com")
        window.navigate()
        
        # Take screenshot after loading
        QTimer.singleShot(5000, take_screenshot)
    
    def take_screenshot():
        print("Taking screenshot of example.com...")
        pixmap = window.grab()
        pixmap.save("/tmp/klar_example_com.png")
        print("Screenshot saved to /tmp/klar_example_com.png")
        print(f"Current URL: {window.address_bar.text()}")
        print(f"Status: {window.status_label.text()}")
        app.quit()
    
    # Load domain after 500ms
    QTimer.singleShot(500, load_domain)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
