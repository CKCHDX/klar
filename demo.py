#!/usr/bin/env python3
"""
Load and display the demo HTML file
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from browser_window import BrowserWindow


def main():
    """Load demo.html in the browser"""
    app = QApplication(sys.argv)
    
    window = BrowserWindow()
    window.show()
    
    def load_demo():
        # Read demo.html
        demo_path = os.path.join(os.path.dirname(__file__), 'demo.html')
        with open(demo_path, 'r') as f:
            html_content = f.read()
        
        # Load into browser
        window.viewport.load_html(html_content, f"file://{demo_path}")
        window.address_bar.setText(f"file://{demo_path}")
        window.status_label.setText(f"Loaded demo.html")
        
        print("Demo HTML loaded successfully!")
    
    # Load demo after 500ms
    QTimer.singleShot(500, load_demo)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
