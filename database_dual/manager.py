#!/usr/bin/env python3
"""
Database manager that automatically selects between SQLite and Firestore
"""

import os
import logging
from typing import Optional
from .base import DatabaseInterface
from .sqlite_db import SQLiteDatabase
from .firestore_db import FirestoreDatabase

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database selection based on environment"""
    
    def __init__(self, db_type: Optional[str] = None, **kwargs):
        """Initialize database manager with automatic backend selection
        
        Args:
            db_type: Force specific database type ('sqlite' or 'firestore')
            **kwargs: Additional arguments passed to the database backend
        """
        self.db_type = db_type or os.getenv('DATABASE_TYPE', 'sqlite').lower()
        self.kwargs = kwargs
        self.db: Optional[DatabaseInterface] = None
        
        # Initialize the appropriate database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the appropriate database backend"""
        try:
            if self.db_type == 'firestore':
                logger.info("Initializing Firestore database")
                self.db = FirestoreDatabase(**self.kwargs)
            else:
                logger.info("Initializing SQLite database")
                db_path = self.kwargs.get('db_path', 'linkedin_results.db')
                self.db = SQLiteDatabase(db_path=db_path)
            
            logger.info(f"Database initialized successfully: {self.db_type}")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.db_type} database: {e}")
            # Fallback to SQLite if Firestore fails
            if self.db_type == 'firestore':
                logger.info("Falling back to SQLite database")
                db_path = self.kwargs.get('db_path', 'linkedin_results.db')
                self.db = SQLiteDatabase(db_path=db_path)
            else:
                raise
    
    def get_database_info(self) -> dict:
        """Get information about the current database"""
        if self.db:
            info = self.db.get_database_info()
            info['selected_backend'] = self.db_type
            return info
        return {}
    
    def __getattr__(self, name):
        """Delegate all other method calls to the database instance"""
        if self.db and hasattr(self.db, name):
            return getattr(self.db, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def close(self):
        """Close the database connection"""
        if self.db:
            self.db.close_connection()

# Convenience function for easy database creation
def create_database(db_type: Optional[str] = None, **kwargs) -> DatabaseInterface:
    """Create a database instance with automatic backend selection
    
    Args:
        db_type: Force specific database type ('sqlite' or 'firestore')
        **kwargs: Additional arguments for the database backend
        
    Returns:
        DatabaseInterface: The appropriate database instance
    """
    manager = DatabaseManager(db_type=db_type, **kwargs)
    return manager.db
