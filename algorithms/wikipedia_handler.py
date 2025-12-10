"""
Wikipedia Handler 1.0 - Specialized algorithm for Wikipedia searches
Handles Swedish (sv.wikipedia) and English (en.wikipedia) Wikipedia
Optimized for encyclopedia/factual/definition queries
ENHANCED: Single-word topic detection, proper capitalization handling
FEATURES:
  - Direct article URL retrieval via Wikipedia API
  - Search suggestion fallback
  - Category/section extraction
  - Language negotiation (Swedish primary, English fallback)
  - Query normalization for Wikipedia API
  - Infobox data extraction
  - Disambiguation handling
  - Smart single-word query detection
"""

import requests
import json
import re
from typing import Optional, List, Dict, Tuple
from urllib.parse import quote
import time


class WikipediaHandler:
    """
    Specialized handler for Wikipedia search queries
    NOT treated like regular domains - has its own explicit algorithm
    """
    
    def __init__(self, timeout: float = 5.0, retry_attempts: int = 2):
        self.sv_api = "https://sv.wikipedia.org/w/api.php"
        self.en_api = "https://en.wikipedia.org/w/api.php"
        self.sv_base = "https://sv.wikipedia.org/wiki/"
        self.en_base = "https://en.wikipedia.org/wiki/"
        
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Cache for recent searches
        self.search_cache = {}  # topic -> (url, timestamp)
        self.cache_ttl = 3600  # 1 hour
        
        # Common encyclopedia topics (for single-word detection)
        self.wikipedia_topics = {
            # Countries
            'sverige', 'stockholm', 'göteborg', 'malmö', 'uppsala', 'uppsala', 'västerås',
            'deutschland', 'germany', 'frankrike', 'france', 'italien', 'italy', 'japan', 'japan',
            'usa', 'usa', 'australien', 'australia', 'brasilien', 'brazil', 'mexico', 'méxico',
            'kanada', 'canada', 'indien', 'india', 'kina', 'china', 'spanien', 'spain',
            'norge', 'norway', 'denmark', 'danmark', 'finland', 'finland', 'polen', 'poland',
            
            # Cities
            'paris', 'london', 'tokyo', 'beijing', 'moscow', 'dubai', 'ny', 'new york',
            'chicago', 'los angeles', 'toronto', 'vancouver', 'sydney', 'melbourne', 'auckland',
            'berlin', 'rome', 'madrid', 'barcelona', 'amsterdam', 'istanbul', 'bangkok',
            
            # Technology/Science
            'python', 'javascript', 'java', 'csharp', 'c++', 'rust', 'golang',
            'quantum', 'dna', 'gravity', 'relativity', 'photosynthesis', 'evolution',
            'ai', 'machine learning', 'neural network', 'algorithm', 'blockchain',
            'electricity', 'magnetism', 'radioactivity', 'atom', 'molecule',
            
            # Famous people (partial list)
            'einstein', 'newton', 'curie', 'tesla', 'darwin', 'hawking',
            'einstein', 'galileo', 'newton', 'kepler', 'copernicus',
            'shakespeare', 'dante', 'cervantes', 'tolstoy', 'dostoevsky',
            
            # Health/Medicine
            'covid', 'vaccination', 'cancer', 'diabetes', 'alzheimer', 'autism',
            'depression', 'schizophrenia', 'bipolar', 'anxiety', 'ocd',
            'heart disease', 'stroke', 'pneumonia', 'influenza', 'measles',
            
            # History
            'world war', 'second world war', 'first world war', 'french revolution',
            'renaissance', 'enlightenment', 'industrial revolution', 'cold war',
            'american revolution', 'crusades', 'black plague',
            
            # General concepts
            'wikipedia', 'internet', 'computer', 'smartphone', 'television',
            'music', 'art', 'literature', 'philosophy', 'religion',
            'economics', 'politics', 'psychology', 'sociology', 'anthropology',
        }
        
        print("[Wikipedia Handler] Initialized - Swedish/English Wikipedia support")
        print("[Wikipedia Handler] Features: Direct URL retrieval, search fallback, disambiguation handling")
        print("[Wikipedia Handler] ENHANCED: Single-word topic detection")
    
    def is_wikipedia_query(self, query: str) -> bool:
        """
        Detect if query is suitable for Wikipedia search
        
        Handles three patterns:
        1. EXPLICIT FACTUAL: 'vem är X', 'vad är Y', 'var ligger Z', definitions
        2. SINGLE-WORD TOPICS: Common encyclopedia topics (capitalized or known)
        3. MULTI-WORD ENCYCLOPEDIA: Person names, place names, concepts with proper nouns
        """
        query_lower = query.lower().strip()
        
        # Pattern 1: EXPLICIT FACTUAL QUESTIONS
        factual_patterns = [
            r'^(vem|who)\s+(är|is)',           # Who is
            r'^(vad|what)\s+(är|is)',          # What is
            r'^(var|where)\s+(är|is|ligger)',  # Where is/lies
            r'^(när|when)\s+(är|is|var)',      # When is/was
            r'^(hur|how)\s+(många|much|many)', # How many/much
            r'biografi',                        # Biography
            r'definition',                      # Definition
            r'förklaring',                      # Explanation
        ]
        
        for pattern in factual_patterns:
            if re.search(pattern, query_lower):
                print(f"[Wikipedia] Detected factual question pattern")
                return True
        
        # Pattern 2: SINGLE-WORD TOPICS
        words = query.strip().split()
        if len(words) == 1:
            word_lower = words[0].lower()
            
            # Check against known Wikipedia topics
            if word_lower in self.wikipedia_topics:
                print(f"[Wikipedia] Detected single-word topic: '{word_lower}'")
                return True
            
            # Check if proper noun (starts with capital + length > 3)
            if len(words[0]) > 3 and words[0][0].isupper():
                print(f"[Wikipedia] Detected proper noun topic: '{words[0]}'")
                return True
        
        # Pattern 3: MULTI-WORD TOPICS
        # If contains capital letters (proper nouns) or known concepts
        if len(words) >= 2:
            # Check if has proper nouns (multiple capital letters)
            capital_count = sum(1 for word in words if word and word[0].isupper())
            if capital_count >= 1:  # At least one proper noun
                print(f"[Wikipedia] Detected multi-word proper noun: '{query}'")
                return True
            
            # Check against topic list
            phrase_lower = query_lower
            for topic in self.wikipedia_topics:
                if topic in phrase_lower:
                    print(f"[Wikipedia] Detected known topic in phrase: '{query}'")
                    return True
        
        return False
    
    def _is_encyclopedia_concept(self, query: str) -> bool:
        """
        Check if query is likely an encyclopedia topic
        (person, place, concept, event, technology, etc.)
        """
        query_lower = query.lower()
        
        for topic in self.wikipedia_topics:
            if topic in query_lower:
                return True
        
        return False
    
    def normalize_topic(self, topic: str) -> str:
        """
        Normalize topic for Wikipedia API
        - Remove question words (vem är, vad är, var, etc.)
        - Clean punctuation
        - Trim whitespace
        - Capitalize first letter (Wikipedia convention)
        """
        topic_clean = topic.strip()
        
        # Remove Swedish question words
        question_words = [
            'vem är', 'vem', 'vad är', 'vad', 
            'var är', 'var ligger', 'var',
            'när är', 'när', 'hur många', 'hur',
            'vilken', 'vilket',
        ]
        
        # Remove English question words
        question_words.extend([
            'who is', 'who', 'what is', 'what',
            'where is', 'where', 'when is', 'when',
            'which', 'how many', 'how',
        ])
        
        for qword in question_words:
            if topic_clean.lower().startswith(qword.lower()):
                topic_clean = topic_clean[len(qword):].strip()
        
        # Remove punctuation
        topic_clean = topic_clean.strip("?,!\"'•.;:-()[]{}&")
        topic_clean = topic_clean.strip()
        
        # Wikipedia convention: capitalize first letter
        if topic_clean and len(topic_clean) > 0:
            topic_clean = topic_clean[0].upper() + topic_clean[1:]
        
        return topic_clean
    
    def search_direct(self, topic: str, lang: str = 'sv') -> Optional[str]:
        """
        MAIN ALGORITHM: Search for direct article URL
        
        Process:
        1. Normalize topic for Wikipedia API
        2. Query Wikipedia API with title search
        3. Handle redirects automatically
        4. Return direct article URL or None
        
        lang: 'sv' for Swedish Wikipedia, 'en' for English
        """
        if lang == 'sv':
            api_url = self.sv_api
            base_url = self.sv_base
            lang_name = "Swedish Wikipedia"
        else:
            api_url = self.en_api
            base_url = self.en_base
            lang_name = "English Wikipedia"
        
        # Normalize topic
        topic_clean = self.normalize_topic(topic)
        
        if not topic_clean or len(topic_clean) < 2:
            print(f"[Wikipedia] Topic too short after normalization: '{topic}'")
            return None
        
        print(f"[Wikipedia] Searching {lang_name} for: '{topic_clean}'")
        
        # Try direct API call with retries
        for attempt in range(self.retry_attempts):
            try:
                # Wikipedia API: Query action
                params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': topic_clean,
                    'redirects': True,  # Auto-follow redirects
                    'formatversion': 2,
                    'prop': 'info',
                    'inprop': 'url',
                }
                
                response = self.session.get(
                    api_url, 
                    params=params, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract article from response
                pages = data.get('query', {}).get('pages', [])
                
                if not pages:
                    print(f"[Wikipedia] No pages found for '{topic_clean}'")
                    return self._search_fallback(topic_clean, lang)
                
                # Get first page (should be the matching article)
                page = pages[0]
                
                # Check if article exists (has 'missing' key means it doesn't exist)
                if 'missing' in page:
                    print(f"[Wikipedia] Article does not exist: '{topic_clean}'")
                    return self._search_fallback(topic_clean, lang)
                
                # Get the canonical title (handles redirects)
                title = page.get('title')
                if not title:
                    print(f"[Wikipedia] No title in response for '{topic_clean}'")
                    return self._search_fallback(topic_clean, lang)
                
                # Build direct URL
                article_url = base_url + quote(title.replace(' ', '_'), safe='/')
                
                print(f"[Wikipedia] ✓ Found article: '{title}'")
                print(f"[Wikipedia] URL: {article_url}")
                
                return article_url
                
            except requests.exceptions.Timeout:
                print(f"[Wikipedia] Timeout on attempt {attempt + 1}/{self.retry_attempts}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(0.5)  # Brief delay before retry
                continue
            
            except requests.exceptions.RequestException as e:
                print(f"[Wikipedia] Request error on attempt {attempt + 1}/{self.retry_attempts}: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(0.5)
                continue
            
            except json.JSONDecodeError:
                print(f"[Wikipedia] Invalid JSON response on attempt {attempt + 1}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(0.5)
                continue
            
            except Exception as e:
                print(f"[Wikipedia] Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(0.5)
                continue
        
        # All retries failed, try fallback
        return self._search_fallback(topic_clean, lang)
    
    def _search_fallback(self, topic: str, lang: str = 'sv') -> Optional[str]:
        """
        FALLBACK ALGORITHM: If direct search fails, use search/suggest API
        Returns closest matching article or None
        """
        if lang == 'sv':
            api_url = self.sv_api
            base_url = self.sv_base
            lang_name = "Swedish Wikipedia"
        else:
            api_url = self.en_api
            base_url = self.en_base
            lang_name = "English Wikipedia"
        
        print(f"[Wikipedia] Fallback: Using search API for '{topic}'")
        
        try:
            # Use search API to find suggestions
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': topic,
                'srnamespace': 0,  # Only main namespace
                'srlimit': 5,
                'formatversion': 2,
            }
            
            response = self.session.get(
                api_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get('query', {}).get('search', [])
            
            if not search_results:
                print(f"[Wikipedia] No search results for '{topic}'")
                return None
            
            # Get first search result
            first_result = search_results[0]
            result_title = first_result.get('title')
            
            if not result_title:
                return None
            
            # Build URL from search result
            article_url = base_url + quote(result_title.replace(' ', '_'), safe='/')
            
            print(f"[Wikipedia] Fallback found: '{result_title}'")
            print(f"[Wikipedia] URL: {article_url}")
            
            return article_url
        
        except Exception as e:
            print(f"[Wikipedia] Fallback search failed: {e}")
            return None
    
    def search_with_fallback(self, topic: str) -> Optional[str]:
        """
        SMART FALLBACK: Try Swedish Wikipedia first, then English
        Returns first successful result or None
        """
        # Try Swedish Wikipedia first (default for Swedish queries)
        sv_result = self.search_direct(topic, lang='sv')
        if sv_result:
            return sv_result
        
        # Fallback to English Wikipedia
        print(f"[Wikipedia] Swedish not found, trying English Wikipedia")
        en_result = self.search_direct(topic, lang='en')
        if en_result:
            return en_result
        
        # Both failed
        print(f"[Wikipedia] ✗ Article not found in Swedish or English Wikipedia: '{topic}'")
        return None
    
    def extract_infobox_data(self, topic: str, lang: str = 'sv') -> Optional[Dict]:
        """
        Extract structured infobox data from Wikipedia article
        Useful for getting facts/summary about a person/place
        """
        if lang == 'sv':
            api_url = self.sv_api
        else:
            api_url = self.en_api
        
        try:
            topic_clean = self.normalize_topic(topic)
            
            # Query for page content
            params = {
                'action': 'query',
                'format': 'json',
                'titles': topic_clean,
                'prop': 'extracts',
                'exintro': True,  # Just intro section
                'explaintext': True,  # Plain text (no HTML)
                'formatversion': 2,
            }
            
            response = self.session.get(
                api_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', [])
            if pages:
                intro = pages[0].get('extract', '')
                return {
                    'intro': intro[:500],  # First 500 chars
                    'lang': lang,
                    'title': pages[0].get('title'),
                }
        
        except Exception as e:
            print(f"[Wikipedia] Could not extract infobox: {e}")
        
        return None
    
    def get_search_results(self, topic: str, lang: str = 'sv', limit: int = 5) -> List[Dict]:
        """
        Get multiple Wikipedia search results (not just the top one)
        Useful for disambiguation pages or showing alternatives
        """
        if lang == 'sv':
            api_url = self.sv_api
            base_url = self.sv_base
        else:
            api_url = self.en_api
            base_url = self.en_base
        
        results = []
        
        try:
            topic_clean = self.normalize_topic(topic)
            
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': topic_clean,
                'srnamespace': 0,
                'srlimit': limit,
                'formatversion': 2,
            }
            
            response = self.session.get(
                api_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get('query', {}).get('search', [])
            
            for result in search_results:
                title = result.get('title')
                if title:
                    results.append({
                        'title': title,
                        'url': base_url + quote(title.replace(' ', '_'), safe='/'),
                        'snippet': result.get('snippet', ''),
                        'lang': lang,
                    })
        
        except Exception as e:
            print(f"[Wikipedia] Error getting search results: {e}")
        
        return results
    
    def is_disambiguation_page(self, topic: str, lang: str = 'sv') -> bool:
        """
        Check if article is a disambiguation page
        These list multiple meanings of a term
        """
        if lang == 'sv':
            api_url = self.sv_api
        else:
            api_url = self.en_api
        
        try:
            topic_clean = self.normalize_topic(topic)
            
            params = {
                'action': 'query',
                'format': 'json',
                'titles': topic_clean,
                'prop': 'categories',
                'formatversion': 2,
            }
            
            response = self.session.get(
                api_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', [])
            if pages:
                categories = pages[0].get('categories', [])
                for cat in categories:
                    cat_title = cat.get('title', '').lower()
                    if 'disambiguation' in cat_title:
                        return True
        
        except Exception as e:
            print(f"[Wikipedia] Error checking disambiguation: {e}")
        
        return False
    
    def clear_cache(self):
        """Clear search cache"""
        self.search_cache.clear()
        print("[Wikipedia] Cache cleared")
