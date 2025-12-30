#!/usr/bin/env python3
"""
Test script to verify improved response selection in the API
"""
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from agent import qdrant_retrieval_tool

def test_query_content_matching(query):
    """Test the improved content selection logic"""
    print(f"\nTesting query: '{query}'")
    print("="*60)

    # Get the passages
    retrieval_result = qdrant_retrieval_tool(query=query)
    passages = retrieval_result.get("passages", [])

    print(f"Found {len(passages)} passages")

    if not passages:
        print("No passages found!")
        return ""

    # Apply the improved selection logic
    query_lower = query.lower()
    query_keywords = [word for word in query_lower.split() if len(word) > 2]

    best_content = ""
    best_score = 0

    print(f"Query keywords: {query_keywords}")

    # Find the most relevant passage that best matches the query
    for i, passage in enumerate(passages[:3]):  # Check top 3 passages
        content = passage.get("content", "")
        if content:
            # Clean up the content by removing problematic Unicode characters
            clean_content = content.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')

            # Calculate relevance score based on keyword matching
            content_lower = clean_content.lower()
            keyword_matches = sum(1 for keyword in query_keywords if keyword in content_lower)

            # Use a combination of similarity score and keyword relevance
            similarity_score = passage.get("similarity_score", 0.0)
            combined_score = similarity_score + (keyword_matches * 0.1)

            print(f"Passage {i+1}: Score={similarity_score:.3f}, Keywords={keyword_matches}, Combined={combined_score:.3f}")

            # Select the passage with the highest combined relevance score
            if combined_score > best_score and keyword_matches > 0:
                best_score = combined_score
                best_content = clean_content
                print(f"  -> Selected as best passage")

    # If no passage has good keyword matches, use the highest similarity passage
    if not best_content.strip():
        top_passage = passages[0]
        content = top_passage.get("content", "")
        if content:
            clean_content = content.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
            best_content = clean_content
            print("  -> Using top passage due to no keyword matches")

    # Truncate to reasonable length for focused responses
    if len(best_content) > 600:
        best_content = best_content[:600] + "..."

    print(f"\nSelected content (length: {len(best_content)}):")
    print(best_content)

    return best_content

def main():
    """Test various queries to verify improved response selection"""
    test_queries = [
        "what is Physical AI?",
        "what is module 3?",
        "how does ROS 2 work?",
        "explain humanoid robotics",
        "what is a digital twin?"
    ]

    for query in test_queries:
        test_query_content_matching(query)
        print("\n")

if __name__ == "__main__":
    main()