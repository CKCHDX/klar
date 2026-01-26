"""
kse_data_serializer.py - Data Serialization for KSE

Handles serialization and deserialization of Python objects to/from
JSON and pickle formats. Supports compression and validation.

Formats:
- Pickle (binary, fast, supports complex objects)
- JSON (text, human-readable, limited to basic types)

Usage:
    >>> from kse.storage import DataSerializer
    >>> serializer = DataSerializer(format='pickle')
    >>> serialized = serializer.serialize(data)
    >>> deserialized = serializer.deserialize(serialized)

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
import pickle
import json
import gzip
from pathlib import Path
from typing import Any, Optional, Union
from datetime import datetime

from kse.core import (
    get_logger,
    KSEStorageException,
    KSEStorageCorrupted,
    STORAGE_FORMAT,
    STORAGE_COMPRESSION,
)

logger = get_logger('storage')


class DataSerializer:
    """
    Handles serialization and deserialization of data.
    
    Supports multiple formats:
    - Pickle: Binary format, fast, supports complex Python objects
    - JSON: Text format, human-readable, basic types only
    
    Optional compression using gzip.
    """
    
    SUPPORTED_FORMATS = ['pickle', 'json']
    
    def __init__(
        self,
        format: str = STORAGE_FORMAT,
        compression: bool = STORAGE_COMPRESSION,
    ):
        """
        Initialize serializer.
        
        Args:
            format: Serialization format ('pickle' or 'json')
            compression: Whether to use gzip compression
            
        Raises:
            ValueError: If format not supported
        """
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Format '{format}' not supported. "
                f"Use: {self.SUPPORTED_FORMATS}"
            )
        
        self.format = format
        self.compression = compression
        logger.debug(
            f"Serializer initialized: format={format}, "
            f"compression={compression}"
        )
    
    def serialize(self, data: Any) -> bytes:
        """
        Serialize Python object to bytes.
        
        Args:
            data: Object to serialize
            
        Returns:
            Serialized bytes
            
        Raises:
            KSEStorageException: If serialization fails
        """
        try:
            if self.format == 'pickle':
                serialized = pickle.dumps(data)
            elif self.format == 'json':
                # Convert to JSON string then to bytes
                json_str = json.dumps(data, default=str)
                serialized = json_str.encode('utf-8')
            
            if self.compression:
                serialized = gzip.compress(serialized)
            
            logger.debug(
                f"Serialized {self.format}: {len(serialized)} bytes"
            )
            return serialized
            
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            raise KSEStorageException(
                f"Failed to serialize data: {str(e)}",
                error_code="SERIALIZATION_ERROR"
            )
    
    def deserialize(self, data: bytes) -> Any:
        """
        Deserialize bytes to Python object.
        
        Args:
            data: Serialized bytes
            
        Returns:
            Deserialized object
            
        Raises:
            KSEStorageCorrupted: If data is corrupted
        """
        try:
            if self.compression:
                data = gzip.decompress(data)
            
            if self.format == 'pickle':
                return pickle.loads(data)
            elif self.format == 'json':
                json_str = data.decode('utf-8')
                return json.loads(json_str)
            
        except (pickle.UnpicklingError, json.JSONDecodeError, EOFError) as e:
            logger.error(f"Deserialization failed: {e}")
            raise KSEStorageCorrupted(
                "Unknown",
                f"Failed to deserialize: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected deserialization error: {e}")
            raise KSEStorageException(
                f"Deserialization error: {str(e)}",
                error_code="DESERIALIZATION_ERROR"
            )
    
    def save_to_file(self, data: Any, path: Union[str, Path]) -> None:
        """
        Serialize and save to file.
        
        Args:
            data: Object to save
            path: File path
            
        Raises:
            KSEStorageException: If save fails
        """
        path = Path(path)
        try:
            serialized = self.serialize(data)
            path.write_bytes(serialized)
            logger.info(f"Saved to {path}: {len(serialized)} bytes")
        except Exception as e:
            logger.error(f"Failed to save to {path}: {e}")
            raise
    
    def load_from_file(self, path: Union[str, Path]) -> Any:
        """
        Load and deserialize from file.
        
        Args:
            path: File path
            
        Returns:
            Deserialized object
            
        Raises:
            KSEStorageException: If load fails
        """
        path = Path(path)
        try:
            data = path.read_bytes()
            logger.info(f"Loaded from {path}: {len(data)} bytes")
            return self.deserialize(data)
        except Exception as e:
            logger.error(f"Failed to load from {path}: {e}")
            raise


__all__ = [
    "DataSerializer",
]
