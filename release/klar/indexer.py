import re
import math
import pickle
import time
from collections import defaultdict, Counter
from urllib.parse import urlparse
import threading

class SuperFastBM25Indexer:
    """
    Super-fast BM25 indexer optimized for Swedish content
    Fixes the issues with domain coverage beyond news sites
    """
    
    def __init__(self, k1=1.8, b=0.75, trusted_domains=None, trusted_boost=0.3):
        self.index = defaultdict(lambda: defaultdict(float))
        self.doc_lengths = {}
        self.documents = {}
        self.snippets = {}
        self.N = 0
        self.avg_doc_len = 0
        self.k1 = k1  # Increased for Swedish compound words
        self.b = b
        self.trusted_domains = trusted_domains or set()
        self.trusted_boost = trusted_boost
        self.doc_metadata = {}
        self.cache = {}
        
        # Enhanced Swedish language support
        self.swedish_stopwords = self._load_swedish_stopwords()
        self.swedish_synonyms = self._load_swedish_synonyms()
        self.domain_boosts = self._setup_domain_boosts()
        
        # Thread safety
        self.lock = threading.RLock()
        
    def _load_swedish_stopwords(self):
        """Comprehensive Swedish stopwords"""
        return {
            'och', 'i', 'att', 'det', 'som', 'på', 'är', 'av', 'för', 'den',
            'till', 'en', 'har', 'de', 'med', 'var', 'sig', 'om', 'från', 
            'vid', 'så', 'han', 'hon', 'eller', 'inte', 'ett', 'man', 'kan',
            'ska', 'skulle', 'vara', 'blir', 'då', 'få', 'får', 'hade', 'här',
            'när', 'där', 'över', 'under', 'mycket', 'samma', 'andra', 'alla',
            'bara', 'första', 'stora', 'egen', 'nya', 'gamla', 'små', 'inom',
            'utan', 'mellan', 'efter', 'genom', 'sedan', 'medan', 'både'
        }
    
    def _load_swedish_synonyms(self):
        """Swedish synonyms and related terms for better search coverage"""
        return {
            # News and information
            'nyheter': ['nyhet', 'aktuellt', 'senaste', 'rapporter', 'information'],
            'nyhet': ['nyheter', 'rapport', 'artikel', 'meddelande'],
            
            # Government and authorities  
            'myndighet': ['myndigheter', 'regering', 'stat', 'offentlig'],
            'skatt': ['beskattning', 'skatten', 'avgift', 'moms'],
            'kommun': ['kommunal', 'stad', 'municipal'],
            
            # Commerce and shopping
            'köpa': ['köp', 'handel', 'handla', 'shopping', 'inköp'],
            'sälja': ['sälj', 'försäljning', 'marknadsplats', 'annons'],
            'bil': ['bilar', 'fordon', 'auto', 'motorfordon'],
            'pris': ['priser', 'kostnad', 'avgift', 'belopp'],
            
            # Education and work
            'jobb': ['arbete', 'anställning', 'karriär', 'yrke', 'tjänst'],
            'utbildning': ['skola', 'universitet', 'kurs', 'studier'],
            'forskning': ['vetenskap', 'studie', 'forskare', 'akademisk'],
            
            # Places and locations
            'stockholm': ['huvudstad', 'sthlm'],
            'göteborg': ['gbg', 'götet'], 
            'malmö': ['malmoe'],
            
            # Technology and digital
            'dator': ['datorer', 'pc', 'computer', 'teknologi'],
            'internet': ['webb', 'online', 'digital', 'nätet']
        }
    
    def _setup_domain_boosts(self):
        """Domain-specific relevance boosts for different query types"""
        return {
            # Government queries boost government domains
            'government_terms': {
                'terms': ['skatt', 'myndighet', 'regering', 'offentlig', 'kommun', 'stat'],
                'domains': ['skatteverket.se', 'regeringen.se', 'polisen.se', 'forsakringskassan.se'],
                'boost': 1.5
            },
            
            # News queries boost news domains  
            'news_terms': {
                'terms': ['nyhet', 'senaste', 'aktuellt', 'politik', 'ekonomi'],
                'domains': ['svt.se', 'dn.se', 'aftonbladet.se', 'expressen.se', 'svd.se'],
                'boost': 1.4
            },
            
            # Commerce queries boost commerce domains
            'commerce_terms': {
                'terms': ['köp', 'sälj', 'pris', 'handel', 'bil', 'hus', 'annons'],
                'domains': ['blocket.se', 'tradera.com', 'prisjakt.nu', 'ica.se'],
                'boost': 1.3
            },
            
            # Education queries boost educational domains
            'education_terms': {
                'terms': ['utbildning', 'universitet', 'skola', 'kurs', 'forskning'],
                'domains': ['kth.se', 'uu.se', 'lu.se', 'su.se', 'liu.se'],
                'boost': 1.3
            },
            
            # Local queries boost city domains
            'local_terms': {
                'terms': ['kommun', 'stad', 'tjänster', 'evenemang'],
                'domains': ['stockholm.se', 'goteborg.se', 'malmo.se'],
                'boost': 1.2
            }
        }
    
    def enhanced_tokenize(self, text):
        """Enhanced tokenization for Swedish with compound word handling"""
        if not text:
            return []
        
        # Basic tokenization with Swedish characters
        tokens = re.findall(r'[a-zåäöéüA-ZÅÄÖÉÜ]+', text.lower())
        
        # Remove stopwords and short tokens
        tokens = [t for t in tokens if len(t) > 2 and t not in self.swedish_stopwords]
        
        # Handle compound words (common in Swedish)
        enhanced_tokens = []
        for token in tokens:
            enhanced_tokens.append(token)
            
            # Split long words that might be compounds
            if len(token) > 8:
                mid = len(token) // 2
                part1, part2 = token[:mid], token[mid:]
                if len(part1) > 3 and len(part2) > 3:
                    enhanced_tokens.extend([part1, part2])
        
        return enhanced_tokens
    
    def add_document(self, url, title, snippet, content, date=None):
        """Add document with enhanced Swedish processing"""
        with self.lock:
            self.N += 1
            doc_id = self.N
            
            self.documents[doc_id] = {"url": url, "title": title}
            self.snippets[doc_id] = snippet or content[:200] + "..."
            
            # Enhanced tokenization
            title_tokens = self.enhanced_tokenize(title)
            snippet_tokens = self.enhanced_tokenize(snippet or "")
            content_tokens = self.enhanced_tokenize(content)
            
            all_tokens = title_tokens + snippet_tokens + content_tokens
            self.doc_lengths[doc_id] = len(all_tokens)
            
            # Weighted indexing with higher title boost
            for token in title_tokens:
                self.index[token][doc_id] += 5.0  # Strong title boost
            
            for token in snippet_tokens:
                self.index[token][doc_id] += 3.0  # Meta description boost
            
            for token in content_tokens:
                self.index[token][doc_id] += 1.0  # Base content weight
            
            # Add synonyms for better coverage
            for token in title_tokens + snippet_tokens:
                if token in self.swedish_synonyms:
                    for synonym in self.swedish_synonyms[token][:2]:  # Limit to top 2
                        self.index[synonym][doc_id] += 2.0
            
            self.avg_doc_len = sum(self.doc_lengths.values()) / self.N
            
            # Domain and content metadata
            domain = urlparse(url).netloc.lower().replace("www.", "")
            is_trusted = domain in self.trusted_domains
            
            # Swedish content detection
            full_text = f"{title} {snippet} {content}"
            swedish_score = self._calculate_swedish_score(full_text)
            
            self.doc_metadata[doc_id] = {
                "domain": domain, 
                "trusted": is_trusted, 
                "date": date,
                "swedish_score": swedish_score,
                "content_type": self._classify_content_type(title, content)
            }
    
    def _calculate_swedish_score(self, text):
        """Calculate how Swedish the content is (0.0 to 1.0)"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Swedish character frequency
        swedish_chars = len(re.findall(r'[åäö]', text_lower))
        char_ratio = swedish_chars / max(len(text) * 0.01, 1)
        
        # Swedish word indicators
        swedish_indicators = ['och', 'att', 'för', 'på', 'är', 'som', 'sverige', 'svenska', 'kronor']
        word_matches = sum(1 for word in swedish_indicators if word in text_lower)
        word_ratio = word_matches / len(swedish_indicators)
        
        # Combined score
        return min((char_ratio * 0.4 + word_ratio * 0.6), 1.0)
    
    def _classify_content_type(self, title, content):
        """Classify content type for better relevance"""
        text = (title + " " + content).lower()
        
        if any(word in text for word in ['nyhet', 'rapport', 'aktuellt', 'senaste']):
            return 'news'
        elif any(word in text for word in ['köp', 'sälj', 'pris', 'handel', 'butik']):
            return 'commerce'
        elif any(word in text for word in ['myndighet', 'kommun', 'regering', 'offentlig']):
            return 'government'
        elif any(word in text for word in ['utbildning', 'universitet', 'kurs', 'forskning']):
            return 'education'
        else:
            return 'general'
    
    def enhanced_search(self, query, limit=10):
        """Enhanced search with Swedish optimizations and domain boosting"""
        if query in self.cache:
            return self.cache[query]
        
        query_tokens = self.enhanced_tokenize(query)
        if not query_tokens:
            return []
        
        # Expand query with synonyms
        expanded_tokens = query_tokens.copy()
        for token in query_tokens:
            if token in self.swedish_synonyms:
                expanded_tokens.extend(self.swedish_synonyms[token][:2])
        
        scores = defaultdict(float)
        
        # BM25 scoring with enhancements
        for qtoken in set(expanded_tokens):  # Remove duplicates
            postings = self.index.get(qtoken, {})
            df = len(postings)
            if df == 0:
                continue
            
            # Enhanced IDF calculation
            idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
            
            for doc_id, tf in postings.items():
                dl = self.doc_lengths[doc_id]
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avg_doc_len)
                score = idf * ((tf * (self.k1 + 1)) / denom)
                
                # Apply various boosts
                metadata = self.doc_metadata[doc_id]
                
                # Trusted domain boost
                if metadata["trusted"]:
                    score *= (1 + self.trusted_boost)
                
                # Swedish content boost
                score *= (1 + metadata["swedish_score"] * 0.2)
                
                # Domain-specific boosts based on query
                score *= self._get_domain_boost(query, metadata["domain"])
                
                # Content type relevance
                if qtoken in query_tokens:  # Original query terms get higher weight
                    score *= 1.2
                
                scores[doc_id] += score
        
        # Sort and format results
        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        formatted = []
        for doc_id, score in results:
            doc = self.documents[doc_id]
            metadata = self.doc_metadata[doc_id]
            
            formatted.append({
                "url": doc["url"],
                "title": doc["title"],
                "snippet": self._generate_enhanced_snippet(doc_id, query_tokens),
                "score": score,
                "domain": metadata["domain"],
                "content_type": metadata["content_type"],
                "swedish_score": metadata["swedish_score"]
            })
        
        self.cache[query] = formatted
        return formatted
    
    def _get_domain_boost(self, query, domain):
        """Get domain-specific boost based on query content"""
        query_lower = query.lower()
        
        for category, config in self.domain_boosts.items():
            # Check if query contains relevant terms
            if any(term in query_lower for term in config['terms']):
                # Check if domain should be boosted for this query type
                if domain in config['domains']:
                    return config['boost']
        
        return 1.0  # No boost
    
    def _generate_enhanced_snippet(self, doc_id, query_tokens):
        """Generate enhanced snippet with query highlighting"""
        snippet = self.snippets[doc_id]
        
        # Highlight query terms (simple approach)
        for token in query_tokens:
            if len(token) > 3:  # Only highlight meaningful terms
                pattern = re.compile(re.escape(token), re.IGNORECASE)
                snippet = pattern.sub(f"**{token}**", snippet)
        
        return snippet
    
    def get_document_count(self):
        """Get total number of indexed documents"""
        return self.N
    
    def get_cache_data(self):
        """Get data for caching to disk"""
        return {
            'index': dict(self.index),
            'doc_lengths': self.doc_lengths,
            'documents': self.documents,
            'snippets': self.snippets,
            'doc_metadata': self.doc_metadata,
            'N': self.N,
            'avg_doc_len': self.avg_doc_len
        }
    
    def load_from_cache(self, cache_data):
        """Load index from cached data"""
        self.index = defaultdict(lambda: defaultdict(float), cache_data['index'])
        self.doc_lengths = cache_data['doc_lengths']
        self.documents = cache_data['documents']
        self.snippets = cache_data['snippets'] 
        self.doc_metadata = cache_data['doc_metadata']
        self.N = cache_data['N']
        self.avg_doc_len = cache_data['avg_doc_len']
    
    def get_stats(self):
        """Get comprehensive indexer statistics"""
        content_types = Counter(meta['content_type'] for meta in self.doc_metadata.values())
        domains = Counter(meta['domain'] for meta in self.doc_metadata.values())
        
        return {
            'total_documents': self.N,
            'total_terms': len(self.index),
            'avg_doc_length': self.avg_doc_len,
            'cache_size': len(self.cache),
            'content_types': dict(content_types),
            'top_domains': dict(domains.most_common(10)),
            'swedish_documents': sum(1 for meta in self.doc_metadata.values() 
                                   if meta['swedish_score'] > 0.5)
        }