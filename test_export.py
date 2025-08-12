#!/usr/bin/env python3
"""
Test script to verify the export functionality
"""

import requests
import json

def test_export_functionality():
    """Test the export functionality"""
    
    print("=== Testing Export Functionality ===\n")
    
    base_url = "http://localhost:5001"
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print()
    
    # Test 2: Test CSV export with small dataset
    print("2. Testing CSV export with small dataset...")
    try:
        test_data = {
            "extracted_data": [
                {
                    "Name": "John Doe",
                    "Title": "Software Engineer",
                    "Period": "2w",
                    "Details": "Looking for remote work",
                    "Company": "Test Company",
                    "Location": "Remote"
                }
            ]
        }
        
        response = requests.post(f"{base_url}/export/csv", data={"data": json.dumps(test_data)})
        if response.status_code == 200:
            print("✅ CSV export with POST works")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")
        else:
            print(f"❌ CSV export failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ CSV export error: {e}")
    
    print()
    
    # Test 3: Test JSON export with small dataset
    print("3. Testing JSON export with small dataset...")
    try:
        response = requests.post(f"{base_url}/export/json", data={"data": json.dumps(test_data)})
        if response.status_code == 200:
            print("✅ JSON export with POST works")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")
        else:
            print(f"❌ JSON export failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ JSON export error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_export_functionality()
