#!/usr/bin/env python3
"""
Comprehensive test script to verify the improved response selection in the RAG API
"""
import requests
import json

# Test the API with various queries to verify focused responses
API_URL = "http://localhost:8002/chat"

# Test queries with expected characteristics
test_queries = [
    {"query": "What is Physical AI?", "category": "definition"},
    {"query": "What is ROS 2?", "category": "definition"},
    {"query": "What is a Digital Twin?", "category": "definition"},
    {"query": "Module 1 overview", "category": "overview"},
    {"query": "Module 2 overview", "category": "overview"},
    {"query": "What are learning objectives for Week 1?", "category": "learning_objectives"},
    {"query": "Explain Gazebo simulation", "category": "explanation"},
    {"query": "What is humanoid robotics?", "category": "definition"},
]

print("Running comprehensive tests for API response quality...")

success_count = 0
total_tests = len(test_queries)

for i, test_case in enumerate(test_queries):
    query = test_case["query"]
    category = test_case["category"]
    print(f"\n--- Test {i+1}: {query} [{category}] ---")

    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', 'No response field')

            print(f"Response: {response_text[:300]}...")

            # Check if response is relevant and focused
            query_lower = query.lower()
            response_lower = response_text.lower()

            # Check if response contains relevant content
            relevant_indicators = ['is', 'are', 'means', 'refers to', 'describes', 'explains', 'overview', 'introduction', 'definition', 'concept']
            has_relevant_content = any(indicator in response_lower for indicator in relevant_indicators)

            # Check response length (should be focused, not too long)
            is_concise = len(response_text) < 500

            # Check if query terms appear in response (for relevance)
            query_words = [word for word in query_lower.split() if len(word) > 2]
            query_term_match = sum(1 for word in query_words if word in response_lower) >= max(1, len(query_words) // 2)

            if has_relevant_content and is_concise and query_term_match:
                print("SUCCESS: Response is relevant, focused, and contains query terms")
                success_count += 1
            else:
                print("PARTIAL: Response could be improved")
                print(f"   - Relevant content: {has_relevant_content}")
                print(f"   - Concise: {is_concise}")
                print(f"   - Query match: {query_term_match}")

        else:
            print(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Exception: {str(e)}")

print(f"\nComprehensive testing completed!")
print(f"Success rate: {success_count}/{total_tests} ({(success_count/total_tests)*100:.1f}%)")

if success_count >= total_tests * 0.7:  # 70% success rate
    print("OVERALL SUCCESS: Response selection improvements are effective!")
else:
    print("MIXED RESULTS: Some responses still need improvement.")