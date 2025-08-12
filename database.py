#!/usr/bin/env python3
"""
Database module for LinkedIn Data Extraction AI Agent
Handles storage and retrieval of processing results
"""

import sqlite3
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import pickle

logger = logging.getLogger(__name__)

class ResultsDatabase:
    """Database manager for storing and retrieving processing results."""
    
    def __init__(self, db_path: str = "linkedin_results.db"):
        """Initialize the database connection."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processing_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        data_count INTEGER NOT NULL,
                        processing_method TEXT NOT NULL,
                        results_data BLOB,
                        results_json TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP DEFAULT (DATETIME('now', '+24 hours'))
                    )
                ''')
                
                # Create enhanced data table for AI-enhanced results
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS enhanced_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        result_id INTEGER NOT NULL,
                        name TEXT,
                        title TEXT,
                        period TEXT,
                        details TEXT,
                        company TEXT,
                        location TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (result_id) REFERENCES processing_results(id) ON DELETE CASCADE
                    )
                ''')
                
                # Create index for faster lookups
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_filename_timestamp 
                    ON processing_results(filename, timestamp)
                ''')
                
                # Create index for expiration cleanup
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_expires_at 
                    ON processing_results(expires_at)
                ''')
                
                # Create index for enhanced data lookups
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_enhanced_result_id 
                    ON enhanced_data(result_id)
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def store_results(self, filename: str, timestamp: str, data_count: int, 
                     processing_method: str, results: Dict[str, Any]) -> str:
        """Store processing results in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Store results as both pickle (for complex objects) and JSON (for metadata)
                results_pickle = pickle.dumps(results)
                results_json = json.dumps({
                    'success': results.get('success'),
                    'file_path': results.get('file_path'),
                    'data_count': len(results.get('extracted_data', [])),
                    'quality_score': results.get('analysis', {}).get('data_quality_score', 0),
                    'extraction_method': results.get('analysis', {}).get('extraction_method', 'unknown')
                })
                
                cursor.execute('''
                    INSERT INTO processing_results 
                    (filename, timestamp, data_count, processing_method, results_data, results_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (filename, timestamp, data_count, processing_method, results_pickle, results_json))
                
                result_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Results stored in database with ID: {result_id}")
                return str(result_id)
                
        except Exception as e:
            logger.error(f"Error storing results in database: {e}")
            raise
    
    def store_enhanced_data(self, result_id: str, enhanced_data: List[Dict[str, str]]) -> bool:
        """Store enhanced data (with Company and Location) in the enhanced_data table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First, clear any existing enhanced data for this result
                cursor.execute('DELETE FROM enhanced_data WHERE result_id = ?', (result_id,))
                
                # Insert the enhanced data
                for record in enhanced_data:
                    cursor.execute('''
                        INSERT INTO enhanced_data 
                        (result_id, name, title, period, details, company, location)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        result_id,
                        record.get('Name', ''),
                        record.get('Title', ''),
                        record.get('Period', ''),
                        record.get('Details', ''),
                        record.get('Company', ''),
                        record.get('Location', '')
                    ))
                
                conn.commit()
                logger.info(f"Enhanced data stored successfully for result ID: {result_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing enhanced data: {e}")
            return False
    
    def get_enhanced_data(self, result_id: str) -> Optional[List[Dict[str, str]]]:
        """Retrieve enhanced data from the enhanced_data table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT name, title, period, details, company, location
                    FROM enhanced_data 
                    WHERE result_id = ?
                    ORDER BY id
                ''', (result_id,))
                
                rows = cursor.fetchall()
                if rows:
                    enhanced_data = []
                    for row in rows:
                        name, title, period, details, company, location = row
                        enhanced_data.append({
                            'Name': name or '',
                            'Title': title or '',
                            'Period': period or '',
                            'Details': details or '',
                            'Company': company or '',
                            'Location': location or ''
                        })
                    
                    logger.info(f"Retrieved {len(enhanced_data)} enhanced records for result ID: {result_id}")
                    return enhanced_data
                else:
                    logger.warning(f"No enhanced data found for result ID: {result_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving enhanced data: {e}")
            return None
    
    def has_enhanced_data(self, result_id: str) -> bool:
        """Check if enhanced data exists for a given result ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM enhanced_data WHERE result_id = ?', (result_id,))
                count = cursor.fetchone()[0]
                
                return count > 0
                
        except Exception as e:
            logger.error(f"Error checking enhanced data: {e}")
            return False
    
    def retrieve_results(self, filename: str, timestamp: str) -> Optional[Dict[str, Any]]:
        """Retrieve processing results from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT results_data, results_json, data_count, processing_method
                    FROM processing_results 
                    WHERE filename = ? AND timestamp = ?
                    AND expires_at > DATETIME('now')
                ''', (filename, timestamp))
                
                row = cursor.fetchone()
                if row:
                    results_data, results_json, data_count, processing_method = row
                    
                    # Load the full results from pickle
                    results = pickle.loads(results_data)
                    
                    logger.info(f"Results retrieved from database: {data_count} records, method: {processing_method}")
                    return results
                else:
                    logger.warning(f"No results found for {filename} at {timestamp}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving results from database: {e}")
            return None
    
    def cleanup_expired_results(self):
        """Clean up expired results (older than 24 hours)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM processing_results 
                    WHERE expires_at < DATETIME('now')
                ''')
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired results")
                    
        except Exception as e:
            logger.error(f"Error cleaning up expired results: {e}")
    
    def get_results_summary(self) -> List[Dict[str, Any]]:
        """Get a summary of all recent results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT filename, timestamp, data_count, processing_method, results_json, created_at
                    FROM processing_results 
                    WHERE expires_at > DATETIME('now')
                    ORDER BY created_at DESC
                    LIMIT 100
                ''')
                
                rows = cursor.fetchall()
                summary = []
                
                for row in rows:
                    filename, timestamp, data_count, processing_method, results_json, created_at = row
                    metadata = json.loads(results_json) if results_json else {}
                    
                    summary.append({
                        'filename': filename,
                        'timestamp': timestamp,
                        'data_count': data_count,
                        'processing_method': processing_method,
                        'quality_score': metadata.get('quality_score', 0),
                        'extraction_method': metadata.get('extraction_method', 'unknown'),
                        'created_at': created_at
                    })
                
                return summary
                
        except Exception as e:
            logger.error(f"Error getting results summary: {e}")
            return []
    
    def delete_results(self, filename: str, timestamp: str) -> bool:
        """Delete specific results from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM processing_results 
                    WHERE filename = ? AND timestamp = ?
                ''', (filename, timestamp))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Deleted results for {filename} at {timestamp}")
                    return True
                else:
                    logger.warning(f"No results found to delete for {filename} at {timestamp}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting results: {e}")
            return False

# Global database instance
db = ResultsDatabase()

def get_database():
    """Get the global database instance."""
    return db 