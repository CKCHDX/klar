#!/usr/bin/env python3
"""
DOSSNA 2.0 - Dynamic On Sight Search/Navigation Algorithm
Revolutionary Swedish Search Engine Core with SVEN, THOR, and LOKI
Complete rewrite for Swedish digital sovereignty
"""

import re
import json
import sqlite3
import numpy as np
import time
import hashlib
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
from pathlib import Path

@dataclass
class SwedishSearchContext:
    """Revolutionary Swedish search context with cultural intelligence"""
    query: str
    swedish_confidence: float = 0.0
    intent: str = "general"
    cultural_keywords: List[str] = field(default_factory=list)
    regional_context: Optional[str] = None
    seasonal_context: Optional[str] = None
    government_relevance: float = 0.0
    commercial_intent: float = 0.0
    educational_intent: float = 0.0
    emergency_intent: float = 0.0

class SVEN_SwedishEmbedding:
    """
    SVEN - Swedish Vectorized Embedding Network
    Revolutionary Swedish language AI with cultural intelligence
    """
    
    def __init__(self):
        print("🧠 Initializing SVEN - Swedish Vectorized Embedding Network...")
        
        # Core Swedish vocabulary with semantic vectors (simplified for demo)
        self.swedish_vectors = self._initialize_swedish_vectors()
        self.cultural_concepts = self._load_cultural_concepts()
        self.government_entities = self._load_government_entities()
        self.compound_patterns = self._load_compound_patterns()
        
        # Vector dimension
        self.vector_dim = 300
        
        print("✅ SVEN Swedish Language AI initialized!")
    
    def _initialize_swedish_vectors(self):
        """Initialize Swedish word vectors with cultural context"""
        return {
            # Core Swedish words
            'sverige': {'vector': np.random.rand(300), 'weight': 1.0, 'cultural': True},
            'svenska': {'vector': np.random.rand(300), 'weight': 1.0, 'cultural': True},
            'svensk': {'vector': np.random.rand(300), 'weight': 1.0, 'cultural': True},
            
            # Government terms
            'myndighet': {'vector': np.random.rand(300), 'weight': 1.2, 'authority': True},
            'kommun': {'vector': np.random.rand(300), 'weight': 1.2, 'local': True},
            'regering': {'vector': np.random.rand(300), 'weight': 1.3, 'authority': True},
            'skatt': {'vector': np.random.rand(300), 'weight': 1.2, 'government': True},
            
            # Cultural concepts (uniquely Swedish)
            'allemansrätt': {'vector': np.random.rand(300), 'weight': 1.5, 'cultural': True},
            'fika': {'vector': np.random.rand(300), 'weight': 1.3, 'cultural': True},
            'lagom': {'vector': np.random.rand(300), 'weight': 1.3, 'cultural': True},
            'jantelagen': {'vector': np.random.rand(300), 'weight': 1.2, 'cultural': True},
            'midsommar': {'vector': np.random.rand(300), 'weight': 1.4, 'seasonal': True},
            'lucia': {'vector': np.random.rand(300), 'weight': 1.3, 'seasonal': True},
            'valborg': {'vector': np.random.rand(300), 'weight': 1.2, 'seasonal': True},
            
            # Common Swedish terms
            'nyheter': {'vector': np.random.rand(300), 'weight': 1.1, 'news': True},
            'utbildning': {'vector': np.random.rand(300), 'weight': 1.1, 'education': True},
            'hälsa': {'vector': np.random.rand(300), 'weight': 1.2, 'health': True},
            'arbete': {'vector': np.random.rand(300), 'weight': 1.1, 'work': True},
            
            # Regional terms
            'stockholm': {'vector': np.random.rand(300), 'weight': 1.2, 'regional': True},
            'göteborg': {'vector': np.random.rand(300), 'weight': 1.2, 'regional': True},
            'malmö': {'vector': np.random.rand(300), 'weight': 1.2, 'regional': True},
            'norrland': {'vector': np.random.rand(300), 'weight': 1.1, 'regional': True},
        }
    
    def _load_cultural_concepts(self):
        """Load Swedish cultural concept mappings"""
        return {
            'allemansrätt': {
                'description': 'Right to roam in Swedish nature',
                'related': ['natur', 'camping', 'vandring', 'friluftsliv', 'naturvård'],
                'authority_source': 'naturvardsverket.se',
                'cultural_importance': 0.9
            },
            'fika': {
                'description': 'Swedish coffee break culture',
                'related': ['kaffe', 'paus', 'kaka', 'arbetsplats', 'kultur'],
                'cultural_importance': 0.8
            },
            'jantelagen': {
                'description': 'Cultural norm emphasizing equality and humility',
                'related': ['jämlikhet', 'ödmjukhet', 'kultur', 'samhälle'],
                'cultural_importance': 0.7
            },
            'välfärd': {
                'description': 'Swedish welfare system',
                'related': ['bidrag', 'stöd', 'trygghet', 'socialtjänst'],
                'authority_source': 'forsakringskassan.se',
                'cultural_importance': 0.9
            }
        }
    
    def _load_government_entities(self):
        """Load complete Swedish government entity knowledge"""
        return {
            # National agencies with Swedish names
            'skatteverket': {
                'domain': 'skatteverket.se',
                'authority_score': 1.0,
                'services': ['deklaration', 'skatt', 'moms', 'beskattning'],
                'contact': '0771-567 567',
                'swedish_name': 'Skatteverket'
            },
            'polisen': {
                'domain': 'polisen.se', 
                'authority_score': 1.0,
                'services': ['brott', 'säkerhet', 'pass', 'körkort'],
                'emergency': '112',
                'non_emergency': '114 14',
                'swedish_name': 'Polismyndigheten'
            },
            'försäkringskassan': {
                'domain': 'forsakringskassan.se',
                'authority_score': 1.0,
                'services': ['sjukpenning', 'föräldrapenning', 'pension', 'bidrag'],
                'contact': '0771-524 524',
                'swedish_name': 'Försäkringskassan'
            },
            'arbetsförmedlingen': {
                'domain': 'arbetsformedlingen.se',
                'authority_score': 1.0, 
                'services': ['jobb', 'arbetslöshet', 'utbildning', 'stöd'],
                'contact': '0771-60 00 00',
                'swedish_name': 'Arbetsförmedlingen'
            }
        }
    
    def _load_compound_patterns(self):
        """Load Swedish compound word patterns"""
        return {
            # Common Swedish compound word patterns
            'government_compounds': [
                r'(myndighets)([a-zåäö]+)',   # myndighetsutövning
                r'(kommun)([a-zåäö]+)',       # kommunstyrelse  
                r'(skatte)([a-zåäö]+)',       # skatteåterbäring
                r'([a-zåäö]+)(verket)',       # trafikverket
            ],
            
            'service_compounds': [
                r'(vård)([a-zåäö]+)',         # vårdcentral
                r'(sjuk)([a-zåäö]+)',         # sjukvård
                r'(arbets)([a-zåäö]+)',       # arbetslöshet
                r'(utbildnings)([a-zåäö]+)',  # utbildningsväsende
            ],
            
            'location_compounds': [
                r'(stockholm)([a-zåäö]+)',    # stockholmare
                r'(göteborg)([a-zåäö]+)',     # göteborgare
                r'(malmö)([a-zåäö]+)',        # malmöbo
            ]
        }
    
    def encode_swedish_text(self, text: str) -> np.ndarray:
        """Encode Swedish text to semantic vector with cultural context"""
        
        if not text:
            return np.zeros(self.vector_dim)
        
        text_lower = text.lower()
        word_vectors = []
        cultural_boost = 0.0
        
        # Tokenize and process words
        words = re.findall(r'[a-zåäöéü]+', text_lower)
        
        for word in words:
            # Direct match
            if word in self.swedish_vectors:
                vec_data = self.swedish_vectors[word]
                word_vectors.append(vec_data['vector'] * vec_data['weight'])
                
                # Cultural boosting
                if vec_data.get('cultural', False):
                    cultural_boost += 0.1
                    
            # Compound word handling
            else:
                compound_parts = self._split_swedish_compound(word)
                for part in compound_parts:
                    if part in self.swedish_vectors:
                        vec_data = self.swedish_vectors[part]
                        word_vectors.append(vec_data['vector'] * vec_data['weight'] * 0.8)
        
        # Calculate final vector
        if word_vectors:
            final_vector = np.mean(word_vectors, axis=0)
            # Apply cultural boost
            final_vector *= (1.0 + cultural_boost)
            return final_vector
        
        return np.zeros(self.vector_dim)
    
    def _split_swedish_compound(self, word: str) -> List[str]:
        """Split Swedish compound words intelligently"""
        
        # Check against known patterns
        for pattern_type, patterns in self.compound_patterns.items():
            for pattern in patterns:
                match = re.match(pattern, word)
                if match:
                    return list(match.groups())
        
        # Fallback: simple split for long words
        if len(word) > 8:
            mid = len(word) // 2
            return [word[:mid], word[mid:]]
        
        return [word]
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between Swedish texts"""
        
        vec1 = self.encode_swedish_text(text1)
        vec2 = self.encode_swedish_text(text2)
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)