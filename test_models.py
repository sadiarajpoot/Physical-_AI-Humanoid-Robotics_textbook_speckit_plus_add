#!/usr/bin/env python3
"""
Test script to check available Gemini models
"""
import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

# Configure with API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not found in environment")
    exit(1)

genai.configure(api_key=api_key)

# List available models
try:
    print("Available models:")
    for model in genai.list_models():
        print(f"- {model.name}")
        # Check if the model supports generateContent
        if 'generateContent' in model.supported_generation_methods:
            print(f"  Supports generateContent: Yes")
        else:
            print(f"  Supports generateContent: No")
        print()
except Exception as e:
    print(f"Error listing models: {e}")