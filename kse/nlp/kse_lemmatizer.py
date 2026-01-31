"""
KSE Lemmatizer - Swedish lemmatization engine
"""
from typing import Dict
from kse.core.kse_logger import get_logger

logger = get_logger(__name__)


class SwedishLemmatizer:
    """Lemmatize Swedish words to their base forms"""
    
    def __init__(self):
        """Initialize lemmatizer"""
        # Swedish suffix rules for basic lemmatization
        # Maps suffix -> replacement
        self.suffix_rules = {
            # Plural nouns
            'arna': 'a',     # flickorna -> flicka
            'erna': 'e',     # pojkerna -> pojke
            'orna': 'o',     # bilorna -> bilo (rare)
            'na': '',        # husen -> hus
            'ar': '',        # flickar -> flicka
            'er': '',        # pojker -> pojke
            'or': '',        # bilar -> bil
            
            # Definite forms
            'en': '',        # bilen -> bil
            'et': '',        # huset -> hus
            'an': '',        # flickan -> flicka
            'n': '',         # hus + n -> hus
            
            # Verbs
            'ade': 'a',      # pratade -> prata
            'ande': 'a',     # pratande -> prata
            'ad': 'a',       # pratad -> prata
            'at': 'a',       # pratat -> prata
            'ar': 'a',       # pratar -> prata
            'er': 'a',       # springer -> springa
            'de': '',        # gjorde -> gör
            'te': '',        # satte -> sätt
            't': '',         # gjort -> gjor
            
            # Adjectives
            'are': '',       # större -> stor
            'ast': '',       # största -> stor
            'a': '',         # stora -> stor
            'e': '',         # store -> stor
        }
        
        # Common irregular forms (manual mapping)
        self.irregular_forms: Dict[str, str] = {
            'är': 'vara',
            'var': 'vara',
            'varit': 'vara',
            'har': 'ha',
            'hade': 'ha',
            'haft': 'ha',
            'gå': 'gå',
            'går': 'gå',
            'gick': 'gå',
            'gått': 'gå',
            'kom': 'komma',
            'kommer': 'komma',
            'kommit': 'komma',
            'säger': 'säga',
            'sa': 'säga',
            'sade': 'säga',
            'sagt': 'säga',
            'vet': 'veta',
            'visste': 'veta',
            'vetat': 'veta',
        }
    
    def lemmatize(self, word: str) -> str:
        """
        Lemmatize a Swedish word
        
        Args:
            word: Word to lemmatize
        
        Returns:
            Lemmatized word
        """
        if not word:
            return word
        
        word = word.lower()
        
        # Check irregular forms first
        if word in self.irregular_forms:
            return self.irregular_forms[word]
        
        # Don't lemmatize very short words (3 characters or less)
        # These are often proper nouns, abbreviations, or already lemmatized
        if len(word) <= 3:
            return word
        
        # Apply suffix rules
        # Try longest suffixes first
        for suffix, replacement in sorted(self.suffix_rules.items(), 
                                         key=lambda x: len(x[0]), 
                                         reverse=True):
            if word.endswith(suffix) and len(word) > len(suffix):
                lemma = word[:-len(suffix)] + replacement
                # Ensure result is valid (at least 3 characters to avoid over-stemming)
                if len(lemma) >= 3:
                    return lemma
        
        # Return original if no rule matched
        return word
    
    def lemmatize_tokens(self, tokens: list) -> list:
        """
        Lemmatize a list of tokens
        
        Args:
            tokens: List of tokens
        
        Returns:
            List of lemmatized tokens
        """
        return [self.lemmatize(token) for token in tokens]
    
    def add_irregular_form(self, word: str, lemma: str) -> None:
        """
        Add an irregular form
        
        Args:
            word: Word form
            lemma: Base form
        """
        self.irregular_forms[word.lower()] = lemma.lower()
