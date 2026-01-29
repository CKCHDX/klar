"""
Alerts - Alert system for monitoring
"""

import logging
from typing import Dict, Any, List, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alert:
    """Alert data structure"""
    
    def __init__(self, level: AlertLevel, message: str, component: str, details: Dict[str, Any] = None):
        self.level = level
        self.message = message
        self.component = component
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            'level': self.level.value,
            'message': self.message,
            'component': self.component,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class AlertSystem:
    """Alert management system"""
    
    def __init__(self, max_alerts: int = 1000):
        """
        Initialize alert system
        
        Args:
            max_alerts: Maximum number of alerts to keep in memory
        """
        self.max_alerts = max_alerts
        self.alerts = []
        self.handlers = []
        logger.info(f"AlertSystem initialized (max_alerts={max_alerts})")
    
    def raise_alert(
        self,
        level: AlertLevel,
        message: str,
        component: str,
        details: Dict[str, Any] = None
    ) -> None:
        """
        Raise a new alert
        
        Args:
            level: Alert severity level
            message: Alert message
            component: Component that raised the alert
            details: Additional alert details
        """
        alert = Alert(level, message, component, details)
        self.alerts.append(alert)
        
        # Trim old alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        # Log alert
        log_func = getattr(logger, level.value, logger.info)
        log_func(f"[{component}] {message}")
        
        # Call handlers
        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def register_handler(self, handler: Callable[[Alert], None]) -> None:
        """Register alert handler function"""
        self.handlers.append(handler)
        logger.info("Alert handler registered")
    
    def get_alerts(
        self,
        level: AlertLevel = None,
        component: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get alerts with optional filtering
        
        Args:
            level: Filter by alert level
            component: Filter by component
            limit: Maximum number of alerts to return
        
        Returns:
            List of alert dictionaries
        """
        filtered = self.alerts
        
        if level:
            filtered = [a for a in filtered if a.level == level]
        
        if component:
            filtered = [a for a in filtered if a.component == component]
        
        # Get most recent alerts
        filtered = filtered[-limit:]
        
        return [alert.to_dict() for alert in filtered]
    
    def clear_alerts(self) -> None:
        """Clear all alerts"""
        self.alerts.clear()
        logger.info("Alerts cleared")
