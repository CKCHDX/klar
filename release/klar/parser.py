from bs4 import BeautifulSoup


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string if soup.title else ""
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    text = soup.get_text(separator=" ", strip=True)
    snippet = " ".join(text.split()[:40])
    return title, snippet, text
