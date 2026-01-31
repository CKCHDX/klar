"""
File Utilities - File handling and I/O utilities
"""

import logging
from pathlib import Path
from typing import Any, Optional
import json
import pickle

logger = logging.getLogger(__name__)


def ensure_directory(path: Path) -> None:
    """
    Ensure directory exists, create if not
    
    Args:
        path: Directory path
    """
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Optional[Any]:
    """
    Read JSON file
    
    Args:
        path: File path
    
    Returns:
        Parsed JSON data or None
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON from {path}: {e}")
        return None


def write_json(path: Path, data: Any, indent: int = 2) -> bool:
    """
    Write JSON file
    
    Args:
        path: File path
        data: Data to write
        indent: JSON indentation
    
    Returns:
        True if successful
    """
    try:
        ensure_directory(path.parent)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to write JSON to {path}: {e}")
        return False


def read_pickle(path: Path) -> Optional[Any]:
    """
    Read pickle file
    
    Args:
        path: File path
    
    Returns:
        Unpickled data or None
    """
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        logger.error(f"Failed to read pickle from {path}: {e}")
        return None


def write_pickle(path: Path, data: Any) -> bool:
    """
    Write pickle file
    
    Args:
        path: File path
        data: Data to pickle
    
    Returns:
        True if successful
    """
    try:
        ensure_directory(path.parent)
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        return True
    except Exception as e:
        logger.error(f"Failed to write pickle to {path}: {e}")
        return False


def get_file_size_mb(path: Path) -> float:
    """
    Get file size in megabytes
    
    Args:
        path: File path
    
    Returns:
        File size in MB
    """
    if not path.exists():
        return 0.0
    return path.stat().st_size / (1024 * 1024)


def read_lines(path: Path) -> list:
    """
    Read file as lines
    
    Args:
        path: File path
    
    Returns:
        List of lines
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed to read lines from {path}: {e}")
        return []
