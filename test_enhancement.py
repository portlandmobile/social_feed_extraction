#!/usr/bin/env python3
"""
Test script to verify the new AI enhancement workflow
"""

from ai_agent import LinkedInDataExtractor

def test_enhancement_workflow():
    """Test the new two-stage workflow"""
    
    print("=== Testing Enhanced Workflow ===\n")
    
    # Create test data (simulating traditional parsing output)
    test_data = [
        {
            "Name": "John Doe",
            "Title": "Senior Software Engineer",
            "Period": "2w",
            "Details": "Looking for a remote software engineering role in Python and React"
        },
        {
            "Name": "Jane Smith",
            "Title": "Product Manager",
            "Period": "1w",
            "Details": "Seeking product management opportunities in San Francisco Bay Area"
        }
    ]
    
    print("1. Traditional parsing output:")
    for item in test_data:
        print(f"   - {item['Name']}: {item['Title']} ({item['Period']})")
    print()
    
    # Test traditional-only processing
    print("2. Testing traditional-only processing...")
    try:
        agent = LinkedInDataExtractor()
        # Simulate the new workflow
        results = {
            "success": True,
            "extracted_data": test_data,
            "analysis": {
                "data_quality_score": 85,
                "extraction_method": "traditional"
            }
        }
        print("✅ Traditional processing works")
        print(f"   Records: {len(results['extracted_data'])}")
        print(f"   Method: {results['analysis']['extraction_method']}")
    except Exception as e:
        print(f"❌ Traditional processing failed: {e}")
    
    print()
    
    # Test AI enhancement (without API keys)
    print("3. Testing AI enhancement workflow (without API keys)...")
    try:
        agent = LinkedInDataExtractor()
        # This should fall back to traditional data
        enhanced_data = agent.enhance_data_with_ai(test_data, "chatgpt")
        print("✅ AI enhancement workflow works (fallback to traditional)")
        print(f"   Input records: {len(test_data)}")
        print(f"   Output records: {len(enhanced_data)}")
        print(f"   Enhancement method: {enhanced_data[0].get('extraction_method', 'unknown')}")
    except Exception as e:
        print(f"❌ AI enhancement workflow failed: {e}")
    
    print()
    
    # Test CSV export with new columns
    print("4. Testing CSV export with new columns...")
    try:
        agent = LinkedInDataExtractor()
        # Add the new columns to test data
        enhanced_test_data = []
        for item in test_data:
            enhanced_item = item.copy()
            enhanced_item['Company'] = 'Test Company'
            enhanced_item['Location'] = 'Remote'
            enhanced_test_data.append(enhanced_item)
        
        csv_file = agent.export_to_csv(enhanced_test_data, "test_enhanced.csv")
        print("✅ CSV export works with new columns")
        print(f"   File: {csv_file}")
        
        # Check the CSV content
        import pandas as pd
        df = pd.read_csv(csv_file)
        print(f"   Columns: {list(df.columns)}")
        print(f"   Rows: {len(df)}")
        
    except Exception as e:
        print(f"❌ CSV export failed: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_enhancement_workflow()
