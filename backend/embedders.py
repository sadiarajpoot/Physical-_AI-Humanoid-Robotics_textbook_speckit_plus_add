import cohere
from typing import List, Dict, Any
from models import TextChunk, Embedding
from exceptions import EmbeddingError, RateLimitError
from logger import logger
from config import Config
import time


class CohereEmbedder:
    """
    A class to handle embedding generation using Cohere API.
    """
    def __init__(self, config: Config):
        """
        Initialize the Cohere embedder with configuration.

        Args:
            config: Configuration object containing API key and settings
        """
        self.config = config
        self.client = cohere.Client(config.cohere_api_key)
        self.model = config.cohere_model
        self.input_type = config.embedding_input_type

    def embed_chunks(self, text_chunks: List[TextChunk], batch_size: int = 96) -> List[Embedding]:
        """
        Generate embeddings for a list of text chunks.

        Args:
            text_chunks: List of TextChunk objects to embed
            batch_size: Number of chunks to process in each batch (default: 96, max allowed by Cohere)

        Returns:
            List[Embedding]: List of Embedding objects
        """
        if not text_chunks:
            return []

        all_embeddings = []
        total_chunks = len(text_chunks)

        # Process in batches to respect API limits
        for i in range(0, total_chunks, batch_size):
            batch = text_chunks[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_chunks-1)//batch_size + 1}")

            try:
                # Extract text content for embedding
                texts = [chunk.content for chunk in batch]

                # Generate embeddings
                response = self.client.embed(
                    texts=texts,
                    model=self.model,
                    input_type=self.input_type
                )

                # Create Embedding objects
                for j, embedding_vector in enumerate(response.embeddings):
                    embedding = Embedding(
                        id=batch[j].id,
                        vector=embedding_vector,
                        text_chunk=batch[j]
                    )
                    all_embeddings.append(embedding)

                # Respect rate limits
                time.sleep(0.1)  # Small delay between batches

            except cohere.CohereError as e:
                logger.error(f"Cohere API error during embedding: {e}")
                if "rate limit" in str(e).lower():
                    raise RateLimitError(f"Rate limit exceeded: {e}")
                else:
                    raise EmbeddingError(f"Cohere API error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during embedding: {e}")
                raise EmbeddingError(f"Unexpected error during embedding: {e}")

        logger.info(f"Generated embeddings for {len(all_embeddings)} text chunks")
        return all_embeddings

    def embed_text(self, text: str, text_chunk: TextChunk = None) -> Embedding:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed
            text_chunk: Optional TextChunk object to associate with the embedding

        Returns:
            Embedding: Embedding object
        """
        try:
            response = self.client.embed(
                texts=[text],
                model=self.model,
                input_type=self.input_type
            )

            if not text_chunk:
                # Create a minimal TextChunk if not provided
                text_chunk = TextChunk(
                    id="temp",
                    content=text,
                    source_url="unknown"
                )

            embedding = Embedding(
                id=text_chunk.id,
                vector=response.embeddings[0],
                text_chunk=text_chunk
            )

            return embedding

        except cohere.CohereError as e:
            logger.error(f"Cohere API error during single text embedding: {e}")
            if "rate limit" in str(e).lower():
                raise RateLimitError(f"Rate limit exceeded: {e}")
            else:
                raise EmbeddingError(f"Cohere API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during single text embedding: {e}")
            raise EmbeddingError(f"Unexpected error during single text embedding: {e}")


def validate_chunk_size(text_chunks: List[TextChunk], max_chars: int = 512000) -> List[str]:
    """
    Validate that text chunks fit within Cohere model limits.

    Args:
        text_chunks: List of TextChunk objects to validate
        max_chars: Maximum number of characters allowed per chunk

    Returns:
        List[str]: List of error messages for invalid chunks
    """
    errors = []

    for i, chunk in enumerate(text_chunks):
        if len(chunk.content) > max_chars:
            errors.append(f"Chunk {i} ({chunk.id}) exceeds character limit: {len(chunk.content)} > {max_chars}")

    return errors


def embed_text_chunks(text_chunks: List[TextChunk], config: Config, batch_size: int = 96) -> List[Embedding]:
    """
    Convenience function to embed text chunks.

    Args:
        text_chunks: List of TextChunk objects to embed
        config: Configuration object
        batch_size: Number of chunks to process in each batch

    Returns:
        List[Embedding]: List of Embedding objects
    """
    embedder = CohereEmbedder(config)
    return embedder.embed_chunks(text_chunks, batch_size)