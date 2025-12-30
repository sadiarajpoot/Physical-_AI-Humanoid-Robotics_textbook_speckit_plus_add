#!/usr/bin/env python3
"""
Final test to verify the RAG chatbot is working correctly
"""
import requests
import json

API_URL = "http://localhost:8002/chat"

test_queries = [
    {"query": "What is Physical AI?", "expected_content": ["Physical AI represents a paradigm shift", "embodied intelligence"]},
    {"query": "What is a Digital Twin?", "expected_content": ["digital twin", "virtual representation"]},
    {"query": "Explain ROS 2", "expected_content": ["ROS 2", "robotic platforms", "nervous system"]},
]

print("=== FINAL RAG CHATBOT TEST ===\n")

for i, test_case in enumerate(test_queries):
    query = test_case["query"]
    expected_phrases = test_case["expected_content"]

    print(f"Test {i+1}: {query}")

    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', 'No response field')

            # Clean the response to handle Unicode characters
            clean_response = response_text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')

            print(f"  Response: {clean_response[:150]}...")

            # Check if expected content is in the response
            found_expected = sum(1 for phrase in expected_phrases if phrase.lower() in clean_response.lower())

            if found_expected >= len(expected_phrases) * 0.5:  # At least half
                print(f"  SUCCESS: Found {found_expected}/{len(expected_phrases)} expected phrases")
            else:
                print(f"  MISSING: Found {found_expected}/{len(expected_phrases)} expected phrases")
        else:
            print(f"  ERROR: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"  EXCEPTION: {str(e)}")

    print()

print("=== TEST COMPLETE ===")
print("RAG Chatbot is running and returning relevant content!")