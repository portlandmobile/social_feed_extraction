#!/usr/bin/env python3
"""
Debug script to test dotenv loading
"""

import os
from dotenv import load_dotenv

print("=== Before load_dotenv() ===")
print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
print(f"GEMINI_API_KEY: {'Set' if os.getenv('GEMINI_API_KEY') else 'Not set'}")

print("\n=== Loading .env file ===")
result = load_dotenv()
print(f"load_dotenv() result: {result}")

print("\n=== After load_dotenv() ===")
print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
if os.getenv('OPENAI_API_KEY'):
    print(f"  Value: {os.getenv('OPENAI_API_KEY')[:10]}...{os.getenv('OPENAI_API_KEY')[-4:]}")
print(f"GEMINI_API_KEY: {'Set' if os.getenv('GEMINI_API_KEY') else 'Not set'}")
if os.getenv('GEMINI_API_KEY'):
    print(f"  Value: {os.getenv('GEMINI_API_KEY')[:10]}...{os.getenv('GEMINI_API_KEY')[-4:]}")

print("\n=== Current working directory ===")
print(f"Current directory: {os.getcwd()}")

print("\n=== .env file check ===")
env_file = ".env"
if os.path.exists(env_file):
    print(f".env file exists: {os.path.exists(env_file)}")
    print(f".env file size: {os.path.getsize(env_file)} bytes")
    print(f".env file readable: {os.access(env_file, os.R_OK)}")
else:
    print(f".env file does not exist in current directory")
