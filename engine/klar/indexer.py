import re
import math
from collections import defaultdict
from urllib.parse import urlparse


class BM25Indexer:
    def __init__(self, k1=1.5, b=0.75, trusted_domains=None, trusted_boost=0.2):
        self.index = defaultdict(lambda: defaultdict(int))
        self.doc_lengths = {}
        self.documents = {}
        self.snippets = {}
        self.N = 0
        self.avg_doc_len = 0
        self.k1 = k1
        self.b = b
        self.trusted_domains = trusted_domains or set()
        self.trusted_boost = trusted_boost
        self.doc_metadata = {}
        self.cache = {}

    def tokenize(self, text):
        return re.findall(r"[a-zåäöéü]+", text.lower())

    def add_document(self, url, title, snippet, content, date=None):
        self.N += 1
        doc_id = self.N
        self.documents[doc_id] = {"url": url, "title": title}
        self.snippets[doc_id] = snippet

        tokens = self.tokenize(content)
        self.doc_lengths[doc_id] = len(tokens)

        # weighted tokens for title & snippet
        for token in self.tokenize(title):
            self.index[token][doc_id] += 3
        for token in self.tokenize(snippet):
            self.index[token][doc_id] += 2
        for token in tokens:
            self.index[token][doc_id] += 1

        self.avg_doc_len = sum(self.doc_lengths.values()) / self.N

        domain = urlparse(url).netloc.lower().replace("www.", "")
        is_trusted = domain in self.trusted_domains
        self.doc_metadata[doc_id] = {"domain": domain, "trusted": is_trusted, "date": date}

    def search(self, query, limit=10):
        if query in self.cache:
            return self.cache[query]

        query_tokens = self.tokenize(query)
        scores = defaultdict(float)

        for qtoken in query_tokens:
            postings = self.index.get(qtoken, {})
            df = len(postings)
            if df == 0:
                continue
            idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
            for doc_id, tf in postings.items():
                dl = self.doc_lengths[doc_id]
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avg_doc_len)
                score = idf * ((tf * (self.k1 + 1)) / denom)

                if self.doc_metadata[doc_id]["trusted"]:
                    score *= (1 + self.trusted_boost)

                scores[doc_id] += score

        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        formatted = [
            {
                "url": self.documents[doc_id]["url"],
                "title": self.documents[doc_id]["title"],
                "snippet": self.snippets[doc_id],
                "score": score,
            }
            for doc_id, score in results
        ]

        self.cache[query] = formatted
        return formatted
