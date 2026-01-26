"""
kse/nlp/__init__.py - Swedish Natural Language Processing API

Components:
  - NLPCore: Main coordinator
  - Tokenizer: Swedish tokenization
  - Lemmatizer: Swedish lemmatization
  - CompoundHandler: Compound word handling
  - StopwordManager: Stopword management
  - EntityExtractor: Named entity recognition
  - IntentDetector: Query intent classification
  - QueryExpander: Query expansion & synonyms
  - SentimentAnalyzer: Sentiment analysis
  - LanguageDetector: Language detection

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from .kse_nlp_core import NLPCore, KSENLPException
from .kse_tokenizer import Tokenizer
from .kse_lemmatizer import Lemmatizer
from .kse_compound_handler import CompoundHandler
from .kse_stopwords import StopwordManager
from .kse_entity_extractor import EntityExtractor
from .kse_intent_detector import IntentDetector
from .kse_query_expander import QueryExpander
from .kse_sentiment_analyzer import SentimentAnalyzer
from .kse_language_detector import LanguageDetector

__all__ = [
    # Core
    "NLPCore",
    
    # Tokenization & Lemmatization
    "Tokenizer",
    "Lemmatizer",
    "CompoundHandler",
    
    # Filtering
    "StopwordManager",
    
    # Entity & Intent
    "EntityExtractor",
    "IntentDetector",
    
    # Query Processing
    "QueryExpander",
    
    # Sentiment & Language
    "SentimentAnalyzer",
    "LanguageDetector",
    
    # Exceptions
    "KSENLPException",
]

__version__ = "1.0.0"
__author__ = "Klar Development Team"


# Quick start examples
"""
QUICK START - NLP Layer

1. Full text processing:
    from kse.nlp import NLPCore
    
    nlp = NLPCore()
    result = nlp.process_text('Svenska text här')
    print(result['tokens'])
    print(result['entities'])

2. Tokenization:
    from kse.nlp import Tokenizer
    
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize('Hej världen! Det är en fin dag.')

3. Lemmatization:
    from kse.nlp import Lemmatizer
    
    lemmatizer = Lemmatizer()
    lemmas = lemmatizer.lemmatize(['hundar', 'springer'])

4. Stopwords:
    from kse.nlp import StopwordManager
    
    stopwords = StopwordManager()
    filtered = stopwords.remove_stopwords(tokens)

5. Entity extraction:
    from kse.nlp import EntityExtractor
    
    extractor = EntityExtractor()
    entities = extractor.extract('Anna bor i Stockholm')

6. Query expansion:
    from kse.nlp import QueryExpander
    
    expander = QueryExpander()
    expanded = expander.expand('bil')

7. Sentiment analysis:
    from kse.nlp import SentimentAnalyzer
    
    analyzer = SentimentAnalyzer()
    score = analyzer.analyze('Det var fantastiskt!')

ARCHITECTURE:

kse/nlp/
├── kse_nlp_core.py             Main orchestrator
├── kse_tokenizer.py            Tokenization
├── kse_lemmatizer.py           Lemmatization
├── kse_compound_handler.py     Compound words
├── kse_stopwords.py            Stopwords
├── kse_entity_extractor.py     Named entities
├── kse_intent_detector.py      Intent classification
├── kse_query_expander.py       Query expansion
├── kse_sentiment_analyzer.py   Sentiment
├── kse_language_detector.py    Language detection
└── __init__.py                 Public API

INTEGRATION:

- Phase 4 (crawler): Uses NLP to process crawled content
- Phase 6 (indexing): Uses NLP for document processing
- Phase 8 (search): Uses NLP for query processing

FEATURES:

Swedish Language Support:
  - Tokenization with abbreviation handling
  - Lemmatization with Swedish rules
  - Compound word handling (Swedi sh connector 's/e')
  - 45+ Swedish stopwords

Text Analysis:
  - Named entity extraction
  - Sentiment analysis (positive/negative/neutral)
  - Language detection (Swedish/English/German)
  - Intent classification (search/product/question/navigation)

Query Processing:
  - Query expansion with synonyms
  - Intent detection
  - Stopword removal
"""
