#!/usr/bin/env python3
"""
Simple script to test Gemini API key
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API key"""
    print("\n" + "="*50)
    print("Testing GEMINI API KEY")
    print("="*50)
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY is not set or is using default value")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Simple test call
        response = model.generate_content("Describe your self", stream=False)
        print("✅ GEMINI API key is valid")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ GEMINI API key test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_gemini_api()
