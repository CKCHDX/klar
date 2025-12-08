# Wikipedia Direct Article Search

## Overview
Klar finds direct Wikipedia article URLs (sv.wikipedia.org/wiki/[TOPIC]) using Wikipedia API

## How It Works

1. User: "vem ar Elon Musk"
2. Klar detects factual query
3. Extracts topic: "Elon Musk"
4. Calls Wikipedia API
5. Returns: `https://sv.wikipedia.org/wiki/Elon_Musk`

## Implementation

Add this method to SearchEngine class:

```python
def _get_wikipedia_article_url(self, topic, lang='sv'):
    try:
        if lang == 'sv':
            api = "https://sv.wikipedia.org/w/api.php"
            base = "https://sv.wikipedia.org/wiki/"
        else:
            api = "https://en.wikipedia.org/w/api.php"
            base = "https://en.wikipedia.org/wiki/"
        
        params = {'action': 'query', 'format': 'json', 'titles': topic, 'redirects': True}
        resp = self.session.get(api, params=params, timeout=5)
        pages = resp.json()['query']['pages']
        
        for pid, page in pages.items():
            if pid != '-1':
                title = page.get('title')
                if title:
                    from urllib.parse import quote
                    url = base + quote(title.replace(' ', '_'))
                    return url
    except Exception as e:
        print(f"[Wikipedia] Error: {e}")
    return None
```

## Examples

- "vem ar Elon Musk" -> sv.wikipedia.org/wiki/Elon_Musk
- "Stockholm" -> sv.wikipedia.org/wiki/Stockholm
- "vad ar AI" -> sv.wikipedia.org/wiki/Artificiell_intelligens
