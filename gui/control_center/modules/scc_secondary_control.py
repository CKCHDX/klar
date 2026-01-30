"""
SECONDARY CONTROL CENTER (SCC)
Search and crawler analytics with data export capabilities
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import csv

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QComboBox, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from gui.kse_gui_config import GUIConfig
from gui.kse_gui_styles import Styles
from gui.control_center.control_center_api_client import ControlCenterAPIClient

logger = logging.getLogger(__name__)


class AnalyticsCard(QFrame):
    """Analytics metric card"""
    
    def __init__(self, title: str, icon: str = ""):
        super().__init__()
        self.setStyleSheet(Styles.get_metric_card_style())
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(140)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Icon and title
        header_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"""
                QLabel {{
                    color: {GUIConfig.COLORS['primary']};
                    font-size: {GUIConfig.get_font_size('header')}pt;
                }}
            """)
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_secondary']};
                font-size: {GUIConfig.get_font_size('medium')}pt;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Primary value
        self.value_label = QLabel("--")
        value_font_size = GUIConfig.get_font_size('header') + 8  # Slightly larger than header
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_primary']};
                font-size: {value_font_size}pt;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.value_label)
        
        # Secondary info
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['text_secondary']};
                font-size: {GUIConfig.get_font_size('small')}pt;
            }}
        """)
        layout.addWidget(self.info_label)
        
        # Trend indicator
        self.trend_label = QLabel("")
        self.trend_label.setStyleSheet(f"""
            QLabel {{
                color: {GUIConfig.COLORS['success']};
                font-size: {GUIConfig.get_font_size('small')}pt;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.trend_label)
        
        layout.addStretch()
    
    def update_value(self, value: str, info: str = "", trend: str = "", trend_positive: bool = True):
        """Update card values"""
        self.value_label.setText(value)
        self.info_label.setText(info)
        self.trend_label.setText(trend)
        
        if trend:
            color = GUIConfig.COLORS['success'] if trend_positive else GUIConfig.COLORS['error']
            self.trend_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: {GUIConfig.get_font_size('small')}pt;
                    font-weight: bold;
                }}
            """)


class SearchAnalytics(QFrame):
    """Search analytics display"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Search Analytics")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Analytics cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)
        
        self.queries_today_card = AnalyticsCard("Queries Today", "🔍")
        cards_layout.addWidget(self.queries_today_card, 0, 0)
        
        self.avg_latency_card = AnalyticsCard("Avg Latency", "⚡")
        cards_layout.addWidget(self.avg_latency_card, 0, 1)
        
        self.popular_terms_card = AnalyticsCard("Popular Term", "📊")
        cards_layout.addWidget(self.popular_terms_card, 0, 2)
        
        layout.addLayout(cards_layout)
    
    def update_analytics(self, data: Dict[str, Any]):
        """Update search analytics"""
        queries_today = data.get('queries_today', 0)
        queries_yesterday = data.get('queries_yesterday', 0)
        
        # Calculate trend
        if queries_yesterday > 0:
            change_percent = ((queries_today - queries_yesterday) / queries_yesterday) * 100
            trend = f"{'↑' if change_percent > 0 else '↓'} {abs(change_percent):.1f}% vs yesterday"
            trend_positive = change_percent > 0
        else:
            trend = ""
            trend_positive = True
        
        self.queries_today_card.update_value(
            f"{queries_today:,}",
            f"{queries_yesterday:,} yesterday",
            trend,
            trend_positive
        )
        
        # Average latency
        avg_latency = data.get('average_latency', 0)
        self.avg_latency_card.update_value(
            f"{avg_latency:.0f} ms",
            f"Max: {data.get('max_latency', 0):.0f} ms",
            f"Min: {data.get('min_latency', 0):.0f} ms",
            avg_latency < 100
        )
        
        # Popular term
        popular_term = data.get('popular_term', '--')
        popular_count = data.get('popular_count', 0)
        self.popular_terms_card.update_value(
            f"{popular_term}",
            f"{popular_count} searches",
            ""
        )


class CrawlerAnalytics(QFrame):
    """Crawler analytics display"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Crawler Analytics")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Analytics cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)
        
        self.pages_today_card = AnalyticsCard("Pages Today", "🌐")
        cards_layout.addWidget(self.pages_today_card, 0, 0)
        
        self.success_rate_card = AnalyticsCard("Success Rate", "✓")
        cards_layout.addWidget(self.success_rate_card, 0, 1)
        
        self.errors_card = AnalyticsCard("Errors", "⚠️")
        cards_layout.addWidget(self.errors_card, 0, 2)
        
        layout.addLayout(cards_layout)
    
    def update_analytics(self, data: Dict[str, Any]):
        """Update crawler analytics"""
        pages_today = data.get('pages_today', 0)
        pages_yesterday = data.get('pages_yesterday', 0)
        
        # Calculate trend
        if pages_yesterday > 0:
            change_percent = ((pages_today - pages_yesterday) / pages_yesterday) * 100
            trend = f"{'↑' if change_percent > 0 else '↓'} {abs(change_percent):.1f}% vs yesterday"
            trend_positive = change_percent > 0
        else:
            trend = ""
            trend_positive = True
        
        self.pages_today_card.update_value(
            f"{pages_today:,}",
            f"{pages_yesterday:,} yesterday",
            trend,
            trend_positive
        )
        
        # Success rate
        success_count = data.get('success_count', 0)
        total_count = data.get('total_count', 0)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        self.success_rate_card.update_value(
            f"{success_rate:.1f}%",
            f"{success_count:,} / {total_count:,}",
            "Healthy" if success_rate > 95 else "Issues detected",
            success_rate > 95
        )
        
        # Errors
        errors = data.get('errors_count', 0)
        self.errors_card.update_value(
            f"{errors}",
            f"{data.get('error_rate', 0):.1f}% error rate",
            "",
            errors == 0
        )


