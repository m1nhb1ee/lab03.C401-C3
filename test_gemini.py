import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file")
    exit(1)

# Configure Gemini API
genai.configure(api_key=api_key)

# List available models
try:
    models = genai.list_models()
    print("Available models:")
    for model in models:
        print(f"- {model.name}")
    print()
except Exception as e:
    print("Failed to list models:", str(e))
    exit(1)

# Test the API with a simple message
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Hello, can you confirm this is working?")
    print("API Test Successful!")
    print("Response:", response.text.strip())
except Exception as e:
    print("API Test Failed!")
    print("Error:", str(e))