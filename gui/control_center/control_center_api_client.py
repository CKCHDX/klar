"""
Control Center API Client
Handles communication with KSE Flask backend API
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from urllib.parse import urljoin
import json

from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtNetwork import (
    QNetworkAccessManager, QNetworkRequest, QNetworkReply
)
from PyQt6.QtCore import QUrl, QByteArray

from gui.control_center.control_center_config import ControlCenterConfig

logger = logging.getLogger(__name__)


class APIRequest(QObject):
    """API request worker for async operations"""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, url: str, method: str = 'GET', data: Optional[Dict] = None):
        super().__init__()
        self.url = url
        self.method = method
        self.data = data
        self.manager = QNetworkAccessManager()
        self.reply: Optional[QNetworkReply] = None
    
    def execute(self):
        """Execute the API request"""
        try:
            request = QNetworkRequest(QUrl(self.url))
            request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
            
            if self.method == 'GET':
                self.reply = self.manager.get(request)
            elif self.method == 'POST':
                data_bytes = QByteArray()
                if self.data:
                    data_bytes = QByteArray(json.dumps(self.data).encode())
                self.reply = self.manager.post(request, data_bytes)
            elif self.method == 'PUT':
                data_bytes = QByteArray()
                if self.data:
                    data_bytes = QByteArray(json.dumps(self.data).encode())
                self.reply = self.manager.put(request, data_bytes)
            elif self.method == 'DELETE':
                self.reply = self.manager.deleteResource(request)
            
            self.reply.finished.connect(self._on_finished)
            
        except Exception as e:
            logger.error(f"Error executing request: {e}")
            self.error.emit(str(e))
    
    def _on_finished(self):
        """Handle request completion"""
        try:
            if self.reply.error() == QNetworkReply.NetworkError.NoError:
                data = bytes(self.reply.readAll()).decode('utf-8')
                result = json.loads(data) if data else {}
                self.finished.emit(result)
            else:
                error_msg = self.reply.errorString()
                logger.error(f"Network error: {error_msg}")
                self.error.emit(error_msg)
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            self.error.emit(str(e))
        finally:
            if self.reply:
                self.reply.deleteLater()


class ControlCenterAPIClient(QObject):
    """API client for KSE Flask backend"""
    
    # Signals
    connection_status_changed = pyqtSignal(str)  # 'connected', 'disconnected', 'error'
    health_check_completed = pyqtSignal(dict)
    stats_received = pyqtSignal(dict)
    search_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Load base URL from config dynamically at initialization
        self.base_url = self._load_base_url()
        self.timeout = ControlCenterConfig.API_TIMEOUT
        self.retry_count = ControlCenterConfig.API_RETRY_COUNT
        self.retry_delay = ControlCenterConfig.API_RETRY_DELAY
        
        self._connection_status = 'disconnected'
        self._retry_attempts = {}
        
        # Network manager
        self.network_manager = QNetworkAccessManager()
        
        # Health check timer
        self.health_timer = QTimer()
        self.health_timer.setInterval(10000)  # 10 seconds
        self.health_timer.timeout.connect(self.check_health)
        
        logger.info(f"API Client initialized with base URL: {self.base_url}")
    
    def _load_base_url(self) -> str:
        """Load base URL from KSE config or environment variable"""
        import os
        
        # First check environment variable
        env_url = os.getenv("KSE_SERVER_URL")
        if env_url:
            logger.info(f"Using base URL from environment: {env_url}")
            return env_url
        
        # Try to load from KSE config
        try:
            from kse.core.kse_config import ConfigManager
            config_manager = ConfigManager()
            
            # Debug: Log what we're getting from config
            public_url = config_manager.get("server.public_url")
            host = config_manager.get("server.host")
            port = config_manager.get("server.port")
            logger.info(f"Config values - public_url: {public_url}, host: {host}, port: {port}")
            
            # Use public_url if it exists and is not None/empty
            if public_url and public_url.strip():
                logger.info(f"Using base URL from config public_url: {public_url}")
                return public_url.strip()
            
            # Fallback to host:port
            if not host:
                host = "localhost"
            if not port:
                port = 5000
            # Convert 0.0.0.0 to localhost for local GUI connections
            if host == "0.0.0.0":
                host = "localhost"
            url = f"http://{host}:{port}"
            logger.info(f"Using base URL from config host:port: {url}")
            return url
        except Exception as e:
            logger.warning(f"Could not load config, using localhost: {e}")
            return "http://localhost:5000"
    
    @property
    def connection_status(self) -> str:
        """Get current connection status"""
        return self._connection_status
    
    def _set_connection_status(self, status: str):
        """Set connection status and emit signal"""
        if self._connection_status != status:
            self._connection_status = status
            self.connection_status_changed.emit(status)
            logger.info(f"Connection status changed to: {status}")
    
    def start_health_monitoring(self):
        """Start periodic health checks"""
        self.health_timer.start()
        self.check_health()  # Initial check
        logger.info("Health monitoring started")
    
    def stop_health_monitoring(self):
        """Stop periodic health checks"""
        self.health_timer.stop()
        logger.info("Health monitoring stopped")
    
    def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict] = None,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None
    ):
        """Make API request with retry logic"""
        url = urljoin(self.base_url, endpoint)
        
        # Create request worker
        worker = APIRequest(url, method, data)
        thread = QThread()
        worker.moveToThread(thread)
        
        # Connect signals
        worker.finished.connect(lambda result: self._on_request_success(
            endpoint, result, callback
        ))
        worker.error.connect(lambda error: self._on_request_error(
            endpoint, method, data, callback, error_callback, error
        ))
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.started.connect(worker.execute)
        
        # Start thread
        thread.start()
        
        # Store thread reference to prevent garbage collection
        if not hasattr(self, '_threads'):
            self._threads = []
        self._threads.append(thread)
        thread.finished.connect(lambda: self._cleanup_thread(thread))
    
    def _cleanup_thread(self, thread: QThread):
        """Safely remove thread from list"""
        try:
            if hasattr(self, '_threads') and thread in self._threads:
                self._threads.remove(thread)
        except (ValueError, RuntimeError):
            pass  # Thread already removed or destroyed
    
    def _on_request_success(self, endpoint: str, result: Dict, callback: Optional[Callable]):
        """Handle successful request"""
        self._retry_attempts[endpoint] = 0
        self._set_connection_status('connected')
        
        if callback:
            try:
                callback(result)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
    
    def _on_request_error(
        self,
        endpoint: str,
        method: str,
        data: Optional[Dict],
        callback: Optional[Callable],
        error_callback: Optional[Callable],
        error: str
    ):
        """Handle request error with retry logic"""
        attempts = self._retry_attempts.get(endpoint, 0)
        
        if attempts < self.retry_count:
            # Retry with exponential backoff
            self._retry_attempts[endpoint] = attempts + 1
            delay = self.retry_delay * (2 ** attempts)
            logger.warning(f"Request failed, retrying in {delay}s (attempt {attempts + 1}/{self.retry_count})")
            QTimer.singleShot(
                int(delay * 1000),
                lambda: self._make_request(endpoint, method, data, callback, error_callback)
            )
        else:
            # Max retries reached
            self._retry_attempts[endpoint] = 0
            self._set_connection_status('error')
            error_msg = f"Request failed after {self.retry_count} attempts: {error}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            
            if error_callback:
                try:
                    error_callback(error)
                except Exception as e:
                    logger.error(f"Error in error callback: {e}")
    
    # API Methods
    
    def check_health(self):
        """Check server health status"""
        self._make_request(
            ControlCenterConfig.API_ENDPOINTS['health'],
            callback=self._on_health_check
        )
    
    def _on_health_check(self, result: Dict):
        """Handle health check response"""
        self.health_check_completed.emit(result)
    
    def get_stats(self):
        """Get system statistics"""
        self._make_request(
            ControlCenterConfig.API_ENDPOINTS['stats'],
            callback=self._on_stats_received
        )
    
    def _on_stats_received(self, result: Dict):
        """Handle stats response"""
        self.stats_received.emit(result)
    
    def search(self, query: str, max_results: int = 10):
        """Execute search query"""
        endpoint = f"{ControlCenterConfig.API_ENDPOINTS['search']}?q={query}&max={max_results}"
        self._make_request(
            endpoint,
            callback=self._on_search_completed
        )
    
    def _on_search_completed(self, result: Dict):
        """Handle search response"""
        self.search_completed.emit(result)
    
    def get_history(self, limit: int = 100):
        """Get search history"""
        endpoint = f"{ControlCenterConfig.API_ENDPOINTS['history']}?limit={limit}"
        return self._make_request(endpoint)
    
    def get_cache_stats(self):
        """Get cache statistics"""
        return self._make_request(ControlCenterConfig.API_ENDPOINTS['cache_stats'])
    
    def clear_cache(self):
        """Clear search cache"""
        return self._make_request(
            ControlCenterConfig.API_ENDPOINTS['cache_clear'],
            method='POST'
        )
    
    def get_ranking_weights(self):
        """Get current ranking weights"""
        return self._make_request(ControlCenterConfig.API_ENDPOINTS['ranking_weights'])
    
    def get_monitoring_status(self):
        """Get monitoring status"""
        return self._make_request(ControlCenterConfig.API_ENDPOINTS['monitoring_status'])
    
    def test_connection(self) -> bool:
        """Test connection to server"""
        try:
            self._set_connection_status('connecting')
            self.check_health()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            self._set_connection_status('error')
            return False
