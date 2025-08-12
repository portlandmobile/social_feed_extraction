#!/usr/bin/env python3
"""
Test script to verify ChatGPT and Gemini AI models work correctly
"""

import os
from ai_agent import LinkedInDataExtractor

def test_ai_models():
    """Test both AI models if API keys are available"""
    
    print("=== Testing AI Models ===\n")
    
    # Test ChatGPT
    print("1. Testing ChatGPT...")
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        try:
            agent = LinkedInDataExtractor(openai_api_key=openai_key, ai_model="chatgpt")
            print("✅ ChatGPT initialized successfully")
            print(f"   AI Model: {agent.ai_model}")
            print(f"   OpenAI Client: {'✅' if agent.openai_client else '❌'}")
            print(f"   Gemini Client: {'✅' if agent.gemini_client else '❌'}")
        except Exception as e:
            print(f"❌ ChatGPT initialization failed: {e}")
    else:
        print("⚠️  OPENAI_API_KEY not set - skipping ChatGPT test")
    
    print()
    
    # Test Gemini
    print("2. Testing Gemini...")
    gemini_key = os.getenv('GOOGLE_API_KEY')
    if gemini_key:
        try:
            agent = LinkedInDataExtractor(gemini_api_key=gemini_key, ai_model="gemini")
            print("✅ Gemini initialized successfully")
            print(f"   AI Model: {agent.ai_model}")
            print(f"   OpenAI Client: {'✅' if agent.openai_client else '❌'}")
            print(f"   Gemini Client: {'✅' if agent.gemini_client else '❌'}")
        except Exception as e:
            print(f"❌ Gemini initialization failed: {e}")
    else:
        print("⚠️  GOOGLE_API_KEY not set - skipping Gemini test")
    
    print()
    
    # Test Traditional
    print("3. Testing Traditional...")
    try:
        agent = LinkedInDataExtractor()
        print("✅ Traditional parser initialized successfully")
        print(f"   AI Model: {agent.ai_model}")
        print(f"   OpenAI Client: {'✅' if agent.openai_client else '❌'}")
        print(f"   Gemini Client: {'✅' if agent.gemini_client else '❌'}")
    except Exception as e:
        print(f"❌ Traditional initialization failed: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_ai_models()
