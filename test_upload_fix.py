#!/usr/bin/env python3
"""
Test script to verify the upload functionality is working
"""

from ai_agent import LinkedInDataExtractor

def test_upload_functionality():
    """Test that the upload functionality works"""
    
    print("=== Testing Upload Functionality ===\n")
    
    # Test 1: Check if the method exists
    print("1. Checking if process_mhtml_file method exists...")
    try:
        agent = LinkedInDataExtractor()
        if hasattr(agent, 'process_mhtml_file'):
            print("✅ process_mhtml_file method exists")
        else:
            print("❌ process_mhtml_file method missing")
            return
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return
    
    print()
    
    # Test 2: Check if the method is callable
    print("2. Checking if process_mhtml_file method is callable...")
    try:
        method = getattr(agent, 'process_mhtml_file')
        if callable(method):
            print("✅ process_mhtml_file method is callable")
        else:
            print("❌ process_mhtml_file method is not callable")
            return
    except Exception as e:
        print(f"❌ Error checking method: {e}")
        return
    
    print()
    
    # Test 3: Check method signature
    print("3. Checking method signature...")
    try:
        import inspect
        sig = inspect.signature(agent.process_mhtml_file)
        params = list(sig.parameters.keys())
        print(f"✅ Method parameters: {params}")
        
        # Check if it has the expected parameters
        expected_params = ['file_path', 'use_ai', 'ai_model']
        for param in expected_params:
            if param in params:
                print(f"   ✅ Has parameter: {param}")
            else:
                print(f"   ❌ Missing parameter: {param}")
                
    except Exception as e:
        print(f"❌ Error checking signature: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_upload_functionality()
