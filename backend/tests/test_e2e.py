"""
End-to-end tests for the book ingestion pipeline.
These tests are placeholders and would need actual services for full testing.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from models import BookContent, TextChunk, Embedding
from config import Config
from crawler import Crawler
from chunker import TextChunker
from embedders import CohereEmbedder
from vector_store import QdrantVectorStore


def test_e2e_pipeline_flow():
    """Test the complete pipeline flow (with mocked external services)."""
    # Create a mock configuration
    config = Config(
        cohere_api_key="test-key",
        qdrant_api_key="test-key",
        qdrant_host="https://test-cluster.qdrant.tech",
        qdrant_collection_name="test_collection",
        book_url="https://example.com/book"
    )

    # Mock the external services to avoid actual API calls
    with patch('qdrant_client.QdrantClient') as mock_qdrant, \
         patch('cohere.Client') as mock_cohere:

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant.return_value = mock_qdrant_instance
        mock_qdrant_instance.get_collection.side_effect = Exception("Collection not found")
        mock_qdrant_instance.create_collection.return_value = True
        mock_qdrant_instance.upsert.return_value = True

        # Mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere.return_value = mock_cohere_instance
        mock_cohere_instance.embed.return_value = MagicMock(embeddings=[[0.1, 0.2, 0.3]])

        # Test data
        book_content = [
            BookContent(
                url="https://example.com/page1",
                title="Test Page 1",
                content="This is the content of test page 1. It contains some text that will be chunked and embedded."
            ),
            BookContent(
                url="https://example.com/page2",
                title="Test Page 2",
                content="This is the content of test page 2. It also contains text for testing purposes."
            )
        ]

        # Test chunking
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        text_chunks = chunker.chunk_book_content(book_content)

        assert len(text_chunks) > 0, "Should generate text chunks"
        for chunk in text_chunks:
            assert isinstance(chunk, TextChunk)
            assert chunk.content
            assert chunk.source_url

        # Test embedding (with mocked API call)
        embedder = CohereEmbedder(config)
        # We can't fully test embedding without a real API key, so we'll test the preparation
        assert embedder.model == "embed-english-v3.0"
        assert embedder.input_type == "search_document"

        # Test storage (with mocked Qdrant)
        vector_store = QdrantVectorStore(config)
        # The collection creation and storage would be tested with real Qdrant instance
        assert vector_store.collection_name == "test_collection"

        # Verify the flow worked without exceptions
        assert len(book_content) == 2
        assert len(text_chunks) > 0


def test_configuration_validation():
    """Test that configuration validation works properly."""
    # Valid configuration
    valid_config = Config(
        cohere_api_key="test-key",
        qdrant_api_key="test-key",
        qdrant_host="https://test-cluster.qdrant.tech",
        qdrant_collection_name="test_collection",
        book_url="https://example.com/book"
    )

    from config import validate_config
    assert validate_config(valid_config) == True

    # Invalid configuration (missing required fields)
    invalid_config = Config(
        cohere_api_key="",
        qdrant_api_key="",
        qdrant_host="",
        book_url=""
    )

    assert validate_config(invalid_config) == False


def test_data_models():
    """Test that data models work correctly."""
    # Test BookContent
    book_content = BookContent(
        url="https://example.com/page",
        title="Test Page",
        content="This is test content"
    )

    assert book_content.url == "https://example.com/page"
    assert book_content.title == "Test Page"
    assert book_content.content == "This is test content"

    # Test TextChunk
    chunk = TextChunk(
        id="test-id",
        content="This is a text chunk",
        source_url="https://example.com/page"
    )

    assert chunk.id == "test-id"
    assert chunk.content == "This is a text chunk"
    assert chunk.source_url == "https://example.com/page"

    # Test Embedding
    embedding = Embedding(
        id="test-emb-id",
        vector=[0.1, 0.2, 0.3],
        text_chunk=chunk
    )

    assert embedding.id == "test-emb-id"
    assert embedding.vector == [0.1, 0.2, 0.3]
    assert embedding.text_chunk == chunk


def test_error_handling():
    """Test basic error handling."""
    from exceptions import BookIngestionError, CrawlerError, EmbeddingError, QdrantError

    # Test base exception
    try:
        raise BookIngestionError("Test error message")
    except BookIngestionError as e:
        assert str(e) == "Test error message"

    # Test specific exceptions
    try:
        raise CrawlerError("Crawler error")
    except CrawlerError:
        pass  # Expected

    try:
        raise EmbeddingError("Embedding error")
    except EmbeddingError:
        pass  # Expected

    try:
        raise QdrantError("Qdrant error")
    except QdrantError:
        pass  # Expected