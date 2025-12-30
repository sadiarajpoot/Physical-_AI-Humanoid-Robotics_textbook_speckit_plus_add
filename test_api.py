#!/usr/bin/env python3
"""
Test script to verify the RAG chatbot API is working correctly
"""
import requests
import json

# Test the API with a simple query
API_URL = "http://localhost:8002/chat"

test_query = {"query": "What is Physical AI?"}

print("Testing RAG Chatbot API...")

try:
    response = requests.post(
        API_URL,
        json=test_query,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        response_text = result.get('response', 'No response field')
        # Clean the response to handle Unicode characters
        clean_response = response_text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
        print(f"SUCCESS: API is working!")
        print(f"Response: {clean_response[:200]}...")
        print(f"Status: {response.status_code}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Exception: {str(e)}")
    print("Make sure the API server is running on port 8002")

print("\nAPI Test completed!")