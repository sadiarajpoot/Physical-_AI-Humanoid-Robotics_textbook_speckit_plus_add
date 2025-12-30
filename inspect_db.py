#!/usr/bin/env python3
"""
Script to inspect the content in the Qdrant vector database
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from retriever import RAGRetriever
from config import get_config

def clean_content(content):
    """Clean content by removing problematic Unicode characters"""
    return content.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')

def inspect_database_content():
    """Inspect what content is stored in the database"""
    config = get_config()
    retriever = RAGRetriever(config)

    # Perform a general search to see what kind of content we have
    print("Inspecting database content...")

    # Sample queries to understand the content structure
    sample_queries = [
        "Physical AI",
        "introduction",
        "overview",
        "ROS 2",
        "definition"
    ]

    for query in sample_queries:
        print(f"\n--- Query: '{query}' ---")
        try:
            results = retriever.query_embeddings(query, top_k=3)
            for i, result in enumerate(results):
                clean_cont = clean_content(result['content'])
                print(f"Result {i+1}:")
                print(f"  Content: {clean_cont[:300]}...")
                print(f"  Score: {result['similarity_score']}")
                print(f"  Source: {result['source_url']}")
                print()
        except Exception as e:
            print(f"Error querying for '{query}': {e}")

    # Let's also test specific queries that we know should have good answers
    print("\n--- Testing specific queries that should have direct answers ---")
    specific_queries = [
        "What is Physical AI?",
        "What is ROS 2?",
        "Module 1 overview",
        "Digital Twin definition"
    ]

    for query in specific_queries:
        print(f"\n--- Query: '{query}' ---")
        try:
            results = retriever.query_embeddings(query, top_k=3)
            for i, result in enumerate(results):
                clean_cont = clean_content(result['content'])
                print(f"Result {i+1}:")
                print(f"  Content: {clean_cont[:300]}...")
                print(f"  Score: {result['similarity_score']}")
                print(f"  Source: {result['source_url']}")
                print()
        except Exception as e:
            print(f"Error querying for '{query}': {e}")

if __name__ == "__main__":
    inspect_database_content()