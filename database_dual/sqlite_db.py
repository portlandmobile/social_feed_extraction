#!/usr/bin/env python3
"""
SQLite database implementation for LinkedIn data extraction
"""

import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import DatabaseInterface

logger = logging.getLogger(__name__)

class SQLiteDatabase(DatabaseInterface):
    """SQLite implementation of the database interface"""
    
    def __init__(self, db_path: str = "linkedin_results.db"):
        """Initialize SQLite database connection"""
        self.db_path = db_path
        self.connection = None
        self.initialize_database()
    
    def initialize_database(self) -> bool:
        """Initialize the database and create necessary tables"""
        try:
            # Create database directory if it doesn't exist
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            # Connect to database
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            self._create_tables()
            logger.info(f"SQLite database initialized successfully: {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SQLite database: {e}")
            return False
    
    def _create_tables(self):
        """Create necessary database tables"""
        cursor = self.connection.cursor()
        
        # Create extracted_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extracted_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT,
                period TEXT,
                details TEXT,
                extraction_method TEXT DEFAULT 'traditional',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create enhanced_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enhanced_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT,
                period TEXT,
                details TEXT,
                company TEXT,
                location TEXT,
                hiring TEXT,
                extraction_method TEXT DEFAULT 'traditional+ai',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add hiring column if it doesn't exist (for backward compatibility)
        try:
            cursor.execute("ALTER TABLE enhanced_data ADD COLUMN hiring TEXT")
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        self.connection.commit()
        logger.info("Database tables created successfully")
    
    def store_extracted_data(self, data: List[Dict[str, str]], extraction_method: str = "traditional") -> bool:
        """Store extracted LinkedIn data"""
        try:
            cursor = self.connection.cursor()
            
            for record in data:
                cursor.execute("""
                    INSERT INTO extracted_data (name, title, period, details, extraction_method)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    record.get('Name', ''),
                    record.get('Title', ''),
                    record.get('Period', ''),
                    record.get('Details', ''),
                    extraction_method
                ))
            
            self.connection.commit()
            logger.info(f"Stored {len(data)} extracted records")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store extracted data: {e}")
            return False
    
    def store_enhanced_data(self, data: List[Dict[str, str]], extraction_method: str = "traditional+ai") -> bool:
        """Store AI-enhanced LinkedIn data"""
        try:
            cursor = self.connection.cursor()
            
            for record in data:
                cursor.execute("""
                    INSERT INTO enhanced_data (name, title, period, details, company, location, hiring, extraction_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.get('Name', ''),
                    record.get('Title', ''),
                    record.get('Period', ''),
                    record.get('Details', ''),
                    record.get('Company', ''),
                    record.get('Location', ''),
                    record.get('Hiring?', ''),
                    extraction_method
                ))
            
            self.connection.commit()
            logger.info(f"Stored {len(data)} enhanced records")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store enhanced data: {e}")
            return False
    
    def get_extracted_data(self) -> List[Dict[str, str]]:
        """Retrieve all extracted data"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM extracted_data ORDER BY timestamp DESC")
            
            data = []
            for row in cursor.fetchall():
                data.append({
                    'Name': row['name'],
                    'Title': row['title'],
                    'Period': row['period'],
                    'Details': row['details'],
                    'extraction_method': row['extraction_method'],
                    'timestamp': row['timestamp']
                })
            
            logger.info(f"Retrieved {len(data)} extracted records")
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve extracted data: {e}")
            return []
    
    def get_enhanced_data(self) -> List[Dict[str, str]]:
        """Retrieve all enhanced data"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM enhanced_data ORDER BY timestamp DESC")
            
            data = []
            for row in cursor.fetchall():
                data.append({
                    'Name': row['name'],
                    'Title': row['title'],
                    'Period': row['period'],
                    'Details': row['details'],
                    'Company': row['company'],
                    'Location': row['location'],
                    'Hiring?': row['hiring'],
                    'extraction_method': row['extraction_method'],
                    'timestamp': row['timestamp']
                })
            
            logger.info(f"Retrieved {len(data)} enhanced records")
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve enhanced data: {e}")
            return []
    
    def clear_all_data(self) -> bool:
        """Clear all data from the database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM extracted_data")
            cursor.execute("DELETE FROM enhanced_data")
            self.connection.commit()
            logger.info("All data cleared from database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear data: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Get record counts
            cursor.execute("SELECT COUNT(*) FROM extracted_data")
            extracted_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM enhanced_data")
            enhanced_count = cursor.fetchone()[0]
            
            # Get database file size
            file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return {
                'database_type': 'SQLite',
                'database_path': self.db_path,
                'file_size_bytes': file_size,
                'extracted_records': extracted_count,
                'enhanced_records': enhanced_count,
                'total_records': extracted_count + enhanced_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {}
    
    def close_connection(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("SQLite database connection closed")
