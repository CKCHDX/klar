"""kse_text_utils.py - Text Processing Utilities

Utilities for text manipulation:
- Text cleaning
- Text truncation
- Encoding detection
- HTML stripping
"""

import logging
from typing import Optional
import re
from html import unescape

from kse.core import get_logger

logger = get_logger('utils')


class TextUtils:
    """Text processing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text for processing
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        try:
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            # Remove special characters but keep basic punctuation
            text = re.sub(r'[^\w\s\.\,\!\?\-\(\)\:]', '', text)
            
            return text.strip()
        except Exception as e:
            logger.warning(f"Failed to clean text: {e}")
            return text
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to max length
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        # Truncate and add ellipsis
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated + '...'
    
    @staticmethod
    def strip_html(html: str) -> str:
        """Remove HTML tags from text
        
        Args:
            html: HTML text
            
        Returns:
            Plain text
        """
        try:
            # Remove script and style tags
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            
            # Decode HTML entities
            text = unescape(text)
            
            return text.strip()
        except Exception as e:
            logger.warning(f"Failed to strip HTML: {e}")
            return html
    
    @staticmethod
    def extract_sentences(text: str, limit: int = None) -> list:
        """Extract sentences from text
        
        Args:
            text: Text to split
            limit: Maximum sentences
            
        Returns:
            List of sentences
        """
        try:
            # Split on sentence boundaries
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            # Filter empty
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if limit:
                sentences = sentences[:limit]
            
            return sentences
        except Exception as e:
            logger.warning(f"Failed to extract sentences: {e}")
            return [text]
    
    @staticmethod
    def highlight_text(text: str, terms: list, wrapper: str = '<mark>') -> str:
        """Highlight search terms in text
        
        Args:
            text: Text to highlight
            terms: Terms to highlight
            wrapper: Highlight wrapper (e.g., <mark> or <b>)
            
        Returns:
            Highlighted text
        """
        try:
            closing = wrapper.replace('<', '</')
            
            for term in terms:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                text = pattern.sub(f'{wrapper}{term}{closing}', text)
            
            return text
        except Exception as e:
            logger.warning(f"Failed to highlight text: {e}")
            return text


__all__ = ["TextUtils"]
