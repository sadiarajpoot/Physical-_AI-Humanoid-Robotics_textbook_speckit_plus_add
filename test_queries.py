#!/usr/bin/env python3
"""
Test script to verify the improved response selection in the RAG API
"""
import requests
import json

# Test the API with various queries to verify focused responses
API_URL = "http://localhost:8002/chat"

test_queries = [
    "What is Physical AI?",
    "What is ROS 2?",
    "What is Module 1 about?",
    "What is Module 2 about?",
    "Explain Gazebo simulation",
    "What are the learning objectives for Week 1?",
    "What is a Digital Twin?",
    "Explain humanoid robotics"
]

print("Testing API responses for focused content...")

for i, query in enumerate(test_queries):
    print(f"\n--- Test {i+1}: {query} ---")
    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'No response field')[:500]}...")

            # Check if response is focused and relevant
            response_text = result.get('response', '')
            if len(response_text) > 300 and query.lower() not in response_text.lower():
                print("WARNING: Response might not be focused on the query")
            else:
                print("Response appears focused")

        else:
            print(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Exception: {str(e)}")

print("\nTesting completed!")