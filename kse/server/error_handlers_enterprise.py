"""
Enterprise-grade error handling for KSE Web Server
Implements production-ready error recovery and logging
"""

import logging
import traceback
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from functools import wraps
import json


class ErrorHandler:
    """Enterprise error handling with recovery strategies."""
    
    def __init__(self, log_file: str = 'logs/errors.log'):
        self.logger = logging.getLogger('KSE.ErrorHandler')
        self.log_file = log_file
        self._setup_logging()
        self.error_count = 0
        self.error_history = []
        self.max_history = 1000
    
    def _setup_logging(self):
        """Setup enterprise logging with rotation."""
        try:
            from logging.handlers import RotatingFileHandler
            handler = RotatingFileHandler(
                self.log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        except Exception as e:
            print(f"Failed to setup error logging: {e}")
    
    def log_error(
        self,
        error_type: str,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Log error with full context."""
        self.error_count += 1
        
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_id': f'ERR-{self.error_count}',
            'type': error_type,
            'message': message,
            'context': context or {},
            'traceback': traceback.format_exc() if exception else None
        }
        
        self.error_history.append(error_data)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # Log to file
        log_msg = f"[{error_data['error_id']}] {error_type}: {message}"
        if context:
            log_msg += f" | Context: {json.dumps(context)}"
        
        self.logger.error(log_msg, exc_info=exception)
        
        return error_data
    
    def get_error_history(self, limit: int = 100) -> list:
        """Get recent error history."""
        return self.error_history[-limit:]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        error_types = {}
        for error in self.error_history:
            err_type = error['type']
            error_types[err_type] = error_types.get(err_type, 0) + 1
        
        return {
            'total_errors': self.error_count,
            'errors_by_type': error_types,
            'recent_errors': len(self.error_history),
            'most_common': max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        }


class RetryStrategy:
    """Retry strategies for resilient operations."""
    
    @staticmethod
    def exponential_backoff(
        func,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ):
        """Execute function with exponential backoff retry."""
        import time
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(min(delay, max_delay))
                        delay *= 2  # Exponential backoff
                    continue
            
            raise last_exception
        
        return wrapper
    
    @staticmethod
    def circuit_breaker(
        failure_threshold: int = 5,
        timeout: int = 60
    ):
        """Decorator for circuit breaker pattern."""
        class CircuitBreaker:
            def __init__(self):
                self.failure_count = 0
                self.failure_threshold = failure_threshold
                self.timeout = timeout
                self.last_failure_time = None
                self.is_open = False
            
            def __call__(self, func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    if self.is_open:
                        elapsed = datetime.now().timestamp() - self.last_failure_time
                        if elapsed > self.timeout:
                            self.is_open = False
                            self.failure_count = 0
                        else:
                            raise Exception("Circuit breaker is open")
                    
                    try:
                        result = func(*args, **kwargs)
                        self.failure_count = 0
                        return result
                    except Exception as e:
                        self.failure_count += 1
                        self.last_failure_time = datetime.now().timestamp()
                        if self.failure_count >= self.failure_threshold:
                            self.is_open = True
                        raise e
                
                return wrapper
        
        return CircuitBreaker()


class ValidationError(Exception):
    """Validation error with context."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.context = context or {}
        super().__init__(message)


class InputValidator:
    """Enterprise input validation."""
    
    @staticmethod
    def validate_query(query: str, min_len: int = 2, max_len: int = 500) -> Tuple[bool, str]:
        """Validate search query."""
        if not query:
            return False, "Query cannot be empty"
        
        if len(query) < min_len:
            return False, f"Query must be at least {min_len} characters"
        
        if len(query) > max_len:
            return False, f"Query cannot exceed {max_len} characters"
        
        # Check for SQL injection patterns
        dangerous_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', '--', ';']
        if any(pattern in query.upper() for pattern in dangerous_patterns):
            return False, "Invalid query format"
        
        return True, ""
    
    @staticmethod
    def validate_pagination(limit: int, offset: int) -> Tuple[bool, str]:
        """Validate pagination parameters."""
        if limit < 1:
            return False, "Limit must be at least 1"
        
        if limit > 100:
            return False, "Limit cannot exceed 100"
        
        if offset < 0:
            return False, "Offset cannot be negative"
        
        return True, ""
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """Validate URL format."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # Protocol
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # Domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # Optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False, "Invalid URL format"
        
        return True, ""


class RecoveryStrategy:
    """Strategies for system recovery."""
    
    @staticmethod
    def fallback_cache(cache_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback to cached data on error."""
        if cache_data:
            return {
                'status': 'ok',
                'data': cache_data,
                'source': 'cache',
                'cached': True
            }
        return {'status': 'error', 'message': 'No cache available'}
    
    @staticmethod
    def graceful_degradation(feature: str) -> Dict[str, Any]:
        """Gracefully degrade functionality."""
        degraded_features = {
            'autocomplete': {'enabled': False, 'reason': 'Service temporarily unavailable'},
            'similar_pages': {'enabled': False, 'reason': 'Service temporarily unavailable'},
            'analytics': {'enabled': False, 'reason': 'Service temporarily unavailable'},
        }
        
        return degraded_features.get(feature, {'enabled': False, 'reason': 'Unknown feature'})


# Global error handler instance
error_handler = ErrorHandler()


def handle_enterprise_error(error_type: str, context: Optional[Dict[str, Any]] = None):
    """Decorator for enterprise error handling."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_data = error_handler.log_error(
                    error_type=error_type,
                    message=str(e),
                    exception=e,
                    context=context
                )
                # Re-raise with context
                raise ValueError(f"Error {error_data['error_id']}: {str(e)}") from e
        
        return wrapper
    return decorator