class QueryTrendingTable(QFrame):
    """Query trending table - top searches"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Trending Queries (Top 20)")
        title.setStyleSheet(Styles.get_title_style('medium'))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Time range selector
        time_label = QLabel("Period:")
        header_layout.addWidget(time_label)
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(['Today', 'Last 7 Days', 'Last 30 Days', 'All Time'])
        self.time_range_combo.currentTextChanged.connect(self._on_time_range_changed)
        header_layout.addWidget(self.time_range_combo)
        
        layout.addLayout(header_layout)
        
        # Trending table
        self.trending_table = QTableWidget()
        self.trending_table.setStyleSheet(Styles.get_table_style())
        self.trending_table.setColumnCount(5)
        self.trending_table.setHorizontalHeaderLabels([
            'Rank', 'Query', 'Count', 'Avg Latency', 'Trend'
        ])
        self.trending_table.setColumnWidth(0, 60)
        self.trending_table.setColumnWidth(1, 300)
        self.trending_table.setColumnWidth(2, 80)
        self.trending_table.setColumnWidth(3, 100)
        self.trending_table.setColumnWidth(4, 80)
        self.trending_table.setMaximumHeight(400)
        self.trending_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.trending_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.trending_table)
    
    def _on_time_range_changed(self, time_range: str):
        """Handle time range change"""
        logger.info(f"Time range changed to: {time_range}")
        # Trigger data refresh for new time range
    
    def update_trending(self, queries: List[Dict[str, Any]]):
        """Update trending queries"""
        self.trending_table.setRowCount(0)
        
        for i, query in enumerate(queries[:20], 1):
            row = self.trending_table.rowCount()
            self.trending_table.insertRow(row)
            
            # Rank
            rank_item = QTableWidgetItem(str(i))
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.trending_table.setItem(row, 0, rank_item)
            
            # Query
            query_item = QTableWidgetItem(query.get('query', ''))
            self.trending_table.setItem(row, 1, query_item)
            
            # Count
            count_item = QTableWidgetItem(f"{query.get('count', 0):,}")
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.trending_table.setItem(row, 2, count_item)
            
            # Avg Latency
            latency = query.get('avg_latency', 0)
            latency_item = QTableWidgetItem(f"{latency:.0f} ms")
            latency_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.trending_table.setItem(row, 3, latency_item)
            
            # Trend
            trend = query.get('trend', 0)
            trend_text = f"{'↑' if trend > 0 else '↓'}{abs(trend):.0f}%"
            trend_item = QTableWidgetItem(trend_text)
            trend_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            trend_color = GUIConfig.COLORS['success'] if trend > 0 else GUIConfig.COLORS['error']
            trend_item.setForeground(trend_color)
            self.trending_table.setItem(row, 4, trend_item)


class DomainStatisticsTable(QFrame):
    """Domain statistics table"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Domain Statistics")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Domain table
        self.domain_table = QTableWidget()
        self.domain_table.setStyleSheet(Styles.get_table_style())
        self.domain_table.setColumnCount(5)
        self.domain_table.setHorizontalHeaderLabels([
            'Domain', 'Pages', 'Size (MB)', 'Last Crawl', 'Status'
        ])
        self.domain_table.setColumnWidth(0, 250)
        self.domain_table.setColumnWidth(1, 80)
        self.domain_table.setColumnWidth(2, 100)
        self.domain_table.setColumnWidth(3, 150)
        self.domain_table.setColumnWidth(4, 100)
        self.domain_table.setMaximumHeight(300)
        self.domain_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.domain_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.domain_table)
    
    def update_domains(self, domains: List[Dict[str, Any]]):
        """Update domain statistics"""
        self.domain_table.setRowCount(0)
        
        for domain in domains:
            row = self.domain_table.rowCount()
            self.domain_table.insertRow(row)
            
            # Domain
            domain_item = QTableWidgetItem(domain.get('domain', ''))
            self.domain_table.setItem(row, 0, domain_item)
            
            # Pages
            pages_item = QTableWidgetItem(f"{domain.get('pages', 0):,}")
            pages_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.domain_table.setItem(row, 1, pages_item)
            
            # Size
            size_mb = domain.get('size_mb', 0)
            size_item = QTableWidgetItem(f"{size_mb:.2f}")
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.domain_table.setItem(row, 2, size_item)
            
            # Last crawl
            last_crawl = domain.get('last_crawl', '')
            crawl_item = QTableWidgetItem(last_crawl)
            self.domain_table.setItem(row, 3, crawl_item)
            
            # Status
            status = domain.get('status', 'unknown')
            status_item = QTableWidgetItem(status)
            status_color = GUIConfig.get_status_color(status)
            status_item.setForeground(status_color)
            self.domain_table.setItem(row, 4, status_item)


