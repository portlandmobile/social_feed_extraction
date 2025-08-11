#!/usr/bin/env python3
"""
Test script for the LinkedIn Data Extraction AI Agent
"""

import os
import sys
from ai_agent import LinkedInDataExtractor

def test_ai_agent():
    """Test the AI agent functionality."""
    print("🧪 Testing LinkedIn Data Extraction AI Agent...")
    print("=" * 50)
    
    # Initialize the AI agent
    try:
        agent = LinkedInDataExtractor()
        print("✅ AI Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing AI Agent: {e}")
        return False
    
    # Test with a sample file path (this won't actually process anything)
    test_file_path = "/Users/peekay/Downloads/LinkedIn_hiring _product manager_ martech_ Aug_9.mhtml"
    
    if os.path.exists(test_file_path):
        print(f"✅ Test file found: {test_file_path}")
        print("🔍 Testing file processing...")
        
        try:
            results = agent.process_mhtml_file(test_file_path)
            
            if results.get("success"):
                print(f"✅ File processed successfully!")
                print(f"📊 Extracted {len(results['extracted_data'])} posts")
                print(f"🎯 Quality score: {results['analysis']['data_quality_score']}%")
                print(f"💡 Insights: {', '.join(results['analysis']['insights'])}")
                
                # Test export functionality
                try:
                    csv_file = agent.export_to_csv(results['extracted_data'])
                    json_file = agent.export_to_json(results['extracted_data'])
                    print(f"📁 Data exported to: {csv_file} and {json_file}")
                    
                    # Clean up test files
                    if os.path.exists(csv_file):
                        os.remove(csv_file)
                    if os.path.exists(json_file):
                        os.remove(json_file)
                    print("🧹 Test export files cleaned up")
                    
                except Exception as e:
                    print(f"⚠️  Export test failed: {e}")
                
            else:
                print(f"❌ File processing failed: {results.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error processing test file: {e}")
            return False
            
    else:
        print(f"⚠️  Test file not found: {test_file_path}")
        print("📝 This is expected if you haven't downloaded the LinkedIn MHTML file yet")
        print("💡 You can still test the web interface with any MHTML file")
    
    print("=" * 50)
    print("🎉 AI Agent test completed!")
    print("🌐 To test the web interface, run: python3 start_ai_agent.py")
    print("📱 Then open http://localhost:5000 in your browser")
    
    return True

if __name__ == '__main__':
    success = test_ai_agent()
    sys.exit(0 if success else 1) 