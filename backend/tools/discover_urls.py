#!/usr/bin/env python3
"""
Script to discover actual available URLs by crawling from the main page
instead of relying solely on sitemap.xml which may contain invalid URLs.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Set


def is_valid_content_page(url: str) -> bool:
    """
    Check if a URL is likely to be a content page worth crawling.
    """
    parsed = urlparse(url)
    path = parsed.path.lower()

    # Exclude common non-content URLs
    excluded_patterns = [
        '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg',
        '.pdf', '.zip', '.exe', '.ico', 'assets', 'static'
    ]

    # Include likely content pages
    included_patterns = [
        '/docs/', '/tutorial', '/modules', '/week', '/intro',
        '/overview', '/capstone', '/assessments', '/learning-outcomes'
    ]

    # Check if it matches excluded patterns
    for pattern in excluded_patterns:
        if pattern in path:
            return False

    # Check if it matches included patterns
    for pattern in included_patterns:
        if pattern in path:
            return True

    # If it doesn't match any specific pattern but is internal, consider it
    return True


def discover_urls_from_page(base_url: str, max_pages: int = 50) -> Set[str]:
    """
    Discover URLs by crawling the main page and following internal links.
    """
    visited_urls = set()
    urls_to_visit = {base_url}
    all_urls = set()

    print(f"Starting URL discovery from: {base_url}")

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop()
        if current_url in visited_urls:
            continue

        try:
            print(f"Crawling: {current_url}")
            response = requests.get(
                current_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout=30
            )

            # Add to visited set
            visited_urls.add(current_url)

            if response.status_code == 200:
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(base_url, href)

                    # Check if it's an internal link and a potential content page
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        if is_valid_content_page(full_url):
                            if full_url not in visited_urls and full_url not in urls_to_visit:
                                urls_to_visit.add(full_url)
                                all_urls.add(full_url)

            time.sleep(1)  # Be respectful to the server

        except requests.RequestException as e:
            print(f"Error crawling {current_url}: {e}")
            visited_urls.add(current_url)  # Don't retry failed URLs

    print(f"\nDiscovered {len(all_urls)} potential content URLs")
    for url in sorted(all_urls):
        print(f"  - {url}")

    return all_urls


def test_url_accessibility(url: str, timeout: int = 30) -> bool:
    """
    Test if a URL is actually accessible.
    """
    try:
        response = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=timeout
        )
        is_accessible = response.status_code == 200
        print(f"{'✓' if is_accessible else '✗'} {url} - Status: {response.status_code}")
        return is_accessible
    except requests.RequestException:
        print(f"✗ {url} - Request failed")
        return False


def main():
    base_url = "https://physical-ai-humanoid-robotics-textb-seven-lime.vercel.app"

    print("Discovering URLs from the main page...")
    discovered_urls = discover_urls_from_page(base_url)

    print(f"\nTesting accessibility of {len(discovered_urls)} URLs...")
    accessible_urls = []

    for url in discovered_urls:
        if test_url_accessibility(url):
            accessible_urls.append(url)

    print(f"\nFound {len(accessible_urls)} accessible content URLs:")
    for url in accessible_urls:
        print(f"  {url}")

    # Save to file
    with open('accessible_urls.txt', 'w') as f:
        for url in accessible_urls:
            f.write(url + '\n')

    print(f"\nAccessible URLs saved to accessible_urls.txt")


if __name__ == "__main__":
    main()