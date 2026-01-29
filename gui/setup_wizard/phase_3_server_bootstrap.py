"""
Phase 3: Server Bootstrap
Flask server startup, health checks, and API verification
"""

import logging
import requests
import time
from typing import Optional, Dict
from pathlib import Path

from PyQt6.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QMessageBox, QFrame, QTextBrowser
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles

logger = logging.getLogger(__name__)


class ServerThread(QThread):
    """Worker thread for Flask server management"""
    
    # Signals
    server_started = pyqtSignal(str)  # server_url
    server_stopped = pyqtSignal()
    status_changed = pyqtSignal(str)  # status message
    error_occurred = pyqtSignal(str)  # error message
    health_check_result = pyqtSignal(bool, dict)  # success, data
    
    def __init__(self, host: str = "localhost", port: int = 5000):
        """Initialize server thread"""
        super().__init__()
        self.host = host
        self.port = port
        self.server_url = f"http://{host}:{port}"
        self.server_process: Optional[Process] = None
        self.is_running = False
    
    def run(self):
        """Start Flask server in background"""
        try:
            self.status_changed.emit("Starting Flask server...")
            
            # Import server module
            from kse.server.kse_server import create_app
            
            # Create and configure app
            app = create_app()
            
            self.status_changed.emit(f"Server initializing on {self.server_url}")
            
            # Start server in a way that doesn't block
            self.is_running = True
            self.server_started.emit(self.server_url)
            
            # Run Flask server (blocking)
            app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
            
        except Exception as e:
            error_msg = f"Failed to start server: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
        
        finally:
            self.is_running = False
            self.server_stopped.emit()
    
    def stop(self):
        """Stop the server (note: Flask doesn't support graceful shutdown easily)"""
        self.is_running = False
        # Note: terminate() is used as Flask's app.run() doesn't support graceful shutdown
        # In production, consider using werkzeug.serving.make_server() with shutdown capability
        logger.warning("Forcing server thread termination - Flask doesn't support graceful shutdown")
        self.terminate()
        self.wait(2000)  # Wait max 2 seconds


