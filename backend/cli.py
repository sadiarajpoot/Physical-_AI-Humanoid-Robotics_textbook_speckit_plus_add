import argparse
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the book ingestion CLI.

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Tool to crawl Docusaurus book pages, generate Cohere embeddings, and store in Qdrant"
    )

    # Main arguments
    parser.add_argument(
        "--url",
        type=str,
        help="Base URL of the Docusaurus book to crawl (overrides BOOK_URL env var)"
    )

    parser.add_argument(
        "--collection-name",
        type=str,
        help="Name of the Qdrant collection to use (overrides QDRANT_COLLECTION_NAME env var)"
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Size of text chunks for embedding (default: 1000)"
    )

    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between text chunks (default: 200)"
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last completed step"
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify ingestion results after completion"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually storing embeddings"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--config-file",
        type=str,
        help="Path to configuration file (default: .env)"
    )

    return parser


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = create_parser()
    return parser.parse_args()


def print_usage() -> None:
    """
    Print usage information.
    """
    parser = create_parser()
    parser.print_help()


if __name__ == "__main__":
    # Example usage
    args = parse_arguments()
    print(f"Parsed arguments: {args}")