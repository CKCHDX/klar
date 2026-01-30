#!/usr/bin/env python3
"""
Simple test script to verify render engine functionality
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from browser_window import BrowserWindow

# Test timing constants
INITIAL_DELAY_MS = 500
SCREENSHOT_DELAY_MS = 500


def main():
    """Test the render engine with a simple HTML document"""
    app = QApplication(sys.argv)
    
    window = BrowserWindow()
    window.show()
    
    def take_screenshot():
        print("Taking screenshot of default page...")
        pixmap = window.grab()
        pixmap.save("/tmp/klar_default_page.png")
        print("Screenshot saved to /tmp/klar_default_page.png")
        
        # Load a simple test HTML
        test_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Klar Render Engine Test</h1>
            <p>This is a test of the custom render engine.</p>
            <p><strong>Bold text</strong> and <em>italic text</em></p>
            <h2>Features</h2>
            <ul>
                <li>HTML parsing</li>
                <li>CSS styling</li>
                <li>Text rendering</li>
            </ul>
        </body>
        </html>
        """
        window.viewport.load_html(test_html, "test:page")
        
        # Take another screenshot after loading test HTML
        QTimer.singleShot(SCREENSHOT_DELAY_MS, take_test_screenshot)
    
    def take_test_screenshot():
        print("Taking screenshot of test page...")
        pixmap = window.grab()
        pixmap.save("/tmp/klar_test_page.png")
        print("Screenshot saved to /tmp/klar_test_page.png")
        print("Test complete!")
        app.quit()
    
    # Take screenshot after 500ms
    QTimer.singleShot(INITIAL_DELAY_MS, take_screenshot)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
