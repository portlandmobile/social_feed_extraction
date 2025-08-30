#!/usr/bin/env python3
"""
Test script to verify AI agent creation with environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_ai_agent():
    """Test if AI agent can be created with environment variables"""
    
    print("=== AI Agent Test ===\n")
    
    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    print("Environment Variables:")
    print(f"  OPENAI_API_KEY: {'Set' if openai_key else 'Not set'}")
    print(f"  GEMINI_API_KEY: {'Set' if gemini_key else 'Not set'}")
    
    if not openai_key and not gemini_key:
        print("\n❌ No API keys found. Cannot test AI agent.")
        return
    
    print("\n=== Testing AI Agent Creation ===\n")
    
    try:
        # Import after loading environment variables
        from ai_agent import LinkedInDataExtractor
        
        # Test creating AI agent with environment variables
        agent = LinkedInDataExtractor(
            openai_api_key=openai_key,
            gemini_api_key=gemini_key
        )
        print("✅ AI Agent created successfully!")
        
        print(f"  AI Model: {agent.ai_model}")
        print(f"  OpenAI Client: {'✅ Available' if agent.openai_client else '❌ Not available'}")
        print(f"  Gemini Client: {'✅ Available' if agent.gemini_client else '❌ Not available'}")
        
        # Test AI enhancement capability
        if agent.openai_client or agent.gemini_client:
            print("\n✅ AI Enhancement is ready!")
            if agent.openai_client:
                print("  - ChatGPT enhancement available")
            if agent.gemini_client:
                print("  - Gemini enhancement available")
                
            print("\n🎯 The system should now work with AI enhancement!")
            print("   - Upload a file and select 'AI Enhancement'")
            print("   - Choose your preferred AI model")
            print("   - The system will automatically use your API keys")
        else:
            print("\n❌ AI Enhancement is NOT available!")
            print("  - Check your API keys and .env file")
            
    except Exception as e:
        print(f"❌ Error creating AI Agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_agent() 