class Phase3ServerBootstrap(QWizardPage):
    """Phase 3: Server bootstrap and verification wizard page"""
    
    # Signals
    server_ready = pyqtSignal(str)  # server_url
    
    def __init__(self, parent=None):
        """Initialize server bootstrap page"""
        super().__init__(parent)
        
        self.setTitle("Phase 3: Server Bootstrap")
        self.setSubTitle("Start the KSE server and verify it's working correctly")
        
        # State
        self.server_thread: Optional[ServerThread] = None
        self.server_url = "http://localhost:5000"
        self.is_server_running = False
        self.health_check_passed = False
        
        # Setup UI
        self._init_ui()
        
        # Timer for periodic health checks
        self.health_check_timer = QTimer()
        self.health_check_timer.timeout.connect(self._periodic_health_check)
        
        logger.info("Phase 3 (Server Bootstrap) initialized")
    
    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Control section
        control_group = self._create_control_section()
        layout.addWidget(control_group)
        
        # Server status section
        status_group = self._create_status_section()
        layout.addWidget(status_group)
        
        # API testing section
        api_group = self._create_api_section()
        layout.addWidget(api_group)
        
        # Information section
        info_group = self._create_info_section()
        layout.addWidget(info_group, 1)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _create_control_section(self) -> QGroupBox:
        """Create server control section"""
        group = QGroupBox("Server Control")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {GUIConfig.get_font_size('medium')}pt;
                font-weight: bold;
                color: {GUIConfig.COLORS['primary']};
                border: 2px solid {GUIConfig.COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Description
        desc_label = QLabel(
            "Start the KSE Flask server to enable search API and web interface."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.start_server_btn = QPushButton("🚀 Start Server")
        self.start_server_btn.setStyleSheet(Styles.get_success_button_style())
        self.start_server_btn.clicked.connect(self._start_server)
        btn_layout.addWidget(self.start_server_btn)
        
        self.stop_server_btn = QPushButton("⏹ Stop Server")
        self.stop_server_btn.setStyleSheet(Styles.get_danger_button_style())
        self.stop_server_btn.clicked.connect(self._stop_server)
        self.stop_server_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_server_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_status_section(self) -> QGroupBox:
        """Create server status section"""
        group = QGroupBox("Server Status")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {GUIConfig.get_font_size('medium')}pt;
                font-weight: bold;
                color: {GUIConfig.COLORS['primary']};
                border: 2px solid {GUIConfig.COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Status indicator
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        
        self.status_indicator = QLabel("⚫ Stopped")
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_secondary']};
                font-size: {GUIConfig.get_font_size('medium')}pt;
                font-weight: bold;
            }}
        """)
        status_layout.addWidget(self.status_indicator)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Server URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        
        self.url_label = QLabel(self.server_url)
        self.url_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['primary']};
                font-family: 'Courier New', monospace;
                font-size: {GUIConfig.get_font_size('normal')}pt;
            }}
        """)
        self.url_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        url_layout.addWidget(self.url_label)
        url_layout.addStretch()
        layout.addLayout(url_layout)
        
        # Health status
        health_layout = QHBoxLayout()
        health_layout.addWidget(QLabel("Health:"))
        
        self.health_label = QLabel("Not checked")
        self.health_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        health_layout.addWidget(self.health_label)
        health_layout.addStretch()
        layout.addLayout(health_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_api_section(self) -> QGroupBox:
        """Create API testing section"""
        group = QGroupBox("API Testing")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {GUIConfig.get_font_size('medium')}pt;
                font-weight: bold;
                color: {GUIConfig.COLORS['primary']};
                border: 2px solid {GUIConfig.COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        desc_label = QLabel("Test API endpoints to ensure the server is responding correctly.")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Test buttons
        btn_layout = QHBoxLayout()
        
        self.test_health_btn = QPushButton("Test Health Endpoint")
        self.test_health_btn.setStyleSheet(Styles.get_button_style())
        self.test_health_btn.clicked.connect(self._test_health)
        self.test_health_btn.setEnabled(False)
        btn_layout.addWidget(self.test_health_btn)
        
        self.test_search_btn = QPushButton("Test Search API")
        self.test_search_btn.setStyleSheet(Styles.get_button_style())
        self.test_search_btn.clicked.connect(self._test_search)
        self.test_search_btn.setEnabled(False)
        btn_layout.addWidget(self.test_search_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Test result display
        self.test_result_label = QLabel("")
        self.test_result_label.setWordWrap(True)
        self.test_result_label.setStyleSheet(f"""
            QLabel {{
                padding: 8px;
                border: 1px solid {GUIConfig.COLORS['border']};
                border-radius: 4px;
                background-color: {GUIConfig.COLORS['bg_secondary']};
            }}
        """)
        layout.addWidget(self.test_result_label)
        
        group.setLayout(layout)
        return group
    
    def _create_info_section(self) -> QGroupBox:
        """Create information section"""
        group = QGroupBox("Next Steps")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {GUIConfig.get_font_size('medium')}pt;
                font-weight: bold;
                color: {GUIConfig.COLORS['primary']};
                border: 2px solid {GUIConfig.COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        info_text = QTextBrowser()
        info_text.setOpenExternalLinks(True)
        info_text.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {GUIConfig.COLORS['bg_secondary']};
                color: {GUIConfig.COLORS['text_primary']};
                border: none;
                padding: 10px;
            }}
        """)
        info_text.setHtml(f"""
            <div style="color: {GUIConfig.COLORS['text_primary']};">
                <h3 style="color: {GUIConfig.COLORS['primary']};">🎉 Setup Complete!</h3>
                <p>Once the server is running and tested, you can:</p>
                <ul>
                    <li><b>Access the web interface:</b> Open <a href="{self.server_url}" style="color: {GUIConfig.COLORS['info']};">{self.server_url}</a> in your browser</li>
                    <li><b>Use the Search API:</b> Send queries to <code>{self.server_url}/api/search?q=your+query</code></li>
                    <li><b>Check server health:</b> Visit <code>{self.server_url}/api/health</code></li>
                    <li><b>View statistics:</b> Get stats from <code>{self.server_url}/api/stats</code></li>
                </ul>
                <p style="margin-top: 15px;">
                    Click <b>Finish</b> to complete the setup and launch the Control Center.
                </p>
            </div>
        """)
        layout.addWidget(info_text)
        
        group.setLayout(layout)
        return group
    
    def _start_server(self):
        """Start the Flask server"""
        try:
            self.start_server_btn.setEnabled(False)
            
            # Create and start server thread
            self.server_thread = ServerThread(host="localhost", port=5000)
            self.server_thread.server_started.connect(self._on_server_started)
            self.server_thread.server_stopped.connect(self._on_server_stopped)
            self.server_thread.status_changed.connect(self._on_status_changed)
            self.server_thread.error_occurred.connect(self._on_error)
            
            self.server_thread.start()
            
            logger.info("Server start initiated")
            
        except Exception as e:
            error_msg = f"Failed to start server: {str(e)}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(self, "Server Error", error_msg)
            self.start_server_btn.setEnabled(True)
    
    def _stop_server(self):
        """Stop the Flask server"""
        if not self.server_thread:
            return
        
        reply = QMessageBox.question(
            self,
            "Stop Server",
            "Are you sure you want to stop the server?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.server_thread.stop()
            self.health_check_timer.stop()
            logger.info("Server stop initiated")
    
    def _on_server_started(self, server_url: str):
        """Handle server started event"""
        self.is_server_running = True
        self.server_url = server_url
        
        # Update UI
        self.status_indicator.setText("🟢 Running")
        self.status_indicator.setStyleSheet(Styles.get_status_label_style('running'))
        self.url_label.setText(server_url)
        
        self.start_server_btn.setEnabled(False)
        self.stop_server_btn.setEnabled(True)
        self.test_health_btn.setEnabled(True)
        self.test_search_btn.setEnabled(True)
        
        # Start periodic health checks
        self.health_check_timer.start(10000)  # Check every 10 seconds
        
        # Perform initial health check after a delay
        QTimer.singleShot(3000, self._test_health)  # Wait 3 seconds for server to fully initialize
        
        self.server_ready.emit(server_url)
        logger.info(f"Server started: {server_url}")
        
        QMessageBox.information(
            self,
            "Server Started",
            f"KSE server is now running at:\n{server_url}\n\nPerforming health check..."
        )
    
    def _on_server_stopped(self):
        """Handle server stopped event"""
        self.is_server_running = False
        self.health_check_passed = False
        
        # Update UI
        self.status_indicator.setText("⚫ Stopped")
        self.status_indicator.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        self.health_label.setText("Not checked")
        
        self.start_server_btn.setEnabled(True)
        self.stop_server_btn.setEnabled(False)
        self.test_health_btn.setEnabled(False)
        self.test_search_btn.setEnabled(False)
        
        self.health_check_timer.stop()
        self.completeChanged.emit()
        
        logger.info("Server stopped")
    
    def _on_status_changed(self, status: str):
        """Handle status change"""
        logger.info(f"Server status: {status}")
    
    def _on_error(self, error_msg: str):
        """Handle server error"""
        self.is_server_running = False
        self.start_server_btn.setEnabled(True)
        
        QMessageBox.critical(
            self,
            "Server Error",
            f"An error occurred:\n\n{error_msg}\n\nCheck the logs for more details."
        )
    
    def _test_health(self):
        """Test server health endpoint"""
        if not self.is_server_running:
            QMessageBox.warning(self, "Server Not Running", "Please start the server first.")
            return
        
        try:
            # Disable button during test
            self.test_health_btn.setEnabled(False)
            
            # Make health check request
            response = requests.get(
                f"{self.server_url}/api/health",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Update UI
                self.health_label.setText("✓ Healthy")
                self.health_label.setStyleSheet(Styles.get_status_label_style('running'))
                self.health_check_passed = True
                
                # Show result
                version = data.get('version', 'unknown')
                stats = data.get('index_stats', {})
                result_text = (
                    f"✓ Health check passed!\n\n"
                    f"Version: {version}\n"
                    f"Status: {data.get('status', 'unknown')}\n"
                    f"Indexed documents: {stats.get('total_documents', 0)}\n"
                    f"Indexed terms: {stats.get('total_terms', 0)}"
                )
                
                self.test_result_label.setText(result_text)
                self.test_result_label.setStyleSheet(f"""
                    QLabel {{
                        padding: 8px;
                        border: 1px solid {GUIConfig.COLORS['success']};
                        border-radius: 4px;
                        background-color: {GUIConfig.COLORS['bg_secondary']};
                        color: {GUIConfig.COLORS['success']};
                    }}
                """)
                
                self.completeChanged.emit()
                logger.info("Health check passed")
                
            else:
                raise Exception(f"Unexpected status code: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.health_label.setText("✗ Connection failed")
            self.health_label.setStyleSheet(Styles.get_status_label_style('stopped'))
            self.test_result_label.setText("✗ Connection Error: Server may still be starting up. Wait a few seconds and try again.")
            self.test_result_label.setStyleSheet(f"""
                QLabel {{
                    padding: 8px;
                    border: 1px solid {GUIConfig.COLORS['warning']};
                    border-radius: 4px;
                    background-color: {GUIConfig.COLORS['bg_secondary']};
                    color: {GUIConfig.COLORS['warning']};
                }}
            """)
            
        except Exception as e:
            self.health_label.setText("✗ Failed")
            self.health_label.setStyleSheet(Styles.get_status_label_style('stopped'))
            self.test_result_label.setText(f"✗ Health check failed: {str(e)}")
            self.test_result_label.setStyleSheet(f"""
                QLabel {{
                    padding: 8px;
                    border: 1px solid {GUIConfig.COLORS['error']};
                    border-radius: 4px;
                    background-color: {GUIConfig.COLORS['bg_secondary']};
                    color: {GUIConfig.COLORS['error']};
                }}
            """)
            logger.error(f"Health check failed: {e}")
        
        finally:
            self.test_health_btn.setEnabled(True)
    
    def _test_search(self):
        """Test search API endpoint"""
        if not self.is_server_running:
            QMessageBox.warning(self, "Server Not Running", "Please start the server first.")
            return
        
        try:
            self.test_search_btn.setEnabled(False)
            
            # Make search request
            response = requests.get(
                f"{self.server_url}/api/search",
                params={'q': 'test', 'max': 5},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                result_count = len(data.get('results', []))
                query_time = data.get('query_time_ms', 0)
                
                result_text = (
                    f"✓ Search API working!\n\n"
                    f"Test query: 'test'\n"
                    f"Results found: {result_count}\n"
                    f"Query time: {query_time:.2f}ms"
                )
                
                self.test_result_label.setText(result_text)
                self.test_result_label.setStyleSheet(f"""
                    QLabel {{
                        padding: 8px;
                        border: 1px solid {GUIConfig.COLORS['success']};
                        border-radius: 4px;
                        background-color: {GUIConfig.COLORS['bg_secondary']};
                        color: {GUIConfig.COLORS['success']};
                    }}
                """)
                
                logger.info("Search API test passed")
                
            else:
                raise Exception(f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            self.test_result_label.setText(f"✗ Search API test failed: {str(e)}")
            self.test_result_label.setStyleSheet(f"""
                QLabel {{
                    padding: 8px;
                    border: 1px solid {GUIConfig.COLORS['error']};
                    border-radius: 4px;
                    background-color: {GUIConfig.COLORS['bg_secondary']};
                    color: {GUIConfig.COLORS['error']};
                }}
            """)
            logger.error(f"Search API test failed: {e}")
        
        finally:
            self.test_search_btn.setEnabled(True)
    
    def _periodic_health_check(self):
        """Perform periodic health check silently"""
        if not self.is_server_running:
            return
        
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=2)
            if response.status_code == 200:
                if not self.health_check_passed:
                    self.health_label.setText("✓ Healthy")
                    self.health_label.setStyleSheet(Styles.get_status_label_style('running'))
                    self.health_check_passed = True
                    self.completeChanged.emit()
            else:
                self.health_label.setText("⚠ Unhealthy")
                self.health_label.setStyleSheet(Styles.get_status_label_style('warning'))
                self.health_check_passed = False
        except requests.RequestException:
            # Silent failure for periodic checks (connection errors expected during startup)
            pass
        except Exception as e:
            logger.warning(f"Periodic health check error: {e}")
    
    def isComplete(self) -> bool:
        """Check if page is complete"""
        return self.is_server_running and self.health_check_passed
    
    def cleanupPage(self):
        """Cleanup when leaving page"""
        # Don't stop the server when leaving the page - it should keep running
        if self.health_check_timer.isActive():
            self.health_check_timer.stop()
