"""kse_monitoring_coordinator.py - Main Monitoring Orchestrator

Coordinates all monitoring components:
- System health
- Crawler performance
- Index health
- Alert management
"""

import logging
from typing import Dict
from datetime import datetime

from kse.core import get_logger

logger = get_logger('monitoring')


class MonitoringCoordinator:
    """Main monitoring orchestrator"""
    
    def __init__(self,
                 system_monitor,
                 log_monitor,
                 crawler_monitor,
                 index_monitor):
        """Initialize monitoring coordinator
        
        Args:
            system_monitor: SystemMonitor instance
            log_monitor: LogMonitor instance
            crawler_monitor: CrawlerMonitor instance
            index_monitor: IndexMonitor instance
        """
        self.system = system_monitor
        self.logs = log_monitor
        self.crawler = crawler_monitor
        self.index = index_monitor
        
        self.alerts = []
        logger.info("MonitoringCoordinator initialized")
    
    def get_full_health_report(self) -> Dict:
        """Get complete health report
        
        Returns:
            Full health report
        """
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system': self.system.get_system_health(),
            'crawler': self.crawler.get_crawler_health(),
            'index': self.index.get_index_health(),
            'logs': self.logs.get_log_statistics(),
            'alerts': self._check_alerts(),
        }
    
    def get_summary(self) -> str:
        """Get formatted health summary
        
        Returns:
            Formatted summary string
        """
        report = self.get_full_health_report()
        
        summary = f"""
KSE Health Summary [{report['timestamp']}]
={'='*60}

System Status: {report['system']['status'].upper()}
  CPU:     {report['system']['cpu_usage']}%
  Memory:  {report['system']['memory']['percent']}%
  Disk:    {report['system']['disk']['percent']}%

Crawler Status: {report['crawler']['status'].upper()}
  Pages:   {report['crawler']['pages_crawled']} ✓ / {report['crawler']['pages_failed']} ✗
  Rate:    {report['crawler']['pages_per_second']} pages/sec
  Speed:   {report['crawler']['mb_per_second']} MB/sec

Index Status: {report['index']['status'].upper()}
  Documents:  {report['index']['total_documents']}
  Size:       {report['index']['index_size_mb']:.1f} MB
  Age:        {report['index']['index_age_hours']:.1f} hours
  Query Time: {report['index']['avg_query_time_ms']:.1f} ms

Alerts: {len(report['alerts'])}
{self._format_alerts(report['alerts'])}
""".strip()
        
        return summary
    
    def _check_alerts(self) -> list:
        """Check for alert conditions
        
        Returns:
            List of active alerts
        """
        alerts = []
        
        # System alerts
        sys_health = self.system.get_system_health()
        if sys_health['status'] != 'healthy':
            alerts.append({
                'severity': 'warning' if sys_health['status'] == 'warning' else 'critical',
                'component': 'system',
                'message': f"System health: {sys_health['status']}",
            })
        
        # Crawler alerts
        crawler_health = self.crawler.get_crawler_health()
        if crawler_health['status'] != 'healthy':
            alerts.append({
                'severity': 'warning' if crawler_health['status'] == 'warning' else 'critical',
                'component': 'crawler',
                'message': f"Crawler health: {crawler_health['status']}",
            })
        
        # Index alerts
        index_health = self.index.get_index_health()
        if index_health['status'] != 'healthy':
            alerts.append({
                'severity': 'warning',
                'component': 'index',
                'message': f"Index status: {index_health['status']}",
            })
        
        # Log alerts
        error_summary = self.logs.get_error_summary()
        if error_summary['total_errors'] > 10:
            alerts.append({
                'severity': 'warning',
                'component': 'logs',
                'message': f"High error count: {error_summary['total_errors']}",
            })
        
        return alerts
    
    def _format_alerts(self, alerts: list) -> str:
        """Format alerts for display
        
        Args:
            alerts: List of alerts
            
        Returns:
            Formatted alert string
        """
        if not alerts:
            return "  ✓ No active alerts"
        
        lines = []
        for alert in alerts:
            icon = '⚠️' if alert['severity'] == 'warning' else '🔴'
            lines.append(f"  {icon} [{alert['component'].upper()}] {alert['message']}")
        
        return '\n'.join(lines)


__all__ = ["MonitoringCoordinator"]
