"""
Monitoring Core - Main monitoring system for KSE
Coordinates health checks, metrics collection, and system diagnostics
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)


class MonitoringCore:
    """Main monitoring system orchestrator"""
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize monitoring core
        
        Args:
            check_interval: Interval between health checks in seconds
        """
        self.check_interval = check_interval
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Initialize sub-systems
        from kse.monitoring.kse_health_checker import HealthChecker
        from kse.monitoring.kse_metrics_collector import MetricsCollector
        
        self.health_checker = HealthChecker()
        self.metrics_collector = MetricsCollector()
        
        logger.info(f"MonitoringCore initialized (check_interval={check_interval}s)")
    
    def start_monitoring(self) -> None:
        """Start continuous monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform health check
                health_status = self.health_checker.check_system_health()
                
                # Collect metrics
                metrics = self.metrics_collector.collect_metrics()
                
                # Log any issues
                if not health_status.get('healthy', True):
                    logger.warning(f"System health check failed: {health_status}")
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            # Wait for next check
            time.sleep(self.check_interval)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status
        
        Returns:
            System status dictionary
        """
        health = self.health_checker.check_system_health()
        metrics = self.metrics_collector.get_current_metrics()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health': health,
            'metrics': metrics,
            'monitoring_active': self.monitoring_active
        }
    
    def check_component(self, component_name: str) -> Dict[str, Any]:
        """
        Check specific component health
        
        Args:
            component_name: Name of component to check
        
        Returns:
            Component health status
        """
        return self.health_checker.check_component(component_name)
