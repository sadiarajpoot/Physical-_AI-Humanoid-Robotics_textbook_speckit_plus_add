from bs4 import BeautifulSoup
from typing import List, Dict, Any
from models import BookContent
import re


def extract_clean_text_from_html(html_content: str, url: str = "") -> str:
    """
    Extract clean text content from HTML, filtering out navigation elements.

    Args:
        html_content: Raw HTML content to parse
        url: URL of the page being processed (for context)

    Returns:
        str: Clean text content extracted from the HTML
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove navigation and UI elements that are common in Docusaurus sites
    for element in soup.find_all(['nav', 'header', 'footer', 'aside']):
        element.decompose()

    # Remove elements with common Docusaurus class names for navigation/components
    for element in soup.find_all(class_=re.compile(r'navbar|menu|toc|pagination|footer|header|nav')):
        element.decompose()

    # Remove script and style elements
    for script in soup(["script", "style", "meta", "link"]):
        script.decompose()

    # Get text content and clean it up
    text = soup.get_text()

    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    return text


def extract_title_from_html(html_content: str) -> str:
    """
    Extract the title from HTML content.

    Args:
        html_content: Raw HTML content to parse

    Returns:
        str: Title of the page, or empty string if not found
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text().strip()

    # Try to find a h1 tag as an alternative
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.get_text().strip()

    return ""


def extract_content_structure(html_content: str) -> Dict[str, Any]:
    """
    Extract content structure including headings and sections.

    Args:
        html_content: Raw HTML content to parse

    Returns:
        Dict[str, Any]: Dictionary containing content structure information
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    structure = {
        'title': extract_title_from_html(html_content),
        'headings': [],
        'sections': []
    }

    # Extract headings (h1, h2, h3, etc.)
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        structure['headings'].append({
            'level': int(heading.name[1]),
            'text': heading.get_text().strip()
        })

    return structure


def parse_book_page(html_content: str, url: str) -> BookContent:
    """
    Parse a book page HTML and create a BookContent object.

    Args:
        html_content: Raw HTML content of the page
        url: URL of the page

    Returns:
        BookContent: BookContent object with extracted information
    """
    title = extract_title_from_html(html_content)
    clean_content = extract_clean_text_from_html(html_content, url)
    structure = extract_content_structure(html_content)

    # Extract chapter/section info from URL or structure
    chapter = None
    section = None

    # Try to extract chapter/section from URL path
    from urllib.parse import urlparse
    path_parts = urlparse(url).path.strip('/').split('/')
    if len(path_parts) >= 2:
        chapter = path_parts[-2] if path_parts[-2] else None
        section = path_parts[-1] if path_parts[-1] != '' else path_parts[-2]

    # If not found in URL, try to use the first heading as chapter
    if not chapter and structure['headings']:
        for heading in structure['headings']:
            if heading['level'] == 1:
                chapter = heading['text']
                break

    return BookContent(
        url=url,
        title=title,
        content=clean_content,
        chapter=chapter,
        section=section
    )


def filter_navigation_elements(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Remove navigation and UI elements from BeautifulSoup object.

    Args:
        soup: BeautifulSoup object to clean

    Returns:
        BeautifulSoup: Cleaned BeautifulSoup object
    """
    # Remove navigation and UI elements
    for element in soup.find_all(['nav', 'header', 'footer', 'aside']):
        element.decompose()

    # Remove elements with common class names for navigation
    for element in soup.find_all(class_=re.compile(r'navbar|menu|toc|pagination|footer|header|nav')):
        element.decompose()

    # Remove script and style elements
    for script in soup(["script", "style", "meta", "link"]):
        script.decompose()

    return soup