class DataExportPanel(QFrame):
    """Data export panel"""
    
    export_requested = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(Styles.get_card_style())
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Data Export")
        title.setStyleSheet(Styles.get_title_style('medium'))
        layout.addWidget(title)
        
        # Export options
        options_layout = QHBoxLayout()
        
        # Data type selector
        type_label = QLabel("Data Type:")
        options_layout.addWidget(type_label)
        
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems([
            'Search Analytics',
            'Crawler Statistics',
            'Query Trending',
            'Domain Statistics',
            'All Data'
        ])
        options_layout.addWidget(self.data_type_combo)
        
        # Format selector
        format_label = QLabel("Format:")
        options_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(['CSV', 'JSON', 'Excel'])
        options_layout.addWidget(self.format_combo)
        
        options_layout.addStretch()
        
        layout.addLayout(options_layout)
        
        # Export button
        self.export_btn = QPushButton("📥 Export Data")
        self.export_btn.setStyleSheet(Styles.get_button_style())
        self.export_btn.clicked.connect(self._on_export)
        layout.addWidget(self.export_btn)
        
        # Status
        self.status_label = QLabel("Ready to export")
        self.status_label.setStyleSheet(f"color: {GUIConfig.COLORS['text_secondary']};")
        layout.addWidget(self.status_label)
    
    def _on_export(self):
        """Handle export request"""
        data_type = self.data_type_combo.currentText()
        format_type = self.format_combo.currentText().lower()
        
        # Open file dialog
        default_filename = f"kse_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_filter = {
            'csv': 'CSV Files (*.csv)',
            'json': 'JSON Files (*.json)',
            'excel': 'Excel Files (*.xlsx)'
        }.get(format_type, 'All Files (*.*)')
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            default_filename,
            file_filter
        )
        
        if filename:
            self.export_requested.emit(data_type, filename)
            self.status_label.setText(f"Exported to: {filename}")


