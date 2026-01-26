"""
kse/monitoring/__init__.py - System Monitoring & Health Tracking

Components:
  - SystemMonitor: CPU, memory, disk usage
  - LogMonitor: Log analysis & error tracking
  - CrawlerMonitor: Crawler performance
  - IndexMonitor: Index health & freshness
  - MonitoringCoordinator: Main orchestrator

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from .kse_system_monitor import SystemMonitor
from .kse_log_monitor import LogMonitor
from .kse_crawler_monitor import CrawlerMonitor
from .kse_index_monitor import IndexMonitor
from .kse_monitoring_coordinator import MonitoringCoordinator

__all__ = [
    # Core Monitors
    "SystemMonitor",
    "LogMonitor",
    "CrawlerMonitor",
    "IndexMonitor",
    
    # Coordinator
    "MonitoringCoordinator",
]

__version__ = "1.0.0"
__author__ = "Klar Development Team"


# Quick start examples
"""
QUICK START - Monitoring Layer

1. System monitoring:
    from kse.monitoring import SystemMonitor
    
    monitor = SystemMonitor()
    health = monitor.get_system_health()
    print(f"CPU: {health['cpu_usage']}%")
    print(f"Memory: {health['memory']['percent']}%")

2. Log monitoring:
    from kse.monitoring import LogMonitor
    
    logs = LogMonitor('logs/kse.log')
    errors = logs.get_error_summary()
    print(f"Errors: {errors['total_errors']}")

3. Crawler monitoring:
    from kse.monitoring import CrawlerMonitor
    
    crawler = CrawlerMonitor()
    crawler.record_page_crawl('https://example.com', success=True, bytes_downloaded=5000)
    health = crawler.get_crawler_health()
    print(f"Success rate: {health['success_rate']}%")

4. Index monitoring:
    from kse.monitoring import IndexMonitor
    
    index = IndexMonitor()
    index.update_index_stats(doc_count=1000000, index_size_bytes=500000000)
    health = index.get_index_health()
    print(f"Documents: {health['total_documents']}")

5. Complete monitoring:
    from kse.monitoring import (
        SystemMonitor, LogMonitor, CrawlerMonitor,
        IndexMonitor, MonitoringCoordinator
    )
    
    # Initialize all monitors
    system = SystemMonitor()
    logs = LogMonitor('logs/kse.log')
    crawler = CrawlerMonitor()
    index = IndexMonitor()
    
    # Create coordinator
    coordinator = MonitoringCoordinator(system, logs, crawler, index)
    
    # Get full health report
    report = coordinator.get_full_health_report()
    print(coordinator.get_summary())

MONITORING ARCHITECTURE:

kse/monitoring/
├── kse_system_monitor.py           System resources (CPU, RAM, disk)
├── kse_log_monitor.py              Log analysis & errors
├── kse_crawler_monitor.py          Crawler performance
├── kse_index_monitor.py            Index health & stats
├── kse_monitoring_coordinator.py   Main orchestrator
└── __init__.py                     Public API

INTEGRATION:

- Phase 1 (core): Logging system
- Phase 4 (crawler): Crawler stats
- Phase 6 (indexing): Index stats
- Phase 9 (server): API metrics
- Phase 10 (gui): Dashboard display

HEALTH MONITORING:

System Health:
  - CPU usage: < 80% (warning), < 95% (critical)
  - Memory: < 80% (warning), < 95% (critical)
  - Disk: < 80% (warning), < 95% (critical)

Crawler Health:
  - Success rate: > 80% (healthy), < 50% (critical)
  - Speed: pages/sec, MB/sec
  - Errors: timeout, connection, rate limit

Index Health:
  - Status: healthy, slow, stale, outdated
  - Age: < 24h (healthy), > 72h (outdated)
  - Query time: avg ms, p95 ms
  - Size: MB, documents, bytes per doc

Alerts:
  ✓ Automatic alert generation for:
    - System resource issues
    - Crawler failures
    - Index staleness
    - High error rates
    - Slow query times

METRICS COLLECTED:

System:
  - CPU usage (percent)
  - Memory used (MB, percent)
  - Disk used (GB, percent)

Crawler:
  - Pages crawled/failed
  - Success rate
  - Pages per second
  - MB per second downloaded
  - Error types & counts

Index:
  - Total documents
  - Index size (MB, GB)
  - Index age (hours)
  - Average query time (ms)
  - Total queries processed

Logs:
  - Total lines
  - Error count
  - Warning count
  - Info count
  - Debug count

PERFORMANCE TARGETS:

- System monitoring: < 1s
- Log analysis: < 500ms
- Crawler stats: < 100ms
- Index stats: < 100ms
- Full report: < 2s
- Alert check: < 1s

EXAMPLE OUTPUT:

KSE Health Summary [2026-01-26T14:00:00Z]
============================================================

System Status: HEALTHY
  CPU:     42.5%
  Memory:  65.3%
  Disk:    28.1%

Crawler Status: HEALTHY
  Pages:   2,850,000 ✓ / 125,000 ✗
  Rate:    125.3 pages/sec
  Speed:   45.2 MB/sec

Index Status: HEALTHY
  Documents:  2,750,000
  Size:       523.5 MB
  Age:        12.3 hours
  Query Time: 42.1 ms

Alerts: 0
  ✓ No active alerts

DASHBOARD INTEGRATION:

The monitoring system provides real-time metrics for:
1. System Monitor Panel
   - CPU, Memory, Disk gauges
   - Resource usage trends

2. Crawler Status Panel
   - Pages crawled/failed
   - Success rate
   - Crawl speed

3. Index Status Panel
   - Document count
   - Index size
   - Query performance

4. Alerts Panel
   - Active alerts with severity
   - Alert history
   - Auto-recovery status

API INTEGRATION:

GET /api/monitoring/health
  Returns: Full health report

GET /api/monitoring/system
  Returns: System metrics

GET /api/monitoring/crawler
  Returns: Crawler metrics

GET /api/monitoring/index
  Returns: Index metrics

GET /api/monitoring/alerts
  Returns: Active alerts

GET /api/monitoring/summary
  Returns: Formatted summary

DEPLOYMENT:

# Start monitoring
coordinator = MonitoringCoordinator(...)

# Get report periodically
import threading

def monitor_loop():
    while True:
        report = coordinator.get_full_health_report()
        # Send to API/dashboard
        time.sleep(10)  # Check every 10 seconds

# Run in background
monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
monitor_thread.start()
"""
