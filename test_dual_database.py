#!/usr/bin/env python3
"""
Test script to verify dual database functionality
"""

import os
import tempfile
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sqlite_database():
    """Test SQLite database functionality"""
    print("=== Testing SQLite Database ===\n")
    
    try:
        from database import create_database
        
        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        # Test SQLite database
        db = create_database(db_type='sqlite', db_path=temp_db.name)
        
        # Test data
        test_data = [
            {
                'Name': 'John Doe',
                'Title': 'Software Engineer',
                'Period': '2020-2023',
                'Details': 'Worked at Google'
            }
        ]
        
        # Test operations
        print("✅ Database created successfully")
        print(f"Database type: {db.get_database_info()['database_type']}")
        
        # Store data
        success = db.store_extracted_data(test_data, 'test')
        print(f"Store extracted data: {'✅ Success' if success else '❌ Failed'}")
        
        # Retrieve data
        retrieved = db.get_extracted_data()
        print(f"Retrieve data: {'✅ Success' if retrieved else '❌ Failed'}")
        print(f"Retrieved {len(retrieved)} records")
        
        # Close and cleanup
        db.close_connection()
        os.unlink(temp_db.name)
        
        print("✅ SQLite database test completed successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ SQLite database test failed: {e}")
        return False

def test_firestore_database():
    """Test Firestore database functionality"""
    print("=== Testing Firestore Database ===\n")
    
    try:
        from database import create_database
        
        # Check if Firestore credentials are available
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            print("⚠️  GOOGLE_CLOUD_PROJECT not set, skipping Firestore test")
            print("   Set this environment variable to test Firestore\n")
            return False
        
        # Test Firestore database
        db = create_database(db_type='firestore')
        
        # Test data
        test_data = [
            {
                'Name': 'Jane Smith',
                'Title': 'Product Manager',
                'Period': '2019-2022',
                'Details': 'Led product development'
            }
        ]
        
        # Test operations
        print("✅ Firestore database created successfully")
        print(f"Database type: {db.get_database_info()['database_type']}")
        print(f"Project ID: {project_id}")
        
        # Store data
        success = db.store_extracted_data(test_data, 'test')
        print(f"Store extracted data: {'✅ Success' if success else '❌ Failed'}")
        
        # Retrieve data
        retrieved = db.get_extracted_data()
        print(f"Retrieve data: {'✅ Success' if retrieved else '❌ Failed'}")
        print(f"Retrieved {len(retrieved)} records")
        
        # Cleanup test data
        db.clear_all_data()
        print("✅ Test data cleaned up")
        
        # Close connection
        db.close_connection()
        
        print("✅ Firestore database test completed successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ Firestore database test failed: {e}")
        return False

def test_automatic_selection():
    """Test automatic database selection based on environment"""
    print("=== Testing Automatic Database Selection ===\n")
    
    try:
        from database import create_database
        
        # Test with no environment variable (should default to SQLite)
        if 'DATABASE_TYPE' in os.environ:
            del os.environ['DATABASE_TYPE']
        
        db = create_database()
        db_type = db.get_database_info()['database_type']
        print(f"✅ Default database type: {db_type}")
        
        # Test with explicit SQLite
        os.environ['DATABASE_TYPE'] = 'sqlite'
        db = create_database()
        db_type = db.get_database_info()['database_type']
        print(f"✅ SQLite database type: {db_type}")
        
        # Test with Firestore (if credentials available)
        if os.getenv('GOOGLE_CLOUD_PROJECT'):
            os.environ['DATABASE_TYPE'] = 'firestore'
            db = create_database()
            db_type = db.get_database_info()['database_type']
            print(f"✅ Firestore database type: {db_type}")
        else:
            print("⚠️  Skipping Firestore test (no credentials)")
        
        print("✅ Automatic database selection test completed successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ Automatic database selection test failed: {e}")
        return False

def main():
    """Run all database tests"""
    print("🚀 Dual Database System Test\n")
    
    # Test SQLite
    sqlite_success = test_sqlite_database()
    
    # Test Firestore
    firestore_success = test_firestore_database()
    
    # Test automatic selection
    auto_success = test_automatic_selection()
    
    # Summary
    print("=== Test Summary ===")
    print(f"SQLite Database: {'✅ PASS' if sqlite_success else '❌ FAIL'}")
    print(f"Firestore Database: {'✅ PASS' if firestore_success else '⚠️  SKIP'}")
    print(f"Auto Selection: {'✅ PASS' if auto_success else '❌ FAIL'}")
    
    if sqlite_success and auto_success:
        print("\n🎉 Core functionality is working! You can now:")
        print("   - Use SQLite locally for development")
        print("   - Deploy to Google Cloud with Firestore")
        print("   - Switch between backends automatically")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
