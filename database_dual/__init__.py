#!/usr/bin/env python3
"""
Database package for LinkedIn data extraction
Supports both SQLite (local) and Firestore (cloud) backends
"""

from .base import DatabaseInterface
from .sqlite_db import SQLiteDatabase
from .firestore_db import FirestoreDatabase
from .manager import DatabaseManager, create_database

__all__ = [
    'DatabaseInterface',
    'SQLiteDatabase', 
    'FirestoreDatabase',
    'DatabaseManager',
    'create_database'
]

# Version info
__version__ = '1.0.0'
