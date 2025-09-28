import asyncio
import aiohttp
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class DynamicCrawler:
    def __init__(self, domain_metadata, max_pages=20):
        self.domain_metadata = domain_metadata
        self.max_pages = max_pages

    async def fetch(self, session, url):
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200 and "text/html" in resp.headers.get("Content-Type", ""):
                    return await resp.text()
        except Exception as e:
            print(f"Failed {url}: {e}")
        return None

    def is_allowed_domain(self, url):
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return domain in self.domain_metadata

    async def find_seeds(self, query):
        query_tokens = [t.lower() for t in query.split() if t]
        seeds = []
        for domain, keywords in self.domain_metadata.items():
            if any(q in domain or q in keyword for q in query_tokens for keyword in keywords):
                seeds.append(f"https://{domain}")
        if not seeds:
            seeds = list(self.domain_metadata.keys())[:3]
            seeds = [f"https://{d}" for d in seeds]
        print(f"Seeds for query '{query}': {seeds}")
        return seeds

    async def crawl(self, seeds):
        pages = {}
        async with aiohttp.ClientSession() as session:
            for url in seeds[:self.max_pages]:
                if not self.is_allowed_domain(url):
                    continue
                print(f"Crawling {url}")
                html = await self.fetch(session, url)
                if html:
                    pages[url] = html
                else:
                    print(f"Failed {url}")
        return pages

    async def get_domain_links(self, domain):
        """Fetch root page and extract subpage links for navigation"""
        url = f"https://{domain}"
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, url)
            links = []
            if html:
                soup = BeautifulSoup(html, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a.get("href")
                    if href.startswith("/"):
                        full_url = f"https://{domain}{href}"
                    elif href.startswith("http") and domain in href:
                        full_url = href
                    else:
                        continue
                    title = a.get_text(strip=True) or full_url
                    links.append({"url": full_url, "title": title})
            return html, links
