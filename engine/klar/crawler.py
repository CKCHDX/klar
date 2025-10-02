import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


class DynamicCrawler:
    def __init__(self, domain_metadata, max_pages=30):
        self.domain_metadata = domain_metadata
        self.max_pages = max_pages
        self.cache = {}

        # ASI-specific: priority URL path patterns to restrict crawl
        self.priority_paths = {
            "nyheter": ["/nyheter", "/news", "/aktuellt"],
            "priser": ["/priser", "/price", "/produktsida"],
            "about": ["/om-oss", "/about", "/kontakt"],
            "handel": ["/butik", "/produkter", "/faq"],
        }

    async def fetch(self, session, url):
        if url in self.cache:
            return self.cache[url]

        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200 and "text/html" in resp.headers.get("Content-Type", ""):
                    text = await resp.text()

                    if self.is_swedish(text):
                        self.cache[url] = text
                        return text
        except Exception as e:
            print(f"Failed fetch {url}: {e}")
        return None

    def is_swedish(self, text):
        swedish_stopwords = {"och", "är", "att", "det", "som", "en", "på"}
        tokens = set(word.lower() for word in text.split()[:1000])
        matched = tokens.intersection(swedish_stopwords)
        return len(matched) >= 3

    def score_url(self, url):
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        score = 0
        if domain in self.domain_metadata:
            score += 5
        if parsed.scheme == "https":
            score += 3

        for paths in self.priority_paths.values():
            if any(path.startswith(p) for p in paths):
                score += 4
        return score

    async def find_seeds(self, query: str):
        query_tokens = [t.lower() for t in query.split() if t]

        seeds = []
        for domain, keywords in self.domain_metadata.items():
            if any(q in domain or q in keyword for q in query_tokens for keyword in keywords):
                seeds.append(f"https://{domain}")
        if not seeds:
            seeds = list(self.domain_metadata.keys())[:3]
            seeds = [f"https://{d}" for d in seeds]
        print(f"Seeds: {seeds}")
        return seeds

    async def crawl(self, seeds):
        pages = {}
        async with aiohttp.ClientSession() as session:
            to_crawl = set(seeds)
            crawled = set()

            while to_crawl and len(pages) < self.max_pages:
                url = to_crawl.pop()
                if not self.is_allowed_domain(url) or url in crawled:
                    continue
                html = await self.fetch(session, url)
                if html:
                    pages[url] = html
                    crawled.add(url)

                    soup = BeautifulSoup(html, "html.parser")
                    domain = urlparse(url).netloc.lower()

                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if href.startswith("/"):
                            full_url = urljoin(f"https://{domain}", href)
                        elif href.startswith("http"):
                            full_url = href
                        else:
                            continue

                        if self.is_allowed_domain(full_url):
                            score = self.score_url(full_url)
                            if score >= 7:
                                if full_url not in crawled and full_url not in to_crawl:
                                    to_crawl.add(full_url)
        return pages

    def is_allowed_domain(self, url):
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return domain in self.domain_metadata and domain.endswith(".se")
