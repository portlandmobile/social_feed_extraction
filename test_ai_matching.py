#!/usr/bin/env python3
"""
Test script to debug AI enhancement Name field matching
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_ai_matching():
    """Test AI enhancement with a small dataset to debug matching"""
    
    print("=== AI Enhancement Matching Test ===\n")
    
    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    print("Environment Variables:")
    print(f"  OPENAI_API_KEY: {'Set' if openai_key else 'Not set'}")
    print(f"  GEMINI_API_KEY: {'Set' if gemini_key else 'Not set'}")
    
    if not openai_key and not gemini_key:
        print("\n❌ No API keys found. Cannot test AI enhancement.")
        return
    
    print("\n=== Testing AI Enhancement ===\n")
    
    try:
        # Import after loading environment variables
        from ai_agent import LinkedInDataExtractor
        
        # Create AI agent
        agent = LinkedInDataExtractor(
            openai_api_key=openai_key,
            gemini_api_key=gemini_key
        )
        
        print("✅ AI Agent created successfully!")
        
        # Create a small test dataset
        test_data = [
            {
                'Name': 'John Doe',
                'Title': 'Software Engineer',
                'Period': '2020-2023',
                'Details': 'Worked at Google in Mountain View, CA. Remote work available.'
            },
            {
                'Name': 'Jane Smith',
                'Title': 'Product Manager',
                'Period': '2019-2022',
                'Details': 'Led product development at Microsoft in Seattle, WA.'
            },
            {
                'Name': 'Bob Johnson',
                'Title': 'Data Scientist',
                'Period': '2021-2024',
                'Details': 'Analyzed data at Amazon. Remote position.'
            }
        ]
        
        print(f"Test data created: {len(test_data)} records")
        print("Sample record:", test_data[0])
        
        # Test AI enhancement
        print("\n--- Testing Gemini Enhancement ---")
        enhanced_data = agent._enhance_with_gemini(test_data)
        
        if enhanced_data:
            print("✅ Gemini enhancement successful!")
            print(f"Enhanced data count: {len(enhanced_data)}")
            print(f"Enhanced data fields: {list(enhanced_data[0].keys()) if enhanced_data else 'None'}")
            print(f"Sample enhanced record: {enhanced_data[0] if enhanced_data else 'None'}")
            
            # Test merging
            print("\n--- Testing Data Merging ---")
            merged_data = agent._merge_ai_enhancement_with_original(test_data, enhanced_data)
            print(f"Merged data count: {len(merged_data)}")
            print(f"Sample merged record: {merged_data[0] if merged_data else 'None'}")
            
        else:
            print("❌ Gemini enhancement failed")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_matching()
