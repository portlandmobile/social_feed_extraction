#!/usr/bin/env python3
"""
Test script to verify the new export system
"""

import requests
import json
import pandas as pd

def test_new_export_system():
    """Test the new export system that creates content directly"""
    
    print("=== Testing New Export System ===\n")
    
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
    
    # Test 2: Test CSV export with new system
    print("2. Testing CSV export with new system...")
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
                },
                {
                    "Name": "Jane Smith",
                    "Title": "Product Manager",
                    "Period": "1w",
                    "Details": "Seeking opportunities in SF",
                    "Company": "Tech Corp",
                    "Location": "San Francisco"
                }
            ]
        }
        
        response = requests.post(f"{base_url}/export/csv", data={"data": json.dumps(test_data)})
        if response.status_code == 200:
            print("✅ CSV export works with new system")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            # Verify CSV content
            csv_content = response.content.decode('utf-8')
            print(f"   CSV Content Preview: {csv_content[:100]}...")
            
            # Check if it has the right columns
            if "Name,Title,Period,Details,Company,Location" in csv_content:
                print("✅ CSV has correct column headers")
            else:
                print("❌ CSV missing expected columns")
                
        else:
            print(f"❌ CSV export failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ CSV export error: {e}")
    
    print()
    
    # Test 3: Test JSON export with new system
    print("3. Testing JSON export with new system...")
    try:
        response = requests.post(f"{base_url}/export/json", data={"data": json.dumps(test_data)})
        if response.status_code == 200:
            print("✅ JSON export works with new system")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            # Verify JSON content
            json_content = response.content.decode('utf-8')
            print(f"   JSON Content Preview: {json_content[:100]}...")
            
            # Check if it's valid JSON
            try:
                parsed_json = json.loads(json_content)
                print(f"✅ JSON is valid, contains {len(parsed_json)} records")
            except json.JSONDecodeError:
                print("❌ JSON is not valid")
                
        else:
            print(f"❌ JSON export failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ JSON export error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_new_export_system()
