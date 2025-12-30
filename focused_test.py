#!/usr/bin/env python3
"""
Focused test script to verify the improved response selection in the RAG API
"""
import requests
import json

# Test the API with specific queries to verify focused responses
API_URL = "http://localhost:8002/chat"

# Test queries that should have clear, direct answers in the database
test_queries = [
    {"query": "What is Physical AI?", "expected_content": ["Physical AI represents a paradigm shift", "embodied intelligence", "physical world"]},
    {"query": "What is ROS 2?", "expected_content": ["ROS 2 is built around", "Nodes:", "Topics:", "Messages:"]},
    {"query": "What is a Digital Twin?", "expected_content": ["A digital twin is a virtual representation", "real-time data", "understanding, prediction, optimization"]},
]

print("Testing API responses for focused, direct answers...")

for i, test_case in enumerate(test_queries):
    query = test_case["query"]
    expected_phrases = test_case["expected_content"]
    print(f"\n--- Test {i+1}: {query} ---")

    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', 'No response field')
            print(f"Response: {response_text[:500]}...")

            # Check if the response contains expected content
            response_lower = response_text.lower()
            found_expected = sum(1 for phrase in expected_phrases if phrase.lower() in response_lower)

            if found_expected >= len(expected_phrases) * 0.5:  # At least half of expected phrases
                print(f"SUCCESS: Found {found_expected}/{len(expected_phrases)} expected phrases")
            else:
                print(f"PARTIAL: Found {found_expected}/{len(expected_phrases)} expected phrases")

            # Check response length and focus
            if len(response_text) < 300:
                print("Response length is appropriate (concise)")
            else:
                print("Response might be too long")

        else:
            print(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Exception: {str(e)}")

print("\nFocused testing completed!")