#!/usr/bin/env python3
"""
Firestore database implementation for LinkedIn data extraction
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.cloud import firestore
from .base import DatabaseInterface

logger = logging.getLogger(__name__)

class FirestoreDatabase(DatabaseInterface):
    """Firestore implementation of the database interface"""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize Firestore database connection"""
        try:
            # Use provided project ID or get from environment
            self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
            if not self.project_id:
                raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
            
            # Initialize Firestore client
            self.db = firestore.Client(project=self.project_id)
            self.extracted_collection = self.db.collection('extracted_data')
            self.enhanced_collection = self.db.collection('enhanced_data')
            
            logger.info(f"Firestore database initialized successfully for project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firestore database: {e}")
            raise
    
    def initialize_database(self) -> bool:
        """Initialize the database (Firestore collections are created automatically)"""
        try:
            # Test connection by getting collection references
            _ = self.extracted_collection.limit(1).stream()
            _ = self.enhanced_collection.limit(1).stream()
            
            logger.info("Firestore database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Firestore database: {e}")
            return False
    
    def store_extracted_data(self, data: List[Dict[str, str]], extraction_method: str = "traditional") -> bool:
        """Store extracted LinkedIn data"""
        try:
            batch = self.db.batch()
            
            for record in data:
                doc_ref = self.extracted_collection.document()
                doc_data = {
                    'name': record.get('Name', ''),
                    'title': record.get('Title', ''),
                    'period': record.get('Period', ''),
                    'details': record.get('Details', ''),
                    'extraction_method': extraction_method,
                    'timestamp': firestore.SERVER_TIMESTAMP
                }
                batch.set(doc_ref, doc_data)
            
            batch.commit()
            logger.info(f"Stored {len(data)} extracted records in Firestore")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store extracted data in Firestore: {e}")
            return False
    
    def store_enhanced_data(self, data: List[Dict[str, str]], extraction_method: str = "traditional+ai") -> bool:
        """Store AI-enhanced LinkedIn data"""
        try:
            batch = self.db.batch()
            
            for record in data:
                doc_ref = self.enhanced_collection.document()
                doc_data = {
                    'name': record.get('Name', ''),
                    'title': record.get('Title', ''),
                    'period': record.get('Period', ''),
                    'details': record.get('Details', ''),
                    'company': record.get('Company', ''),
                    'location': record.get('Location', ''),
                    'hiring': record.get('Hiring?', ''),
                    'extraction_method': extraction_method,
                    'timestamp': firestore.SERVER_TIMESTAMP
                }
                batch.set(doc_ref, doc_data)
            
            batch.commit()
            logger.info(f"Stored {len(data)} enhanced records in Firestore")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store enhanced data in Firestore: {e}")
            return False
    
    def get_extracted_data(self) -> List[Dict[str, str]]:
        """Retrieve all extracted data"""
        try:
            docs = self.extracted_collection.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
            
            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                data.append({
                    'Name': doc_data.get('name', ''),
                    'Title': doc_data.get('title', ''),
                    'Period': doc_data.get('period', ''),
                    'Details': doc_data.get('details', ''),
                    'extraction_method': doc_data.get('extraction_method', ''),
                    'timestamp': doc_data.get('timestamp', '')
                })
            
            logger.info(f"Retrieved {len(data)} extracted records from Firestore")
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve extracted data from Firestore: {e}")
            return []
    
    def get_enhanced_data(self) -> List[Dict[str, str]]:
        """Retrieve all enhanced data"""
        try:
            docs = self.enhanced_collection.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
            
            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                data.append({
                    'Name': doc_data.get('name', ''),
                    'Title': doc_data.get('title', ''),
                    'Period': doc_data.get('period', ''),
                    'Details': doc_data.get('details', ''),
                    'Company': doc_data.get('company', ''),
                    'Location': doc_data.get('location', ''),
                    'Hiring?': doc_data.get('hiring', ''),
                    'extraction_method': doc_data.get('extraction_method', ''),
                    'timestamp': doc_data.get('timestamp', '')
                })
            
            logger.info(f"Retrieved {len(data)} enhanced records from Firestore")
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve enhanced data from Firestore: {e}")
            return []
    
    def clear_all_data(self) -> bool:
        """Clear all data from the database"""
        try:
            # Delete extracted data
            extracted_docs = self.extracted_collection.stream()
            batch = self.db.batch()
            for doc in extracted_docs:
                batch.delete(doc.reference)
            batch.commit()
            
            # Delete enhanced data
            enhanced_docs = self.enhanced_collection.stream()
            batch = self.db.batch()
            for doc in enhanced_docs:
                batch.delete(doc.reference)
            batch.commit()
            
            logger.info("All data cleared from Firestore")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear data from Firestore: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        try:
            # Get record counts
            extracted_count = len(list(self.extracted_collection.stream()))
            enhanced_count = len(list(self.enhanced_collection.stream()))
            
            return {
                'database_type': 'Firestore',
                'project_id': self.project_id,
                'extracted_records': extracted_count,
                'enhanced_records': enhanced_count,
                'total_records': extracted_count + enhanced_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get Firestore database info: {e}")
            return {}
    
    def close_connection(self) -> None:
        """Close database connection (Firestore handles this automatically)"""
        logger.info("Firestore database connection closed")
