"""
SVEN 1.0 - Swedish Vectorized Embedding Network
Handles semantic understanding and query expansion for Swedish content
"""
import re
from typing import List, Dict
import numpy as np

class SVEN:
    def __init__(self):
        # Swedish stop words
        self.stop_words = {
            'och', 'i', 'att', 'det', 'som', 'pÃ¥', 'Ã¤r', 'av', 'fÃ¶r',
            'den', 'med', 'till', 'om', 'har', 'de', 'ett', 'kan',
            'men', 'var', 'Ã¤n', 'sÃ¥', 'frÃ¥n', 'vid', 'eller', 'han'
        }
        
        # Swedish synonym mappings
        self.synonyms = {
            'nyheter': ['news', 'aktuellt', 'rapporter'],
            'vÃ¤der': ['weather', 'klimat', 'temperatur'],
            'sport': ['idrott', 'fotboll', 'hockey'],
            'mat': ['recept', 'matlagning', 'food'],
            'resor': ['travel', 'semester', 'turism'],
            'bostad': ['lÃ¤genhet', 'hus', 'housing'],
            'jobb': ['arbete', 'karriÃ¤r', 'anstÃ¤llning'],
            'skola': ['utbildning', 'universitet', 'education'],
            'hÃ¤lsa': ['sjukvÃ¥rd', 'medicin', 'health'],
            'ekonomi': ['finance', 'pengar', 'bank']
        }
        
        print("[SVEN] Initialized Swedish language model")
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Swedish text"""
        text = text.lower()
        text = re.sub(r'[^\w\sÃ¥Ã¤Ã¶]', ' ', text)
        tokens = [t for t in text.split() if t not in self.stop_words]
        return tokens
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Create simple embedding for query
        In production, use actual embedding model
        """
        tokens = self.tokenize(query)
        # Simple bag-of-words embedding
        embedding = np.zeros(100)
        for i, token in enumerate(tokens[:10]):
            embedding[i*10:(i+1)*10] = hash(token) % 100 / 100
        return embedding
    
    def expand_query(self, query: str) -> List[str]:
        """Expand query with synonyms and related terms"""
        tokens = self.tokenize(query)
        expanded = set(tokens)
        
        for token in tokens:
            if token in self.synonyms:
                expanded.update(self.synonyms[token])
            
            # Check reverse mappings
            for key, values in self.synonyms.items():
                if token in values:
                    expanded.add(key)
                    expanded.update(values)
        
        return list(expanded)
    
    def score_relevance(self, query: str, text: str) -> float:
        """Score text relevance to query"""
        query_tokens = set(self.tokenize(query))
        text_tokens = set(self.tokenize(text))
        
        if not query_tokens:
            return 0.0
        
        # Calculate overlap
        overlap = len(query_tokens & text_tokens)
        score = overlap / len(query_tokens)
        
        return score