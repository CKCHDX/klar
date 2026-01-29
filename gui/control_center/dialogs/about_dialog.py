"""
About Dialog
Application about/help dialog with version info
"""

from typing import Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTextBrowser, QTabWidget, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from gui.kse_gui_config import GUIConfig
import logging
import platform
import sys

logger = logging.getLogger(__name__)


class AboutDialog(QDialog):
    """About/help dialog"""
    
    # Signals
    link_clicked = pyqtSignal(str)
    
    def __init__(
        self,
        app_name: str = "KSE Application",
        version: str = "1.0.0",
        description: str = "Knowledge Search Engine",
        parent=None
    ):
        """
        Initialize about dialog
        
        Args:
            app_name: Application name
            version: Version string
            description: Short description
            parent: Parent widget
        """
        super().__init__(parent)
        self.app_name = app_name
        self.version = version
        self.description = description
        
        self.setWindowTitle(f"About {app_name}")
        self.setModal(True)
        self.resize(600, 500)
        
        self._setup_ui()
        self._apply_styles()
        
        logger.debug(f"AboutDialog created for {app_name}")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        # App name
        name_label = QLabel(self.app_name)
        name_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['header'] + 4)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(name_label)
        
        # Version
        version_label = QLabel(f"Version {self.version}")
        version_font = QFont(GUIConfig.FONTS['family'], GUIConfig.FONTS['size']['medium'])
        version_label.setFont(version_font)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        header_layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel(self.description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
        
        layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # About tab
        self.tabs.addTab(self._create_about_tab(), "About")
        
        # System Info tab
        self.tabs.addTab(self._create_system_info_tab(), "System Info")
        
        # License tab
        self.tabs.addTab(self._create_license_tab(), "License")
        
        # Credits tab
        self.tabs.addTab(self._create_credits_tab(), "Credits")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _create_about_tab(self) -> QWidget:
        """Create about tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        about_text = QTextBrowser()
        about_text.setOpenExternalLinks(True)
        about_text.setHtml(f"""
        <html>
        <body style="color: {GUIConfig.COLORS['text_primary']};">
        <h2>About {self.app_name}</h2>
        <p>{self.description}</p>
        
        <h3>Features</h3>
        <ul>
            <li>Advanced knowledge search and indexing</li>
            <li>Multi-domain support</li>
            <li>Real-time monitoring and control</li>
            <li>Comprehensive analytics and reporting</li>
            <li>Modular architecture</li>
        </ul>
        
        <h3>Contact</h3>
        <p>
        Website: <a href="https://github.com/kse" style="color: {GUIConfig.COLORS['primary']};">
        github.com/kse</a><br>
        Email: support@kse.example.com
        </p>
        
        <p style="color: {GUIConfig.COLORS['text_secondary']};">
        Copyright © 2024 KSE Project. All rights reserved.
        </p>
        </body>
        </html>
        """)
        
        layout.addWidget(about_text)
        return widget
    
    def _create_system_info_tab(self) -> QWidget:
        """Create system info tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info_text = QTextBrowser()
        info_text.setHtml(f"""
        <html>
        <body style="color: {GUIConfig.COLORS['text_primary']};">
        <h3>System Information</h3>
        <table style="width: 100%;">
        <tr>
            <td><b>Python Version:</b></td>
            <td>{sys.version.split()[0]}</td>
        </tr>
        <tr>
            <td><b>Platform:</b></td>
            <td>{platform.system()} {platform.release()}</td>
        </tr>
        <tr>
            <td><b>Architecture:</b></td>
            <td>{platform.machine()}</td>
        </tr>
        <tr>
            <td><b>Processor:</b></td>
            <td>{platform.processor() or 'Unknown'}</td>
        </tr>
        <tr>
            <td><b>PyQt Version:</b></td>
            <td>6.x</td>
        </tr>
        </table>
        
        <h3>Application Paths</h3>
        <table style="width: 100%;">
        <tr>
            <td><b>Executable:</b></td>
            <td>{sys.executable}</td>
        </tr>
        <tr>
            <td><b>Working Directory:</b></td>
            <td>{sys.path[0]}</td>
        </tr>
        </table>
        </body>
        </html>
        """)
        
        layout.addWidget(info_text)
        return widget
    
    def _create_license_tab(self) -> QWidget:
        """Create license tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        license_text = QTextBrowser()
        license_text.setPlainText("""
MIT License

Copyright (c) 2024 KSE Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
        """)
        
        layout.addWidget(license_text)
        return widget
    
    def _create_credits_tab(self) -> QWidget:
        """Create credits tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        credits_text = QTextBrowser()
        credits_text.setOpenExternalLinks(True)
        credits_text.setHtml(f"""
        <html>
        <body style="color: {GUIConfig.COLORS['text_primary']};">
        <h3>Development Team</h3>
        <ul>
            <li><b>Lead Developer:</b> KSE Team</li>
            <li><b>Contributors:</b> Open Source Community</li>
        </ul>
        
        <h3>Third-Party Libraries</h3>
        <ul>
            <li><b>PyQt6:</b> GUI framework</li>
            <li><b>Python:</b> Programming language</li>
            <li><b>Various Python packages:</b> See requirements.txt</li>
        </ul>
        
        <h3>Special Thanks</h3>
        <p>
        Thanks to all contributors and users who have helped make this project possible.
        </p>
        
        <p style="color: {GUIConfig.COLORS['text_secondary']};">
        For a complete list of dependencies, please check the requirements.txt file.
        </p>
        </body>
        </html>
        """)
        
        layout.addWidget(credits_text)
        return widget
    
    def _apply_styles(self):
        """Apply styling to the dialog"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {GUIConfig.COLORS['bg_primary']};
            }}
            QLabel {{
                color: {GUIConfig.COLORS['text_primary']};
            }}
            QTextBrowser {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
            }}
        """)
    
    @staticmethod
    def show_about(
        app_name: str = "KSE Application",
        version: str = "1.0.0",
        description: str = "Knowledge Search Engine",
        parent=None
    ):
        """
        Static method to show about dialog
        
        Args:
            app_name: Application name
            version: Version string
            description: Short description
            parent: Parent widget
        """
        dialog = AboutDialog(app_name, version, description, parent)
        dialog.exec()
