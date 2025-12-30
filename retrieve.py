#!/usr/bin/env python3
"""
RAG Pipeline: Retrieve extracted data and test end-to-end functionality

This script provides a command-line interface to query the Qdrant vector database
containing book embeddings, perform similarity search, and validate the accuracy
of the Physical AI & Humanoid Robotics textbook content retrieval system.
"""
import os
import sys
import argparse
import json
import time
from typing import List, Dict, Any, Optional
import logging

# Add backend to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.retrievers.retriever import RAGRetriever
from backend.utils.utils import evaluate_query_results, format_retrieved_results, aggregate_metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_test_queries(file_path: str) -> List[Dict[str, Any]]:
    """
    Load test queries from a JSON file for validation.

    Args:
        file_path: Path to the JSON file containing test queries

    Returns:
        List of test query dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('queries', []) if isinstance(data, dict) else data
    except FileNotFoundError:
        logger.error(f"Test queries file not found: {file_path}")
        return [
            {"query": "What is Physical AI?", "expected_topic": "foundations"},
            {"query": "Humanoid robotics systems", "expected_topic": "humanoid"},
            {"query": "ROS 2 fundamentals", "expected_topic": "ros"},
            {"query": "Machine learning in robotics", "expected_topic": "ml"},
            {"query": "Sensor fusion techniques", "expected_topic": "sensors"}
        ]
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in test queries file: {file_path}")
        return []


def run_end_to_end_test(retriever: RAGRetriever, num_queries: int = 5) -> Dict[str, Any]:
    """
    Run end-to-end tests with sample queries to validate the RAG pipeline.

    Args:
        retriever: Initialized RAGRetriever instance
        num_queries: Number of test queries to run

    Returns:
        Dictionary containing test results and metrics
    """
    logger.info(f"Starting end-to-end tests with {num_queries} sample queries...")

    # Sample queries covering different book modules
    sample_queries = [
        "What is Physical AI?",
        "Humanoid robotics systems and applications",
        "ROS 2 fundamentals for robotics development",
        "Machine learning in robotics intelligence",
        "Sensor fusion in humanoid robots",
        "Control systems for humanoid robots",
        "AI planning in robotics",
        "Computer vision for robotics",
        "Motion planning algorithms",
        "Human-robot interaction techniques"
    ]

    test_results = {
        "total_queries_executed": 0,
        "successful_queries": 0,
        "failed_queries": 0,
        "total_results_retrieved": 0,
        "average_similarity_score": 0.0,
        "relevance_percentage": 0.0,
        "average_response_time": 0.0,
        "detailed_results": []
    }

    total_similarity = 0.0
    total_response_time = 0.0
    successful_results = 0
    high_relevance_count = 0

    for i, query_text in enumerate(sample_queries[:num_queries], 1):
        logger.info(f"Test {i}/{num_queries}: Querying '{query_text}'")

        try:
            start_time = time.time()

            # Execute the query
            results = retriever.query_embeddings(query_text, top_k=3)

            response_time = time.time() - start_time

            test_results["total_queries_executed"] += 1
            test_results["successful_queries"] += 1
            test_results["total_results_retrieved"] += len(results)
            total_response_time += response_time

            if results:
                # Calculate average similarity score for this query
                query_avg_similarity = sum(r['similarity_score'] for r in results) / len(results) if results else 0
                total_similarity += query_avg_similarity

                # Count high relevance results (threshold of 0.3)
                high_relevance = sum(1 for r in results if r['similarity_score'] > 0.3)
                high_relevance_count += high_relevance

                successful_results += len(results)

                # Add to detailed results
                query_result = {
                    "query": query_text,
                    "results_count": len(results),
                    "average_similarity": query_avg_similarity,
                    "response_time": response_time,
                    "top_result": results[0] if results else None
                }
                test_results["detailed_results"].append(query_result)

                logger.info(f"  Retrieved {len(results)} results in {response_time:.2f}s")
                logger.info(f"  Average similarity: {query_avg_similarity:.3f}")
            else:
                logger.warning(f"  No results returned for query: {query_text}")

        except Exception as e:
            logger.error(f"Error executing query '{query_text}': {e}")
            test_results["failed_queries"] += 1

    # Calculate final metrics
    if test_results["successful_queries"] > 0:
        test_results["average_response_time"] = total_response_time / test_results["successful_queries"]

    if test_results["successful_queries"] > 0 and successful_results > 0:
        test_results["average_similarity_score"] = total_similarity / test_results["successful_queries"]
        test_results["relevance_percentage"] = (high_relevance_count / successful_results) * 100

    logger.info(f"End-to-end tests completed. Successful: {test_results['successful_queries']}/{num_queries}")
    return test_results

    # Calculate final metrics
    if test_results["successful_queries"] > 0:
        test_results["average_response_time"] = total_response_time / test_results["successful_queries"]

    if successful_results > 0:
        test_results["average_similarity_score"] = total_similarity / test_results["successful_queries"]
        test_results["relevance_percentage"] = (high_relevance_count / successful_results) * 100

    logger.info(f"End-to-end tests completed. Successful: {test_results['successful_queries']}/{num_queries}")
    return test_results


def main():
    """
    Main function to handle command-line arguments and run the retrieval tool.
    """
    parser = argparse.ArgumentParser(
        description="RAG Pipeline: Retrieve extracted book content and test end-to-end functionality"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Natural language query to search for in the book content"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of top results to retrieve (default: 5)"
    )
    parser.add_argument(
        "--filter-source-url",
        type=str,
        help="Filter results by specific source URL"
    )
    parser.add_argument(
        "--validation-mode",
        action="store_true",
        help="Run validation tests with sample queries"
    )
    parser.add_argument(
        "--test-queries-file",
        type=str,
        default="test_queries.json",
        help="Path to JSON file containing test queries for validation"
    )
    parser.add_argument(
        "--num-test-queries",
        type=int,
        default=5,
        help="Number of test queries to run in validation mode (default: 5)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Starting RAG Pipeline Retrieval Tool")

    try:
        # Initialize the RAG retriever
        logger.info("Initializing RAG Retriever...")
        retriever = RAGRetriever()
        logger.info("RAG Retriever initialized successfully")

        if args.validation_mode:
            # Run validation tests
            logger.info("Starting validation tests...")
            test_results = run_end_to_end_test(retriever, args.num_test_queries)

            print("\n" + "="*80)
            print("RAG PIPELINE VALIDATION RESULTS")
            print("="*80)
            print(f"Total queries executed: {test_results['total_queries_executed']}")
            print(f"Successful queries: {test_results['successful_queries']}")
            print(f"Failed queries: {test_results['failed_queries']}")
            print(f"Total results retrieved: {test_results['total_results_retrieved']}")
            print(f"Average response time: {test_results['average_response_time']:.2f}s")
            print(f"Average similarity score: {test_results['average_similarity_score']:.3f}")
            print(f"Relevance percentage (>0.3): {test_results['relevance_percentage']:.1f}%")

            # Success criteria check
            success_criteria_met = (
                test_results['successful_queries'] >= 5 and
                test_results['relevance_percentage'] > 80
            )

            print(f"\nSUCCESS CRITERIA: {'PASSED' if success_criteria_met else 'FAILED'}")
            print(f"- 5+ queries executed: {'✓' if test_results['successful_queries'] >= 5 else '✗'} ({test_results['successful_queries']}/5)")
            print(f"- >80% relevance achieved: {'✓' if test_results['relevance_percentage'] > 80 else '✗'} ({test_results['relevance_percentage']:.1f}%)")

            if success_criteria_met:
                print("\n🎉 RAG Pipeline validation successful!")
                print("The system meets the required success criteria.")
            else:
                print("\n⚠️  RAG Pipeline validation partially completed.")
                print("Some success criteria were not fully met.")

        elif args.query:
            # Process a single query
            logger.info(f"Processing query: '{args.query}'")

            # Prepare filters
            filters = {}
            if args.filter_source_url:
                filters["source_url"] = args.filter_source_url

            # Execute the query
            results = retriever.query_embeddings(
                query_text=args.query,
                top_k=args.top_k,
                filters=filters
            )

            # Display results
            print(f"\nQuery: '{args.query}'")
            print(f"Retrieved {len(results)} results:")
            print("-" * 80)

            for i, result in enumerate(results, 1):
                print(f"{i}. Similarity Score: {result['similarity_score']:.3f}")
                print(f"   Content: {result['content'][:200]}...")
                print(f"   Source: {result['source_url']}")
                print(f"   Chunk ID: {result['chunk_id']}")
                print(f"   Additional Metadata: {result['metadata']}")
                print()

        else:
            # No query provided, show help
            parser.print_help()
            print("\nExamples:")
            print("  python retrieve.py --query 'What is Physical AI?'")
            print("  python retrieve.py --query 'humanoid robotics' --top-k 3")
            print("  python retrieve.py --query 'introduction' --filter-source-url 'https://example.com/docs/intro'")
            print("  python retrieve.py --validation-mode --num-test-queries 10")

    except Exception as e:
        logger.error(f"Error during RAG pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()