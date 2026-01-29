"""
Hash Utilities - Hashing and checksum utilities
"""

import logging
import hashlib
from typing import Any, Optional

logger = logging.getLogger(__name__)


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """
    Hash string using specified algorithm
    
    Args:
        text: Input text
        algorithm: Hash algorithm (md5, sha1, sha256, etc.)
    
    Returns:
        Hex digest of hash
    """
    try:
        hasher = hashlib.new(algorithm)
        hasher.update(text.encode('utf-8'))
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Failed to hash string: {e}")
        return ""


def hash_url(url: str) -> str:
    """
    Generate hash for URL (for deduplication)
    
    Args:
        url: URL string
    
    Returns:
        URL hash
    """
    return hash_string(url.lower(), 'md5')


def hash_content(content: str) -> str:
    """
    Generate content hash (for change detection)
    
    Args:
        content: Content string
    
    Returns:
        Content hash
    """
    return hash_string(content, 'sha256')


def verify_hash(text: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
    """
    Verify text matches expected hash
    
    Args:
        text: Input text
        expected_hash: Expected hash value
        algorithm: Hash algorithm
    
    Returns:
        True if hash matches
    """
    actual_hash = hash_string(text, algorithm)
    return actual_hash == expected_hash


def generate_checksum(data: bytes) -> str:
    """
    Generate checksum for binary data
    
    Args:
        data: Binary data
    
    Returns:
        Checksum (MD5 hex digest)
    """
    return hashlib.md5(data).hexdigest()
