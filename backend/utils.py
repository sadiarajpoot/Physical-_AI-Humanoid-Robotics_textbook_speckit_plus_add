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


def make_request_with_retry(url: str, max_retries: int = 5, timeout: int = 60) -> requests.Response:
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
                # Wait before retrying (exponential backoff)
                wait_time = 3 ** attempt  # Increased backoff
                print(f"Request failed for {url}, attempt {attempt + 1}/{max_retries}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Request failed for {url} after {max_retries} attempts.")

    # If we get here, all retries have failed
    raise last_exception