# Dual Database Migration Guide

## Overview

This guide explains how to migrate from the old `database.py` to the new dual database system that supports both SQLite (local development) and Firestore (Google Cloud production).

## What Changed

### Old System
- Single `database.py` file with hardcoded SQLite implementation
- Direct database calls throughout the codebase

### New System
- Modular database package with abstract interface
- Automatic backend selection based on environment variables
- Support for both SQLite and Firestore
- Same API - no code changes needed in your application logic

## File Structure

```
database/
├── __init__.py          # Package initialization
├── base.py              # Abstract database interface
├── sqlite_db.py         # SQLite implementation
├── firestore_db.py      # Firestore implementation
└── manager.py           # Automatic backend selection
```

## Environment Configuration

### Local Development (.env)
```bash
# Copy env.local to .env for local development
DATABASE_TYPE=sqlite
DATABASE_PATH=./linkedin_results.db

# AI Enhancement API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Production (Google Cloud)
```bash
# Use these settings for Google Cloud Run
DATABASE_TYPE=firestore
GOOGLE_CLOUD_PROJECT=your_google_cloud_project_id_here

# AI Enhancement API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage Examples

### Basic Usage (Recommended)
```python
from database import create_database

# Automatically selects backend based on DATABASE_TYPE environment variable
db = create_database()

# Use the same API as before
db.store_extracted_data(data)
db.store_enhanced_data(data)
results = db.get_enhanced_data()
```

### Explicit Backend Selection
```python
from database import create_database

# Force SQLite
db = create_database(db_type='sqlite', db_path='./my_db.db')

# Force Firestore
db = create_database(db_type='firestore')
```

### Database Manager (Advanced)
```python
from database import DatabaseManager

# Create manager with automatic selection
manager = DatabaseManager()
db = manager.db

# Get database info
info = manager.get_database_info()
print(f"Using: {info['selected_backend']}")
```

## Migration Steps

### 1. Update Imports
**Old:**
```python
from database import store_extracted_data, store_enhanced_data
```

**New:**
```python
from database import create_database

db = create_database()
db.store_extracted_data(data)
db.store_enhanced_data(data)
```

### 2. Update Function Calls
**Old:**
```python
store_extracted_data(data, 'traditional')
store_enhanced_data(data, 'traditional+ai')
```

**New:**
```python
db = create_database()
db.store_extracted_data(data, 'traditional')
db.store_enhanced_data(data, 'traditional+ai')
```

### 3. Update Data Retrieval
**Old:**
```python
data = get_enhanced_data()
```

**New:**
```python
db = create_database()
data = db.get_enhanced_data()
```

## Testing

### Test SQLite Locally
```bash
# Set local environment
cp env.local .env

# Test the system
python3 test_dual_database.py
```

### Test Firestore (requires Google Cloud setup)
```bash
# Set production environment
export GOOGLE_CLOUD_PROJECT=your_project_id
export DATABASE_TYPE=firestore

# Test the system
python3 test_dual_database.py
```

## Deployment

### Local Development
1. Copy `env.local` to `.env`
2. Run your application normally
3. Uses SQLite by default

### Google Cloud Run
1. Set environment variables in Cloud Run:
   - `DATABASE_TYPE=firestore`
   - `GOOGLE_CLOUD_PROJECT=your_project_id`
   - `OPENAI_API_KEY=your_key`
   - `GEMINI_API_KEY=your_key`

2. Deploy your application
3. Automatically uses Firestore

## Benefits

✅ **No Code Changes**: Same API as before  
✅ **Automatic Selection**: Switches backends based on environment  
✅ **Local Development**: Fast SQLite for development  
✅ **Production Ready**: Scalable Firestore for production  
✅ **Fallback Support**: Falls back to SQLite if Firestore fails  
✅ **Easy Testing**: Can test both backends locally  

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're importing from the new `database` package
2. **Environment Variables**: Check that `DATABASE_TYPE` is set correctly
3. **Firestore Credentials**: Ensure `GOOGLE_CLOUD_PROJECT` is set for Firestore
4. **Dependencies**: Install `google-cloud-firestore` for Firestore support

### Debug Mode

Enable debug logging to see which backend is being used:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Support

If you encounter issues:
1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Test with the provided test scripts
4. Ensure all dependencies are installed
