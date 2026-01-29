"""
KSE Data Serializer - JSON and pickle serialization utilities
"""
import json
import pickle
from pathlib import Path
from typing import Any, Dict
from kse.core.kse_exceptions import SerializationError
from kse.core.kse_logger import get_logger

logger = get_logger(__name__)


class DataSerializer:
    """Handles serialization and deserialization of data"""
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: Path) -> None:
        """
        Save data as JSON
        
        Args:
            data: Data to save
            file_path: Path to save file
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"JSON saved to {file_path}")
        except Exception as e:
            raise SerializationError(f"Failed to save JSON to {file_path}: {e}")
    
    @staticmethod
    def load_json(file_path: Path) -> Dict[str, Any]:
        """
        Load data from JSON
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            Loaded data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"JSON loaded from {file_path}")
            return data
        except FileNotFoundError:
            logger.warning(f"JSON file not found: {file_path}")
            return {}
        except Exception as e:
            raise SerializationError(f"Failed to load JSON from {file_path}: {e}")
    
    @staticmethod
    def save_pickle(data: Any, file_path: Path) -> None:
        """
        Save data as pickle
        
        Args:
            data: Data to save
            file_path: Path to save file
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            logger.debug(f"Pickle saved to {file_path}")
        except Exception as e:
            raise SerializationError(f"Failed to save pickle to {file_path}: {e}")
    
    @staticmethod
    def load_pickle(file_path: Path) -> Any:
        """
        Load data from pickle
        
        Args:
            file_path: Path to pickle file
        
        Returns:
            Loaded data
        """
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            logger.debug(f"Pickle loaded from {file_path}")
            return data
        except FileNotFoundError:
            logger.warning(f"Pickle file not found: {file_path}")
            return None
        except Exception as e:
            raise SerializationError(f"Failed to load pickle from {file_path}: {e}")
    
    @staticmethod
    def file_exists(file_path: Path) -> bool:
        """
        Check if file exists
        
        Args:
            file_path: Path to check
        
        Returns:
            True if file exists
        """
        return file_path.exists() and file_path.is_file()
