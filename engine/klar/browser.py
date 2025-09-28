import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl
from qasync import QEventLoop, asyncSlot
import asyncio

from crawler import DynamicCrawler
from parser import parse_html
from indexer import BM25Indexer


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_domain_metadata():
    path = resource_path("domains.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class BackendBridge(QObject):
    sendResults = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        domain_metadata = load_domain_metadata()
        self.crawler = DynamicCrawler(domain_metadata)
        self.index = BM25Indexer()

    @asyncSlot(str)
    async def search(self, query):
        seeds = await self.crawler.find_seeds(query)
        pages = await self.crawler.crawl(seeds)
        for url, html in pages.items():
            title, snippet, text = parse_html(html)
            if text:
                self.index.add_document(url, title, snippet, text)
        results = self.index.search(query)
        self.sendResults.emit(json.dumps(results))

    @pyqtSlot(str)
    def open_url(self, url):
        # Loads the URL inside the web view
        if self.parent():
            self.parent().load_url(url)


class KlarBrowser(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Klar Search Engine")
        self.resize(1280, 900)

        self.browser = QWebEngineView()
        self.channel = QWebChannel()
        self.bridge = BackendBridge(self)
        self.channel.registerObject("backend", self.bridge)
        self.browser.page().setWebChannel(self.channel)
        self.browser.page().profile().setHttpCacheType(self.browser.page().profile().MemoryHttpCache)

        index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates", "index.html"))
        self.browser.load(QUrl.fromLocalFile(index_path))

        self.setCentralWidget(self.browser)

    def load_url(self, url):
        self.browser.load(QUrl(url))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = KlarBrowser()
    window.show()

    with loop:
        loop.run_forever()
