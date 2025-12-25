import time
from typing import List, Set
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from logger import logger
from models import BookContent
from parsers import parse_book_page
from utils import make_request_with_retry, normalize_url, is_internal_link
from exceptions import CrawlerError, NetworkError
import xml.etree.ElementTree as ET


class Crawler:
    """
    A class to crawl Docusaurus book pages and extract content.
    """
    def __init__(self, config, rate_limit_delay: float = 1.0):
        """
        Initialize the crawler with configuration.

        Args:
            config: Configuration object
            rate_limit_delay: Delay between requests to avoid overwhelming the server
        """
        self.config = config
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()

    def _get_urls_from_sitemap(self, base_url: str) -> Set[str]:
        """
        Get all URLs from the sitemap.xml file.

        Args:
            base_url: Base URL of the Docusaurus book

        Returns:
            Set[str]: Set of URLs found in the sitemap
        """
        sitemap_url = f"{base_url}/sitemap.xml"
        urls = set()

        try:
            logger.info(f"Fetching sitemap from: {sitemap_url}")
            response = make_request_with_retry(sitemap_url)

            # Parse the XML sitemap
            root = ET.fromstring(response.content)

            # Find all <loc> elements which contain URLs
            for url_element in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                url = url_element.text.strip()
                if url and is_internal_link(base_url, url):
                    urls.add(normalize_url(url))

        except requests.RequestException as e:
            logger.warning(f"Failed to fetch sitemap from {sitemap_url}: {e}")
            logger.info("Falling back to link extraction from base page")
            # If sitemap is not available, fall back to link extraction
            urls = self._extract_urls_from_page_base(base_url)
        except ET.ParseError as e:
            logger.warning(f"Failed to parse sitemap XML: {e}")
            # If sitemap parsing fails, fall back to link extraction
            urls = self._extract_urls_from_page_base(base_url)

        return urls

    def _extract_urls_from_page_base(self, base_url: str) -> Set[str]:
        """
        Extract URLs by crawling the base page.

        Args:
            base_url: Base URL of the Docusaurus book

        Returns:
            Set[str]: Set of URLs found by crawling the base page
        """
        urls = set()
        try:
            response = make_request_with_retry(base_url)
            new_urls = self._extract_urls_from_page(response.text, base_url)
            urls.update({normalize_url(url) for url in new_urls if is_internal_link(base_url, url)})
        except requests.RequestException as e:
            logger.warning(f"Failed to crawl base page {base_url}: {e}")

        return urls

    def _extract_urls_from_page(self, html_content: str, base_url: str) -> Set[str]:
        """
        Extract all internal URLs from a page's HTML content.

        Args:
            html_content: HTML content of the page
            base_url: Base URL to determine internal links

        Returns:
            Set[str]: Set of internal URLs found in the page
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        urls = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)

            if is_internal_link(base_url, full_url):
                urls.add(full_url)

        return urls

    def crawl_book(self, base_url: str, max_pages: int = 1000) -> List[BookContent]:
        """
        Crawl all pages in the book and extract content using sitemap.xml.

        Args:
            base_url: Base URL of the Docusaurus book
            max_pages: Maximum number of pages to crawl (default: 1000)

        Returns:
            List[BookContent]: List of BookContent objects with extracted content
        """
        base_url = normalize_url(base_url)

        # Get URLs from sitemap first
        urls_to_crawl = self._get_urls_from_sitemap(base_url)
        logger.info(f"Found {len(urls_to_crawl)} URLs in sitemap")

        all_content = []
        crawled_count = 0

        for url in urls_to_crawl:
            if crawled_count >= max_pages:
                break

            try:
                logger.info(f"Crawling: {url}")

                # Make request with retry logic
                response = make_request_with_retry(url)

                # Extract content from the page
                book_content = parse_book_page(response.text, url)
                all_content.append(book_content)

                crawled_count += 1

                # Apply rate limiting
                time.sleep(self.rate_limit_delay)

            except requests.RequestException as e:
                logger.warning(f"Failed to crawl {url}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error crawling {url}: {e}")

        logger.info(f"Crawled {len(all_content)} pages out of {len(urls_to_crawl)} available")
        return all_content

    def crawl_single_page(self, url: str) -> BookContent:
        """
        Crawl a single page and extract content.

        Args:
            url: URL of the page to crawl

        Returns:
            BookContent: BookContent object with extracted content
        """
        try:
            logger.info(f"Crawling single page: {url}")

            # Make request with retry logic
            response = make_request_with_retry(url)

            # Extract content from the page
            book_content = parse_book_page(response.text, url)

            # Apply rate limiting
            time.sleep(self.rate_limit_delay)

            return book_content

        except requests.RequestException as e:
            logger.error(f"Failed to crawl {url}: {e}")
            raise CrawlerError(f"Failed to crawl {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error crawling {url}: {e}")
            raise CrawlerError(f"Unexpected error crawling {url}: {e}")


def crawl_book_content(base_url: str, config, rate_limit_delay: float = 1.0) -> List[BookContent]:
    """
    Convenience function to crawl book content.

    Args:
        base_url: Base URL of the Docusaurus book
        config: Configuration object
        rate_limit_delay: Delay between requests

    Returns:
        List[BookContent]: List of BookContent objects
    """
    crawler = Crawler(config, rate_limit_delay)
    return crawler.crawl_book(base_url)