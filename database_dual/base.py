#!/usr/bin/env python3
"""
Abstract database interface for LinkedIn data extraction
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseInterface(ABC):
    """Abstract base class for database operations"""
    
    @abstractmethod
    def initialize_database(self) -> bool:
        """Initialize the database and create necessary tables/collections"""
        pass
    
    @abstractmethod
    def store_extracted_data(self, data: List[Dict[str, str]], extraction_method: str = "traditional") -> bool:
        """Store extracted LinkedIn data"""
        pass
    
    @abstractmethod
    def store_enhanced_data(self, data: List[Dict[str, str]], extraction_method: str = "traditional+ai") -> bool:
        """Store AI-enhanced LinkedIn data"""
        pass
    
    @abstractmethod
    def get_extracted_data(self) -> List[Dict[str, str]]:
        """Retrieve all extracted data"""
        pass
    
    @abstractmethod
    def get_enhanced_data(self) -> List[Dict[str, str]]:
        """Retrieve all enhanced data"""
        pass
    
    @abstractmethod
    def clear_all_data(self) -> bool:
        """Clear all data from the database"""
        pass
    
    @abstractmethod
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        pass
    
    @abstractmethod
    def close_connection(self) -> None:
        """Close database connection"""
        pass
