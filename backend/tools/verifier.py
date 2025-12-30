from typing import List, Dict, Set
from models import BookContent
from logger import logger


class Verifier:
    """
    A class to verify the ingestion process and check completeness.
    """
    def __init__(self):
        pass

    def verify_crawling_results(self, crawled_content: List[BookContent], expected_urls: Set[str] = None) -> Dict[str, any]:
        """
        Verify that crawling was completed successfully.

        Args:
            crawled_content: List of BookContent objects from crawling
            expected_urls: Set of URLs that were expected to be crawled

        Returns:
            Dict: Verification results with statistics and issues
        """
        results = {
            'total_pages_crawled': len(crawled_content),
            'pages_with_content': 0,
            'pages_without_content': 0,
            'pages_with_title': 0,
            'pages_without_title': 0,
            'total_content_length': 0,
            'issues': [],
            'success': True
        }

        for content in crawled_content:
            if content.content and len(content.content.strip()) > 0:
                results['pages_with_content'] += 1
                results['total_content_length'] += len(content.content)
            else:
                results['pages_without_content'] += 1
                results['issues'].append(f"Page with no content: {content.url}")

            if content.title and len(content.title.strip()) > 0:
                results['pages_with_title'] += 1
            else:
                results['pages_without_title'] += 1

        # Check if we have content for expected URLs if provided
        if expected_urls:
            crawled_urls = {content.url for content in crawled_content}
            missing_urls = expected_urls - crawled_urls
            if missing_urls:
                results['issues'].extend([f"Missing page: {url}" for url in missing_urls])
                results['success'] = False

        # Check if we have any content at all
        if results['pages_with_content'] == 0:
            results['issues'].append("No pages with content were found")
            results['success'] = False

        logger.info(f"Verification completed: {results['total_pages_crawled']} pages crawled, "
                   f"{results['pages_with_content']} with content")

        return results

    def verify_embedding_results(self, embeddings: List, original_chunks: List) -> Dict[str, any]:
        """
        Verify that embedding generation was completed successfully.

        Args:
            embeddings: List of embedding objects
            original_chunks: List of text chunks that were embedded

        Returns:
            Dict: Verification results with statistics and issues
        """
        results = {
            'total_embeddings': len(embeddings),
            'total_chunks': len(original_chunks),
            'embedding_success_rate': 0.0,
            'issues': [],
            'success': True
        }

        if results['total_chunks'] > 0:
            results['embedding_success_rate'] = results['total_embeddings'] / results['total_chunks'] * 100

        if results['total_embeddings'] != results['total_chunks']:
            results['issues'].append(f"Embedding count mismatch: {results['total_embeddings']} embeddings for {results['total_chunks']} chunks")
            results['success'] = False

        # Check if embeddings have proper vector data
        for i, emb in enumerate(embeddings):
            if not hasattr(emb, 'vector') or not emb.vector or len(emb.vector) == 0:
                results['issues'].append(f"Embedding {i} has no vector data")
                results['success'] = False

        logger.info(f"Embedding verification completed: {results['embedding_success_rate']:.2f}% success rate")

        return results

    def verify_storage_results(self, stored_count: int, expected_count: int) -> Dict[str, any]:
        """
        Verify that storage in Qdrant was completed successfully.

        Args:
            stored_count: Number of items stored in Qdrant
            expected_count: Number of items that were expected to be stored

        Returns:
            Dict: Verification results with statistics and issues
        """
        results = {
            'stored_count': stored_count,
            'expected_count': expected_count,
            'storage_success_rate': 0.0,
            'issues': [],
            'success': True
        }

        if expected_count > 0:
            results['storage_success_rate'] = stored_count / expected_count * 100

        if stored_count != expected_count:
            results['issues'].append(f"Storage count mismatch: {stored_count} stored for {expected_count} expected")
            results['success'] = False

        logger.info(f"Storage verification completed: {results['storage_success_rate']:.2f}% success rate")

        return results

    def generate_verification_report(self, crawling_results: Dict = None,
                                  embedding_results: Dict = None,
                                  storage_results: Dict = None) -> str:
        """
        Generate a comprehensive verification report.

        Args:
            crawling_results: Results from crawling verification
            embedding_results: Results from embedding verification
            storage_results: Results from storage verification

        Returns:
            str: Formatted verification report
        """
        report = []
        report.append("=== BOOK INGESTION VERIFICATION REPORT ===\n")

        if crawling_results:
            report.append("Crawling Results:")
            report.append(f"  - Pages crawled: {crawling_results['total_pages_crawled']}")
            report.append(f"  - Pages with content: {crawling_results['pages_with_content']}")
            report.append(f"  - Pages without content: {crawling_results['pages_without_content']}")
            report.append(f"  - Total content length: {crawling_results['total_content_length']}")
            report.append(f"  - Crawling success: {'SUCCESS' if crawling_results['success'] else 'FAILURE'}")
            report.append("")

        if embedding_results:
            report.append("Embedding Results:")
            report.append(f"  - Total embeddings: {embedding_results['total_embeddings']}")
            report.append(f"  - Total chunks: {embedding_results['total_chunks']}")
            report.append(f"  - Success rate: {embedding_results['embedding_success_rate']:.2f}%")
            report.append(f"  - Embedding success: {'SUCCESS' if embedding_results['success'] else 'FAILURE'}")
            report.append("")

        if storage_results:
            report.append("Storage Results:")
            report.append(f"  - Stored count: {storage_results['stored_count']}")
            report.append(f"  - Expected count: {storage_results['expected_count']}")
            report.append(f"  - Success rate: {storage_results['storage_success_rate']:.2f}%")
            report.append(f"  - Storage success: {'SUCCESS' if storage_results['success'] else 'FAILURE'}")
            report.append("")

        # Overall status
        all_success = True
        if crawling_results and not crawling_results['success']:
            all_success = False
        if embedding_results and not embedding_results['success']:
            all_success = False
        if storage_results and not storage_results['success']:
            all_success = False

        report.append(f"Overall Status: {'SUCCESS' if all_success else 'FAILURE'}")

        return "\n".join(report)

    def comprehensive_verification(self, crawled_content: List[BookContent] = None,
                                 embeddings: List = None,
                                 stored_count: int = 0,
                                 expected_count: int = 0) -> str:
        """
        Perform a comprehensive verification of the entire ingestion pipeline.

        Args:
            crawled_content: List of crawled content
            embeddings: List of generated embeddings
            stored_count: Number of items stored
            expected_count: Number of items expected to be stored

        Returns:
            str: Comprehensive verification report
        """
        report_parts = ["=== COMPREHENSIVE INGESTION VERIFICATION ===\n"]

        # Verify crawling if data provided
        if crawled_content is not None:
            crawling_results = self.verify_crawling_results(crawled_content)
            report_parts.append(f"Crawling Verification:")
            report_parts.append(f"  - Total pages: {crawling_results['total_pages_crawled']}")
            report_parts.append(f"  - With content: {crawling_results['pages_with_content']}")
            report_parts.append(f"  - Success: {'SUCCESS' if crawling_results['success'] else 'FAILURE'}")
            report_parts.append("")

        # Verify embeddings if data provided
        if embeddings is not None:
            total_chunks = len(crawled_content) if crawled_content is not None else 0
            embedding_results = self.verify_embedding_results(embeddings, list(range(total_chunks)) if crawled_content else [])
            report_parts.append(f"Embedding Verification:")
            report_parts.append(f"  - Total embeddings: {embedding_results['total_embeddings']}")
            report_parts.append(f"  - Success rate: {embedding_results['embedding_success_rate']:.2f}%")
            report_parts.append(f"  - Success: {'SUCCESS' if embedding_results['success'] else 'FAILURE'}")
            report_parts.append("")

        # Verify storage if data provided
        if stored_count >= 0 and expected_count >= 0:
            storage_results = self.verify_storage_results(stored_count, expected_count)
            report_parts.append(f"Storage Verification:")
            report_parts.append(f"  - Stored: {storage_results['stored_count']}")
            report_parts.append(f"  - Expected: {storage_results['expected_count']}")
            report_parts.append(f"  - Success rate: {storage_results['storage_success_rate']:.2f}%")
            report_parts.append(f"  - Success: {'SUCCESS' if storage_results['success'] else 'FAILURE'}")
            report_parts.append("")

        # Calculate overall success
        crawling_success = crawling_results['success'] if 'crawling_results' in locals() else True
        embedding_success = embedding_results['success'] if 'embedding_results' in locals() else True
        storage_success = storage_results['success'] if 'storage_results' in locals() else True

        overall_success = crawling_success and embedding_success and storage_success
        report_parts.append(f"Overall Pipeline Success: {'SUCCESS' if overall_success else 'FAILURE'}")

        return "\n".join(report_parts)


def verify_crawling(crawled_content: List[BookContent], expected_urls: Set[str] = None) -> Dict[str, any]:
    """
    Convenience function to verify crawling results.

    Args:
        crawled_content: List of BookContent objects from crawling
        expected_urls: Set of URLs that were expected to be crawled

    Returns:
        Dict: Verification results
    """
    verifier = Verifier()
    return verifier.verify_crawling_results(crawled_content, expected_urls)