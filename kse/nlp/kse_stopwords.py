"""
KSE Stopwords - Swedish stopword management
"""
from typing import Set
from pathlib import Path
from kse.core.kse_logger import get_logger
from kse.core.kse_constants import STOPWORDS_FILE

logger = get_logger(__name__)


class SwedishStopwords:
    """Manage Swedish stopwords"""
    
    def __init__(self, stopwords_file: Path = STOPWORDS_FILE):
        """
        Initialize stopwords manager
        
        Args:
            stopwords_file: Path to stopwords file
        """
        self.stopwords: Set[str] = set()
        self._load_stopwords(stopwords_file)
    
    def _load_stopwords(self, stopwords_file: Path) -> None:
        """Load stopwords from file"""
        try:
            if stopwords_file.exists():
                with open(stopwords_file, 'r', encoding='utf-8') as f:
                    self.stopwords = {line.strip().lower() for line in f if line.strip()}
                logger.info(f"Loaded {len(self.stopwords)} Swedish stopwords")
            else:
                logger.warning(f"Stopwords file not found: {stopwords_file}")
                self._load_default_stopwords()
        except Exception as e:
            logger.error(f"Failed to load stopwords: {e}")
            self._load_default_stopwords()
    
    def _load_default_stopwords(self) -> None:
        """Load default Swedish stopwords"""
        # Minimal set of most common Swedish stopwords
        self.stopwords = {
            'och', 'i', 'att', 'det', 'som', 'på', 'är', 'av', 'för', 'med',
            'till', 'den', 'var', 'en', 'har', 'om', 'kan', 'han', 'från', 'men',
            'de', 'ett', 'vi', 'hade', 'inte', 'vid', 'så', 'efter', 'nu', 'skulle',
            'även', 'sedan', 'då', 'alla', 'om', 'bara', 'här', 'dig', 'eller'
        }
        logger.info(f"Loaded {len(self.stopwords)} default Swedish stopwords")
    
    def is_stopword(self, word: str) -> bool:
        """
        Check if word is a stopword
        
        Args:
            word: Word to check
        
        Returns:
            True if word is a stopword
        """
        return word.lower() in self.stopwords
    
    def remove_stopwords(self, words: list) -> list:
        """
        Remove stopwords from word list
        
        Args:
            words: List of words
        
        Returns:
            List with stopwords removed
        """
        return [w for w in words if not self.is_stopword(w)]
    
    def get_stopwords(self) -> Set[str]:
        """
        Get set of stopwords
        
        Returns:
            Set of stopwords
        """
        return self.stopwords.copy()
    
    def add_stopword(self, word: str) -> None:
        """
        Add a stopword
        
        Args:
            word: Word to add
        """
        self.stopwords.add(word.lower())
    
    def remove_stopword(self, word: str) -> None:
        """
        Remove a stopword
        
        Args:
            word: Word to remove
        """
        self.stopwords.discard(word.lower())
