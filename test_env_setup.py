#!/usr/bin/env python3
"""
Test script to verify environment variable setup for AI enhancement
"""

import os
from ai_agent import LinkedInDataExtractor

def test_environment_setup():
    """Test if environment variables are properly set and AI clients are initialized"""
    
    print("=== Environment Variable Test ===\n")
    
    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    print("Environment Variables:")
    print(f"  OPENAI_API_KEY: {'Set' if openai_key else 'Not set'}")
    if openai_key:
        print(f"    Value: {openai_key[:10]}...{openai_key[-4:]}")
    print(f"  GEMINI_API_KEY: {'Set' if gemini_key else 'Not set'}")
    if gemini_key:
        print(f"    Value: {gemini_key[:10]}...{gemini_key[-4:]}")
    
    print("\n=== AI Agent Test ===\n")
    
    # Test AI agent creation
    try:
        agent = LinkedInDataExtractor()
        print("✅ AI Agent created successfully")
        
        print(f"  AI Model: {agent.ai_model}")
        print(f"  OpenAI Client: {'✅ Available' if agent.openai_client else '❌ Not available'}")
        print(f"  Gemini Client: {'✅ Available' if agent.gemini_client else '❌ Not available'}")
        
        # Test AI enhancement capability
        if agent.openai_client or agent.gemini_client:
            print("\n✅ AI Enhancement is available!")
            if agent.openai_client:
                print("  - ChatGPT enhancement ready")
            if agent.gemini_client:
                print("  - Gemini enhancement ready")
        else:
            print("\n❌ AI Enhancement is NOT available!")
            print("  - No API keys found in environment variables")
            print("  - Set OPENAI_API_KEY and/or GEMINI_API_KEY to enable AI enhancement")
            
    except Exception as e:
        print(f"❌ Error creating AI Agent: {e}")
    
    print("\n=== Setup Instructions ===\n")
    
    if not openai_key and not gemini_key:
        print("To enable AI enhancement, you need to set environment variables:")
        print("\nOption 1: Create a .env file")
        print("  echo 'OPENAI_API_KEY=your_openai_key_here' > .env")
        print("  echo 'GEMINI_API_KEY=your_gemini_key_here' >> .env")
        
        print("\nOption 2: Set in terminal")
        print("  export OPENAI_API_KEY='your_openai_key_here'")
        print("  export GEMINI_API_KEY='your_gemini_key_here'")
        
        print("\nOption 3: Set in your shell profile (~/.zshrc, ~/.bashrc, etc.)")
        print("  echo 'export OPENAI_API_KEY=your_openai_key_here' >> ~/.zshrc")
        print("  echo 'export GEMINI_API_KEY=your_gemini_key_here' >> ~/.zshrc")
        print("  source ~/.zshrc")
        
        print("\nAfter setting environment variables, restart your terminal/IDE and run this test again.")
    else:
        print("✅ Environment variables are set! AI enhancement should work.")
        print("Test by uploading a file and selecting 'AI Enhancement' in the web interface.")

if __name__ == "__main__":
    test_environment_setup()