class SCCSecondaryControl(QWidget):
    """Secondary Control Center - Analytics & Reporting"""
    
    def __init__(self, api_client: ControlCenterAPIClient):
        super().__init__()
        self.api_client = api_client
        self.update_timer = QTimer()
        self.update_timer.setInterval(15000)  # 15 seconds
        self.update_timer.timeout.connect(self.refresh_data)
        
        self._setup_ui()
        self._connect_signals()
        
        logger.info("SCC Secondary Control initialized")
    
    def _setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        title = QLabel("Analytics & Reporting Dashboard")
        title.setStyleSheet(Styles.get_title_style('header'))
        main_layout.addWidget(title)
        
        # Search analytics
        self.search_analytics = SearchAnalytics()
        main_layout.addWidget(self.search_analytics)
        
        # Crawler analytics
        self.crawler_analytics = CrawlerAnalytics()
        main_layout.addWidget(self.crawler_analytics)
        
        # Query trending table
        self.query_trending = QueryTrendingTable()
        main_layout.addWidget(self.query_trending)
        
        # Domain statistics table
        self.domain_statistics = DomainStatisticsTable()
        main_layout.addWidget(self.domain_statistics)
        
        # Data export panel
        self.export_panel = DataExportPanel()
        main_layout.addWidget(self.export_panel)
    
    def _connect_signals(self):
        """Connect signals"""
        self.export_panel.export_requested.connect(self._on_export_data)
        self.api_client.stats_received.connect(self._on_stats_update)
    
    def showEvent(self, event):
        """Handle widget show event"""
        super().showEvent(event)
        self.start_updates()
        self.refresh_data()
    
    def hideEvent(self, event):
        """Handle widget hide event"""
        super().hideEvent(event)
        self.stop_updates()
    
    def start_updates(self):
        """Start automatic updates"""
        if not self.update_timer.isActive():
            self.update_timer.start()
            logger.info("SCC updates started")
    
    def stop_updates(self):
        """Stop automatic updates"""
        if self.update_timer.isActive():
            self.update_timer.stop()
            logger.info("SCC updates stopped")
    
    def refresh_data(self):
        """Refresh analytics data"""
        try:
            self.api_client.get_stats()
            self._load_sample_data()  # Load sample data for demonstration
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
    
    def _load_sample_data(self):
        """Load sample data for demonstration"""
        # Sample search analytics
        search_data = {
            'queries_today': 1543,
            'queries_yesterday': 1421,
            'average_latency': 45.3,
            'max_latency': 234.5,
            'min_latency': 12.1,
            'popular_term': 'python tutorial',
            'popular_count': 127
        }
        self.search_analytics.update_analytics(search_data)
        
        # Sample crawler analytics
        crawler_data = {
            'pages_today': 2341,
            'pages_yesterday': 2198,
            'success_count': 2287,
            'total_count': 2341,
            'errors_count': 54,
            'error_rate': 2.3
        }
        self.crawler_analytics.update_analytics(crawler_data)
        
        # Sample trending queries
        trending_queries = [
            {'query': 'python tutorial', 'count': 127, 'avg_latency': 42.1, 'trend': 15.3},
            {'query': 'javascript guide', 'count': 98, 'avg_latency': 38.5, 'trend': -5.2},
            {'query': 'react hooks', 'count': 87, 'avg_latency': 51.2, 'trend': 23.1},
            {'query': 'docker containers', 'count': 76, 'avg_latency': 47.8, 'trend': 8.4},
            {'query': 'kubernetes tutorial', 'count': 65, 'avg_latency': 55.3, 'trend': 12.7},
            {'query': 'machine learning', 'count': 54, 'avg_latency': 62.1, 'trend': -3.5},
            {'query': 'api design', 'count': 48, 'avg_latency': 39.2, 'trend': 19.8},
            {'query': 'database optimization', 'count': 42, 'avg_latency': 58.6, 'trend': 7.2},
        ]
        self.query_trending.update_trending(trending_queries)
        
        # Sample domain statistics
        domains = [
            {'domain': 'docs.python.org', 'pages': 3421, 'size_mb': 156.8, 'last_crawl': '2024-01-29 10:30', 'status': 'running'},
            {'domain': 'developer.mozilla.org', 'pages': 2876, 'size_mb': 234.2, 'last_crawl': '2024-01-29 09:45', 'status': 'running'},
            {'domain': 'stackoverflow.com', 'pages': 1543, 'size_mb': 89.5, 'last_crawl': '2024-01-29 11:15', 'status': 'running'},
            {'domain': 'github.com', 'pages': 987, 'size_mb': 67.3, 'last_crawl': '2024-01-28 22:30', 'status': 'stopped'},
        ]
        self.domain_statistics.update_domains(domains)
    
    def _on_stats_update(self, data: Dict[str, Any]):
        """Handle stats update from API"""
        try:
            # Update analytics with real data if available
            pass
        except Exception as e:
            logger.error(f"Error processing stats update: {e}")
    
    def _on_export_data(self, data_type: str, filename: str):
        """Handle data export request"""
        logger.info(f"Exporting {data_type} to {filename}")
        
        try:
            # Determine format from filename
            if filename.endswith('.json'):
                self._export_json(data_type, filename)
            elif filename.endswith('.csv'):
                self._export_csv(data_type, filename)
            else:
                logger.warning(f"Unsupported export format: {filename}")
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
    
    def _export_json(self, data_type: str, filename: str):
        """Export data as JSON"""
        data = {
            'export_date': datetime.now().isoformat(),
            'data_type': data_type,
            'data': {}  # Would contain actual data
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data exported to JSON: {filename}")
    
    def _export_csv(self, data_type: str, filename: str):
        """Export data as CSV"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Export Date', datetime.now().isoformat()])
            writer.writerow(['Data Type', data_type])
            writer.writerow([])
            # Would write actual data rows here
        
        logger.info(f"Data exported to CSV: {filename}")
