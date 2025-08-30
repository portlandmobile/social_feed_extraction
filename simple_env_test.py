#!/usr/bin/env python3
"""
Simple test script to verify environment variable setup
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_environment_setup():
    """Test if environment variables are properly set"""
    
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
    
    print("\n=== Current Status ===\n")
    
    if not openai_key and not gemini_key:
        print("❌ AI Enhancement is NOT available!")
        print("  - No API keys found in environment variables")
        print("  - The system will only use traditional parsing")
    else:
        print("✅ AI Enhancement is available!")
        if openai_key:
            print("  - ChatGPT enhancement ready")
        if gemini_key:
            print("  - Gemini enhancement ready")
    
    print("\n=== Setup Instructions ===\n")
    
    if not openai_key and not gemini_key:
        print("To enable AI enhancement, you need to set environment variables:")
        print("\nOption 1: Create a .env file (requires python-dotenv)")
        print("  echo 'OPENAI_API_KEY=your_openai_key_here' > .env")
        print("  echo 'GEMINI_API_KEY=your_gemini_key_here' >> .env")
        
        print("\nOption 2: Set in current terminal session")
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
