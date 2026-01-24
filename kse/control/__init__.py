"""
KSE Control Center Module

PyQt6-based GUI for managing the Klar Search Engine.
"""

from .kse_main_window import KSEMainWindow
from .kse_dialogs import (
    CrawlerControlDialog,
    IndexingDialog,
    SettingsDialog,
    DatabaseDialog,
)
from .kse_workers import (
    CrawlerWorker,
    IndexerWorker,
    SearchWorker,
)
from .kse_app import KSEControlApplication

__version__ = "1.0.0"
__all__ = [
    "KSEMainWindow",
    "CrawlerControlDialog",
    "IndexingDialog",
    "SettingsDialog",
    "DatabaseDialog",
    "CrawlerWorker",
    "IndexerWorker",
    "SearchWorker",
    "KSEControlApplication",
]
