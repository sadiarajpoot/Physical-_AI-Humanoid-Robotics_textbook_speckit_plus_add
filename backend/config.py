import os
from typing import Optional
from dotenv import load_dotenv
from dataclasses import dataclass


# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """
    Configuration class that loads settings from environment variables.
    """
    # Cohere configuration
    cohere_api_key: str = os.getenv("COHERE_API_KEY", "")

    # Qdrant configuration
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    qdrant_host: str = os.getenv("QDRANT_HOST", "")
    qdrant_collection_name: str = os.getenv("QDRANT_COLLECTION_NAME", "book_embeddings")

    # Book URL configuration
    book_url: str = os.getenv("BOOK_URL", "")

    # Chunking configuration
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Embedding configuration
    cohere_model: str = os.getenv("COHERE_MODEL", "embed-english-v3.0")
    embedding_input_type: str = os.getenv("COHERE_EMBED_INPUT_TYPE", "search_document")

    # Rate limiting
    rate_limit_delay: float = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))

    # Verification settings
    verify_ingestion: bool = os.getenv("VERIFY_INGESTION", "true").lower() == "true"

    # Resume settings
    resume_from_last: bool = os.getenv("RESUME_FROM_LAST", "false").lower() == "true"


def get_config() -> Config:
    """
    Get the application configuration from environment variables.

    Returns:
        Config: Configuration object with loaded settings
    """
    return Config()


def validate_config(config: Config) -> bool:
    """
    Validate the configuration settings.

    Args:
        config: Configuration object to validate

    Returns:
        bool: True if configuration is valid, False otherwise
    """
    errors = []

    if not config.cohere_api_key:
        errors.append("COHERE_API_KEY is required")

    if not config.qdrant_api_key:
        errors.append("QDRANT_API_KEY is required")

    if not config.qdrant_host:
        errors.append("QDRANT_HOST is required")

    if not config.book_url:
        errors.append("BOOK_URL is required")

    if config.chunk_size <= 0:
        errors.append("CHUNK_SIZE must be positive")

    if config.chunk_overlap < 0:
        errors.append("CHUNK_OVERLAP cannot be negative")

    if config.rate_limit_delay < 0:
        errors.append("RATE_LIMIT_DELAY cannot be negative")

    if config.cohere_model not in ["embed-english-v3.0", "embed-multilingual-v3.0", "embed-english-light-v3.0"]:
        errors.append("COHERE_MODEL must be a valid Cohere embedding model")

    if config.embedding_input_type not in ["search_query", "search_document", "classification", "clustering"]:
        errors.append("COHERE_EMBED_INPUT_TYPE must be one of: search_query, search_document, classification, clustering")

    if errors:
        for error in errors:
            print(f"Configuration error: {error}")
        return False

    return True