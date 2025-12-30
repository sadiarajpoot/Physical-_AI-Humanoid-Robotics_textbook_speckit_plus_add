#!/usr/bin/env python3
"""
Test script to directly check what content is retrieved for Module 3
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.retriever import RAGRetriever
from backend.config import get_config

def test_retrieval():
    config = get_config()
    retriever = RAGRetriever(config)

    # Test query for Module 3
    results = retriever.query_embeddings("What is module 3?", top_k=3)

    print("Retrieved results for 'What is module 3?':")
    print("=" * 50)

    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Similarity Score: {result['similarity_score']}")
        print(f"  Source URL: {result['source_url']}")
        print(f"  Content Preview: {result['content'][:300]}...")
        print(f"  Full Content Length: {len(result['content'])} characters")
        print("-" * 30)

if __name__ == "__main__":
    test_retrieval()