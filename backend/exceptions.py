"""
Custom exception classes for the book embeddings ingestion system.
"""


class BookIngestionError(Exception):
    """
    Base exception class for all ingestion-related errors.
    """
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.original_exception = original_exception
        self.message = message


class CrawlerError(BookIngestionError):
    """
    Exception raised when there are issues with crawling book pages.
    """
    pass


class TextExtractionError(BookIngestionError):
    """
    Exception raised when there are issues with extracting text from HTML.
    """
    pass


class ChunkingError(BookIngestionError):
    """
    Exception raised when there are issues with chunking text.
    """
    pass


class EmbeddingError(BookIngestionError):
    """
    Exception raised when there are issues with generating embeddings.
    """
    pass


class QdrantError(BookIngestionError):
    """
    Exception raised when there are issues with Qdrant operations.
    """
    pass


class ConfigurationError(BookIngestionError):
    """
    Exception raised when there are issues with configuration.
    """
    pass


class ValidationError(BookIngestionError):
    """
    Exception raised when there are issues with data validation.
    """
    pass


class RateLimitError(BookIngestionError):
    """
    Exception raised when API rate limits are exceeded.
    """
    def __init__(self, message: str = "API rate limit exceeded", retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class NetworkError(BookIngestionError):
    """
    Exception raised when there are network-related issues.
    """
    pass