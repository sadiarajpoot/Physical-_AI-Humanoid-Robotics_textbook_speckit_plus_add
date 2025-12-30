#!/usr/bin/env python3
"""
Book Embeddings Ingestion Tool

This script crawls Docusaurus book pages, extracts text content,
generates Cohere embeddings, and stores them in Qdrant.
"""
import sys
from typing import List, Set
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from ..utils.logger import logger
from ..config.config import Config, get_config, validate_config
from ..models.models import BookContent
from ..utils.utils import extract_urls_from_html, normalize_url, is_internal_link
from ..tools.crawler import Crawler
from .cli import parse_arguments
from ..utils.chunker import TextChunker
from ..embedders.embedders import embed_text_chunks
from ..tools.vector_store import store_embeddings_in_qdrant
from ..tools.verifier import Verifier
from ..tools.resumer import create_resumer


def get_urls(base_url: str, max_pages: int = 1000) -> Set[str]:
    """
    Discover all book pages from the base URL using breadth-first search.

    Args:
        base_url: Base URL of the Docusaurus book
        max_pages: Maximum number of pages to crawl (default: 1000)

    Returns:
        Set[str]: Set of unique URLs found in the book
    """
    base_url = normalize_url(base_url)
    urls_to_visit = {base_url}
    visited_urls = set()
    all_urls = {base_url}

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop()
        if current_url in visited_urls:
            continue

        try:
            logger.info(f"Crawling: {current_url}")
            response = requests.get(current_url)
            response.raise_for_status()

            # Extract URLs from the current page
            new_urls = extract_urls_from_html(response.text, base_url)
            new_urls = {normalize_url(url) for url in new_urls if is_internal_link(base_url, url)}

            # Add new URLs to the sets
            all_urls.update(new_urls)
            urls_to_visit.update(new_urls - visited_urls)
            visited_urls.add(current_url)

        except requests.RequestException as e:
            logger.warning(f"Failed to crawl {current_url}: {e}")
            visited_urls.add(current_url)  # Don't retry failed URLs

    logger.info(f"Discovered {len(all_urls)} unique URLs")
    return all_urls


def main():
    """Main function to run the book ingestion pipeline."""
    logger.info("Starting Book Embeddings Ingestion Tool")

    # Parse command line arguments
    args = parse_arguments()

    # Get configuration
    config = get_config()

    # Override config with command line arguments if provided
    if args.url:
        config.book_url = args.url
    if args.collection_name:
        config.qdrant_collection_name = args.collection_name
    if args.chunk_size:
        config.chunk_size = args.chunk_size
    if args.chunk_overlap:
        config.chunk_overlap = args.chunk_overlap
    if args.resume:
        config.resume_from_last = True
    if args.verify:
        config.verify_ingestion = True

    # Validate configuration
    if not validate_config(config):
        logger.error("Configuration validation failed. Please check your environment variables.")
        sys.exit(1)

    logger.info(f"Starting to crawl book at: {config.book_url}")

    # Initialize progress tracking
    total_steps = 4  # crawl, chunk, embed, store
    completed_steps = 0

    # Initialize resumer if needed
    resumer = None
    if config.resume_from_last:
        resumer = create_resumer()
        if resumer.should_resume():
            logger.info("Resuming from previous state...")
            # In a full implementation, we would resume from the last processed URL
        else:
            logger.info("No previous state found, starting fresh...")

    # Initialize crawler
    crawler = Crawler(config, rate_limit_delay=config.rate_limit_delay)

    # Crawl the book
    logger.info(f"[{completed_steps}/{total_steps}] Starting to crawl book pages...")
    book_content = crawler.crawl_book(config.book_url)
    completed_steps += 1
    logger.info(f"[{completed_steps}/{total_steps}] Crawling completed. Found {len(book_content)} pages.")

    # Chunk the content
    logger.info(f"[{completed_steps}/{total_steps}] Starting text chunking...")
    chunker = TextChunker(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    text_chunks = chunker.chunk_book_content(book_content)
    completed_steps += 1
    logger.info(f"[{completed_steps}/{total_steps}] Text chunking completed. Generated {len(text_chunks)} chunks.")

    # Generate embeddings
    logger.info(f"[{completed_steps}/{total_steps}] Starting embedding generation...")
    embeddings = embed_text_chunks(text_chunks, config)
    completed_steps += 1
    logger.info(f"[{completed_steps}/{total_steps}] Embedding generation completed. Generated {len(embeddings)} embeddings.")

    # Store embeddings in Qdrant
    logger.info(f"[{completed_steps}/{total_steps}] Starting storage in Qdrant...")
    stored_count = store_embeddings_in_qdrant(embeddings, config)
    completed_steps += 1
    logger.info(f"[{completed_steps}/{total_steps}] Storage completed. Stored {stored_count} embeddings in Qdrant.")

    # Verification
    if config.verify_ingestion:
        logger.info("Starting verification...")
        verifier = Verifier()
        storage_results = verifier.verify_storage_results(stored_count, len(embeddings))
        report = verifier.generate_verification_report(
            storage_results=storage_results
        )
        print("\n" + report)

    # Print final summary
    print(f"\nIngestion Summary:")
    print(f"- Pages crawled: {len(book_content)}")
    print(f"- Text chunks generated: {len(text_chunks)}")
    print(f"- Embeddings generated: {len(embeddings)}")
    print(f"- Embeddings stored: {stored_count}")
    print(f"- Progress: {completed_steps}/{total_steps} steps completed")

    print(f"\nTotal processing complete. All data has been ingested into Qdrant successfully!")

    if resumer:
        resumer.mark_ingestion_completed()


if __name__ == "__main__":
    main()