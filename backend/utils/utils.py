import re
from urllib.parse import urljoin, urlparse
from typing import List, Set
import requests


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url: URL string to validate

    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize a URL by ensuring it has a proper scheme and removing trailing slashes.

    Args:
        url: URL string to normalize

    Returns:
        str: Normalized URL
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Remove trailing slashes
    url = url.rstrip('/')

    return url


def get_base_url(url: str) -> str:
    """
    Extract the base URL from a full URL.

    Args:
        url: Full URL string

    Returns:
        str: Base URL (scheme + netloc)
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs belong to the same domain.

    Args:
        url1: First URL
        url2: Second URL

    Returns:
        bool: True if URLs are from the same domain, False otherwise
    """
    return urlparse(url1).netloc == urlparse(url2).netloc


def is_internal_link(base_url: str, link: str) -> bool:
    """
    Check if a link is internal to the base URL domain.

    Args:
        base_url: Base URL to compare against
        link: Link to check

    Returns:
        bool: True if link is internal, False otherwise
    """
    full_url = urljoin(base_url, link)
    return is_same_domain(base_url, full_url)


def extract_urls_from_html(html_content: str, base_url: str) -> Set[str]:
    """
    Extract all internal URLs from HTML content.

    Args:
        html_content: HTML content to parse
        base_url: Base URL to determine internal links

    Returns:
        Set[str]: Set of unique internal URLs found in the HTML
    """
    import re
    from urllib.parse import urljoin

    # Regular expression to find href attributes in anchor tags
    href_pattern = r'<a[^>]*href\s*=\s*["\']([^"\']*)["\'][^>]*>'
    matches = re.findall(href_pattern, html_content, re.IGNORECASE)

    urls = set()
    for match in matches:
        full_url = urljoin(base_url, match)
        if is_internal_link(base_url, full_url):
            # Normalize the URL
            normalized_url = normalize_url(full_url)
            urls.add(normalized_url)

    return urls


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and normalizing line breaks.

    Args:
        text: Raw text to clean

    Returns:
        str: Cleaned text
    """
    if not text:
        return ""

    # Replace multiple whitespace characters with a single space
    import re
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def make_request_with_retry(url: str, max_retries: int = 7, timeout: int = 90) -> requests.Response:
    """
    Make an HTTP request with retry logic.

    Args:
        url: URL to request
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds

    Returns:
        requests.Response: HTTP response object

    Raises:
        requests.RequestException: If all retry attempts fail
    """
    import time

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    last_exception = None
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response
        except requests.RequestException as e:
            last_exception = e
            if attempt < max_retries - 1:
                # Wait before retrying (increased exponential backoff for Vercel cold starts)
                wait_time = 5 ** attempt  # Even more aggressive backoff for cold starts
                print(f"Request failed for {url}, attempt {attempt + 1}/{max_retries}. Retrying in {wait_time}s (this may be due to serverless cold start)...")
                time.sleep(wait_time)
            else:
                print(f"Request failed for {url} after {max_retries} attempts.")

    # If we get here, all retries have failed
    raise last_exception


def evaluate_query_results(query: str, results: List[dict], expected_topic: str = None) -> dict:
    """
    Evaluate the relevance of query results.

    Args:
        query: The original query text
        results: List of retrieved results
        expected_topic: Expected topic for evaluation (optional)

    Returns:
        dict: Evaluation metrics and assessment
    """
    if not results:
        return {
            "query": query,
            "result_count": 0,
            "avg_similarity_score": 0.0,
            "high_relevance_count": 0,
            "relevance_percentage": 0.0,
            "expected_topic_match": 0 if expected_topic else None,
            "is_relevant": False
        }

    # Calculate metrics
    total_score = sum(r.get('similarity_score', 0.0) for r in results)
    avg_score = total_score / len(results)

    high_relevance_results = [r for r in results if r.get('similarity_score', 0.0) > 0.3]
    high_relevance_count = len(high_relevance_results)
    relevance_percentage = (high_relevance_count / len(results)) * 100

    # Check if any result matches expected topic if provided
    expected_topic_match = 0
    if expected_topic:
        for result in results:
            metadata = result.get('metadata', {})
            # Check if topic-related metadata matches expected topic
            if expected_topic.lower() in str(metadata.get('chapter', '')).lower() or \
               expected_topic.lower() in str(metadata.get('section', '')).lower() or \
               expected_topic.lower() in result.get('source_url', '').lower():
                expected_topic_match += 1

    return {
        "query": query,
        "result_count": len(results),
        "avg_similarity_score": avg_score,
        "high_relevance_count": high_relevance_count,
        "relevance_percentage": relevance_percentage,
        "expected_topic_match": expected_topic_match if expected_topic else None,
        "is_relevant": relevance_percentage > 50  # Consider relevant if >50% results are high relevance
    }


def format_retrieved_results(results: List[dict]) -> List[dict]:
    """
    Format retrieved results for presentation.

    Args:
        results: Raw results from the retrieval system

    Returns:
        List[dict]: Formatted results ready for presentation
    """
    formatted_results = []
    for result in results:
        formatted_result = {
            "content": result.get("content", ""),
            "similarity_score": round(result.get("similarity_score", 0.0), 4),
            "source_url": result.get("source_url", ""),
            "chunk_id": result.get("chunk_id", ""),
            "metadata": result.get("metadata", {}),
            "content_preview": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", "")
        }
        formatted_results.append(formatted_result)

    return formatted_results


def aggregate_metrics(evaluation_results: List[dict]) -> dict:
    """
    Aggregate evaluation metrics across multiple queries.

    Args:
        evaluation_results: List of individual evaluation results

    Returns:
        dict: Aggregated metrics across all evaluations
    """
    if not evaluation_results:
        return {
            "total_queries": 0,
            "total_results": 0,
            "avg_similarity_score": 0.0,
            "overall_relevance_percentage": 0.0,
            "queries_with_results": 0,
            "high_relevance_queries": 0
        }

    total_queries = len(evaluation_results)
    total_results = sum(er.get("result_count", 0) for er in evaluation_results)
    avg_similarity_scores = [er.get("avg_similarity_score", 0.0) for er in evaluation_results if er.get("result_count", 0) > 0]
    avg_similarity = sum(avg_similarity_scores) / len(avg_similarity_scores) if avg_similarity_scores else 0.0

    queries_with_results = sum(1 for er in evaluation_results if er.get("result_count", 0) > 0)
    high_relevance_queries = sum(1 for er in evaluation_results if er.get("is_relevant", False))

    # Calculate overall relevance percentage
    all_relevance_percentages = [er.get("relevance_percentage", 0.0) for er in evaluation_results if er.get("result_count", 0) > 0]
    overall_relevance_percentage = sum(all_relevance_percentages) / len(all_relevance_percentages) if all_relevance_percentages else 0.0

    return {
        "total_queries": total_queries,
        "total_results": total_results,
        "avg_similarity_score": avg_similarity,
        "overall_relevance_percentage": overall_relevance_percentage,
        "queries_with_results": queries_with_results,
        "high_relevance_queries": high_relevance_queries,
        "success_rate": (high_relevance_queries / total_queries * 100) if total_queries > 0 else 0.0
    }


def add_query_preprocessing(query: str) -> str:
    """
    Preprocess a query string by normalizing and cleaning it.

    Args:
        query: Raw query string

    Returns:
        str: Preprocessed query string
    """
    if not query:
        return ""

    # Convert to lowercase
    processed_query = query.lower()

    # Remove extra whitespace
    import re
    processed_query = re.sub(r'\s+', ' ', processed_query).strip()

    # Remove special characters if needed, though we keep them for semantic search
    # For now, just return the normalized version
    return processed_query