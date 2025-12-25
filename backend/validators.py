from typing import List
from models import TextChunk
from exceptions import ValidationError
from logger import logger


def validate_chunk_size(text_chunks: List[TextChunk], max_chars: int = 512000) -> List[str]:
    """
    Validate that text chunks fit within Cohere model limits.

    Args:
        text_chunks: List of TextChunk objects to validate
        max_chars: Maximum number of characters allowed per chunk (default: 512000 for Cohere)

    Returns:
        List[str]: List of error messages for invalid chunks
    """
    errors = []

    for i, chunk in enumerate(text_chunks):
        if len(chunk.content) == 0:
            errors.append(f"Chunk {i} ({chunk.id}) has empty content")
        elif len(chunk.content) > max_chars:
            errors.append(f"Chunk {i} ({chunk.id}) exceeds character limit: {len(chunk.content)} > {max_chars}")

    return errors


def validate_text_chunks(text_chunks: List[TextChunk], max_chars: int = 512000) -> bool:
    """
    Validate text chunks and raise an exception if any are invalid.

    Args:
        text_chunks: List of TextChunk objects to validate
        max_chars: Maximum number of characters allowed per chunk

    Returns:
        bool: True if all chunks are valid

    Raises:
        ValidationError: If any chunks are invalid
    """
    errors = validate_chunk_size(text_chunks, max_chars)

    if errors:
        error_msg = "Validation failed for text chunks:\n" + "\n".join(errors)
        logger.error(error_msg)
        raise ValidationError(error_msg)

    return True


def validate_embedding_compatibility(embeddings: List, expected_dimension: int = None) -> List[str]:
    """
    Validate that embeddings are compatible with Qdrant storage.

    Args:
        embeddings: List of embedding objects to validate
        expected_dimension: Expected dimension of embeddings (optional)

    Returns:
        List[str]: List of error messages for invalid embeddings
    """
    errors = []

    for i, emb in enumerate(embeddings):
        if not hasattr(emb, 'vector') or emb.vector is None:
            errors.append(f"Embedding {i} has no vector data")
            continue

        if not isinstance(emb.vector, list) and not hasattr(emb.vector, '__iter__'):
            errors.append(f"Embedding {i} vector is not iterable")
            continue

        vector_len = len(emb.vector)
        if vector_len == 0:
            errors.append(f"Embedding {i} has empty vector")

        if expected_dimension and vector_len != expected_dimension:
            errors.append(f"Embedding {i} dimension mismatch: {vector_len} != {expected_dimension}")

    return errors


def validate_url_format(url: str) -> bool:
    """
    Validate that a URL has a proper format.

    Args:
        url: URL string to validate

    Returns:
        bool: True if URL is valid, False otherwise
    """
    from urllib.parse import urlparse
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_book_content(content_list) -> List[str]:
    """
    Validate a list of BookContent objects.

    Args:
        content_list: List of BookContent objects to validate

    Returns:
        List[str]: List of error messages for invalid content
    """
    errors = []

    for i, content in enumerate(content_list):
        if not content.url or not validate_url_format(content.url):
            errors.append(f"Content {i} has invalid URL: {content.url}")

        if not content.content or len(content.content.strip()) == 0:
            errors.append(f"Content {i} has no text content")

    return errors