#!/usr/bin/env python3
"""
Test script to directly test the qdrant_retrieval_tool function
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from agent import qdrant_retrieval_tool

print("Testing qdrant_retrieval_tool directly...")

result = qdrant_retrieval_tool("What is Physical AI?")

print(f"Retrieval result: {result}")
print(f"Number of passages: {len(result.get('passages', []))}")

if result.get('passages'):
    for i, passage in enumerate(result['passages']):
        print(f"Passage {i+1}:")
        print(f"  Content: {passage.get('content', '')[:200]}...")
        print(f"  Score: {passage.get('similarity_score', 0.0)}")
        print(f"  Source: {passage.get('source_url', '')}")
        print()

if result.get('error'):
    print(f"Error: {result['error']}")