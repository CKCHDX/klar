"""
Klar Android-Kotlin Communication Bridge
Handles bidirectional communication between Kotlin UI and Python engine
"""

import json
import threading
from typing import Optional, Callable, Dict, Any

try:
    from android_logger import get_logger
except ImportError:
    import logging
    def get_logger(name=None):
        return logging.getLogger(name or "KlarBridge")

logger = get_logger("KlarBridge")

# ============================================
# COMMUNICATION BRIDGE
# ============================================

class KlarBridge:
    """Bidirectional communication bridge between Kotlin and Python"""
    
    def __init__(self, engine):
        self.engine = engine
        self.callbacks: Dict[str, Callable] = {}
        self.lock = threading.Lock()
        logger.info("KlarBridge initialized")
    
    def register_callback(self, event_name: str, callback: Callable):
        """Register callback for event"""
        with self.lock:
            self.callbacks[event_name] = callback
            logger.debug(f"Callback registered: {event_name}")
    
    def unregister_callback(self, event_name: str):
        """Unregister callback"""
        with self.lock:
            if event_name in self.callbacks:
                del self.callbacks[event_name]
                logger.debug(f"Callback unregistered: {event_name}")
    
    def emit(self, event_name: str, data: Any = None):
        """Emit event to Kotlin"""
        with self.lock:
            if event_name in self.callbacks:
                try:
                    callback = self.callbacks[event_name]
                    callback(data)
                    logger.debug(f"Event emitted: {event_name}")
                except Exception as e:
                    logger.error(f"Error in callback {event_name}: {e}")
    
    def handle_search_request(self, query: str) -> str:
        """Handle search request from Kotlin"""
        logger.info(f"Search request: {query}")
        try:
            result = self.engine.search(query)
            self.emit("search_complete", json.loads(result))
            return result
        except Exception as e:
            error_response = json.dumps({"error": str(e), "query": query})
            self.emit("search_error", {"error": str(e)})
            logger.error(f"Search error: {e}")
            return error_response
    
    def handle_offline_search(self, query: str) -> str:
        """Handle offline search request"""
        logger.info(f"Offline search request: {query}")
        try:
            result = self.engine.offline_search(query)
            self.emit("offline_search_complete", json.loads(result))
            return result
        except Exception as e:
            error_response = json.dumps({"error": str(e), "query": query})
            self.emit("offline_search_error", {"error": str(e)})
            logger.error(f"Offline search error: {e}")
            return error_response
    
    def handle_url_check(self, url: str) -> str:
        """Handle URL whitelist check"""
        logger.debug(f"URL check: {url}")
        try:
            result = self.engine.check_url(url)
            return result
        except Exception as e:
            error_response = json.dumps({"error": str(e), "url": url})
            logger.error(f"URL check error: {e}")
            return error_response
    
    def handle_status_request(self) -> str:
        """Handle engine status request"""
        logger.debug("Status request")
        try:
            return self.engine.get_status()
        except Exception as e:
            error_response = json.dumps({"error": str(e)})
            logger.error(f"Status request error: {e}")
            return error_response
    
    def handle_command(self, command: str, params: Dict[str, Any] = None) -> str:
        """Handle generic command from Kotlin"""
        logger.info(f"Command: {command}")
        try:
            if command == "search":
                query = params.get("query", "") if params else ""
                return self.handle_search_request(query)
            elif command == "offline_search":
                query = params.get("query", "") if params else ""
                return self.handle_offline_search(query)
            elif command == "check_url":
                url = params.get("url", "") if params else ""
                return self.handle_url_check(url)
            elif command == "status":
                return self.handle_status_request()
            elif command == "get_platform_info":
                try:
                    from android_config import get_platform_info
                    info = get_platform_info()
                    return json.dumps({"success": True, "data": info})
                except Exception as e:
                    return json.dumps({"error": str(e)})
            else:
                return json.dumps({"error": f"Unknown command: {command}"})
        except Exception as e:
            logger.error(f"Command error: {e}")
            return json.dumps({"error": str(e), "command": command})

# ============================================
# ASYNC HANDLER
# ============================================

class AsyncBridge(KlarBridge):
    """Asynchronous bridge for long-running operations"""
    
    def search_async(self, query: str, on_complete: Callable, on_error: Callable):
        """Perform search asynchronously"""
        logger.info(f"Async search: {query}")
        
        def _search():
            try:
                result = self.handle_search_request(query)
                on_complete(json.loads(result))
            except Exception as e:
                logger.error(f"Async search error: {e}")
                on_error(str(e))
        
        thread = threading.Thread(target=_search, daemon=True)
        thread.start()
        return thread
    
    def offline_search_async(self, query: str, on_complete: Callable, on_error: Callable):
        """Perform offline search asynchronously"""
        logger.info(f"Async offline search: {query}")
        
        def _search():
            try:
                result = self.handle_offline_search(query)
                on_complete(json.loads(result))
            except Exception as e:
                logger.error(f"Async offline search error: {e}")
                on_error(str(e))
        
        thread = threading.Thread(target=_search, daemon=True)
        thread.start()
        return thread
