"""
Encoding Utilities - Encoding and decoding utilities
"""

import logging
from typing import Optional
import base64

logger = logging.getLogger(__name__)


def encode_base64(text: str) -> str:
    """
    Encode text to base64
    
    Args:
        text: Input text
    
    Returns:
        Base64 encoded string
    """
    try:
        encoded = base64.b64encode(text.encode('utf-8'))
        return encoded.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encode base64: {e}")
        return ""


def decode_base64(encoded: str) -> Optional[str]:
    """
    Decode base64 to text
    
    Args:
        encoded: Base64 encoded string
    
    Returns:
        Decoded text or None
    """
    try:
        decoded = base64.b64decode(encoded.encode('utf-8'))
        return decoded.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decode base64: {e}")
        return None


def safe_decode(data: bytes, encodings: list = None) -> Optional[str]:
    """
    Safely decode bytes trying multiple encodings
    
    Args:
        data: Bytes to decode
        encodings: List of encodings to try
    
    Returns:
        Decoded string or None
    """
    if encodings is None:
        encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
    
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            continue
    
    logger.warning("Failed to decode data with any encoding")
    return None


def normalize_encoding(text: str) -> str:
    """
    Normalize text encoding (fix common issues)
    
    Args:
        text: Input text
    
    Returns:
        Normalized text
    """
    # Encode to UTF-8 and decode back to fix encoding issues
    try:
        return text.encode('utf-8', errors='ignore').decode('utf-8')
    except Exception as e:
        logger.warning(f"Failed to normalize encoding: {e}")
        return text
