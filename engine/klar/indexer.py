import re
import math
from collections import defaultdict

class BM25Indexer:
    def __init__(self, k1=1.5, b=0.75):
        self.index = defaultdict(lambda: defaultdict(int))
        self.doc_lengths = {}
        self.documents = {}
        self.snippets = {}
        self.N = 0
        self.avg_doc_len = 0
        self.k1 = k1
        self.b = b

    def tokenize(self, text):
        return re.findall(r'\w+', text.lower())

    def add_document(self, url, title, snippet, content):
        self.N += 1
        self.documents[self.N] = {"url": url, "title": title}
        self.snippets[self.N] = snippet
        tokens = self.tokenize(content)
        self.doc_lengths[self.N] = len(tokens)
        for token in tokens:
            self.index[token][self.N] += 1
        self.avg_doc_len = sum(self.doc_lengths.values()) / self.N

    def search(self, query):
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
                scores[doc_id] += score
        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {
                "url": self.documents[doc_id]["url"],
                "title": self.documents[doc_id]["title"],
                "snippet": self.snippets[doc_id],
                "score": score,
            }
            for doc_id, score in results
        ]
