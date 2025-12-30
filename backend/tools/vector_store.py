from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Optional, Dict, Any
from ..models.models import Embedding, QdrantCollection
from ..utils.exceptions import QdrantError
from ..utils.logger import logger
from ..config.config import Config
import uuid
import time
from functools import wraps


class QdrantVectorStore:
    """
    A class to handle vector storage operations with Qdrant.
    """
    def __init__(self, config: Config):
        """
        Initialize the Qdrant vector store with configuration.

        Args:
            config: Configuration object containing Qdrant settings
        """
        self.config = config
        self.qdrant_client = QdrantClient(
            url=config.qdrant_host,
            api_key=config.qdrant_api_key,
            prefer_grpc=False  # Using HTTP for compatibility
        )
        self.collection_name = config.qdrant_collection_name

        # Rate limiting configuration
        self._last_request_time = 0
        self._min_request_interval = config.rate_limit_delay  # from config

    def create_collection(self, vector_size: int = 1024, distance: str = "Cosine") -> bool:
        """
        Create a Qdrant collection for storing embeddings.

        Args:
            vector_size: Size of the embedding vectors (default: 1024 for Cohere embeddings)
            distance: Distance metric for similarity search (default: "Cosine")

        Returns:
            bool: True if collection was created or already exists
        """
        try:
            # Check if collection already exists
            try:
                self.qdrant_client.get_collection(self.collection_name)
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True
            except:
                # Collection doesn't exist, create it
                pass

            # Create the collection
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance[distance.upper()]
                )
            )

            logger.info(f"Created collection '{self.collection_name}' with {distance} distance metric")
            return True

        except Exception as e:
            logger.error(f"Error creating collection '{self.collection_name}': {e}")
            raise QdrantError(f"Error creating collection: {e}")

    def store_embeddings(self, embeddings: List[Embedding], batch_size: int = 64) -> int:
        """
        Store embeddings in Qdrant collection.

        Args:
            embeddings: List of Embedding objects to store
            batch_size: Number of embeddings to store in each batch (default: 64)

        Returns:
            int: Number of embeddings successfully stored
        """
        if not embeddings:
            return 0

        total_stored = 0
        total_embeddings = len(embeddings)

        # Process in batches to respect API limits
        for i in range(0, total_embeddings, batch_size):
            batch = embeddings[i:i + batch_size]
            logger.info(f"Storing batch {i//batch_size + 1}/{(total_embeddings-1)//batch_size + 1}")

            try:
                # Prepare points for insertion
                points = []
                for embedding in batch:
                    # Create payload with metadata
                    payload = {
                        "source_url": embedding.text_chunk.source_url,
                        "content": embedding.text_chunk.content,
                        "chunk_id": embedding.text_chunk.id,
                        "chunk_index": embedding.text_chunk.chunk_index,
                        "total_chunks": embedding.text_chunk.total_chunks,
                    }

                    # Add chapter and section if available
                    if embedding.text_chunk.chapter:
                        payload["chapter"] = embedding.text_chunk.chapter
                    if embedding.text_chunk.section:
                        payload["section"] = embedding.text_chunk.section

                    # Add creation timestamp
                    payload["created_at"] = embedding.created_at.isoformat()

                    point = models.PointStruct(
                        id=str(uuid.uuid4()),  # Generate unique ID for the point
                        vector=embedding.vector,
                        payload=payload
                    )
                    points.append(point)

                # Upsert the points to Qdrant
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )

                total_stored += len(points)
                logger.info(f"Stored {len(points)} embeddings in batch")

            except Exception as e:
                logger.error(f"Error storing batch {i//batch_size + 1}: {e}")
                raise QdrantError(f"Error storing embeddings: {e}")

        logger.info(f"Successfully stored {total_stored} embeddings out of {total_embeddings}")
        return total_stored

    def check_idempotency(self, embeddings: List[Embedding]) -> List[Embedding]:
        """
        Check which embeddings already exist in the collection to ensure idempotency.

        Args:
            embeddings: List of Embedding objects to check

        Returns:
            List[Embedding]: List of embeddings that don't already exist in the collection
        """
        if not embeddings:
            return []

        # For idempotency, we'll use the source URL and chunk ID to check if an embedding already exists
        # This is a simplified approach - in a real implementation, you might want to use more sophisticated methods
        new_embeddings = []

        for embedding in embeddings:
            # Check if a point with the same source_url and chunk_id already exists
            try:
                results = self.qdrant_client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="source_url",
                                match=models.MatchValue(value=embedding.text_chunk.source_url)
                            ),
                            models.FieldCondition(
                                key="chunk_id",
                                match=models.MatchValue(value=embedding.text_chunk.id)
                            )
                        ]
                    ),
                    limit=1
                )

                # If no results found, this embedding doesn't exist yet
                if not results[0]:  # results is a tuple (points, next_page_offset)
                    new_embeddings.append(embedding)
                else:
                    logger.info(f"Skipping duplicate embedding for {embedding.text_chunk.source_url} - {embedding.text_chunk.id}")
            except Exception as e:
                logger.warning(f"Error checking idempotency for {embedding.text_chunk.id}: {e}")
                # If there's an error checking, we'll assume it doesn't exist and try to store it
                new_embeddings.append(embedding)

        return new_embeddings

    def search_similar(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in the collection.

        Args:
            query_vector: Vector to search for similarities
            top_k: Number of similar results to return (default: 5)

        Returns:
            List[Dict[str, Any]]: List of similar embeddings with their metadata
        """
        try:
            response = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k
            )

            # Format results - query_points returns a QueryResponse object
            # The results are in the 'points' attribute
            formatted_results = []
            for point in response.points:
                formatted_result = {
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload,
                    "vector": point.vector
                }
                formatted_results.append(formatted_result)

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching for similar embeddings: {e}")
            raise QdrantError(f"Error searching for similar embeddings: {e}")

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.

        Returns:
            Dict[str, Any]: Collection information including point count
        """
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "point_count": collection_info.points_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise QdrantError(f"Error getting collection info: {e}")

    def clear_collection(self) -> bool:
        """
        Clear all points from the collection.

        Returns:
            bool: True if successful
        """
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter()
                )
            )
            logger.info(f"Cleared collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise QdrantError(f"Error clearing collection: {e}")


def store_embeddings_in_qdrant(embeddings: List[Embedding], config: Config, batch_size: int = 64) -> int:
    """
    Convenience function to store embeddings in Qdrant.

    Args:
        embeddings: List of Embedding objects to store
        config: Configuration object
        batch_size: Number of embeddings to store in each batch

    Returns:
        int: Number of embeddings successfully stored
    """
    vector_store = QdrantVectorStore(config)

    # Create collection if it doesn't exist
    vector_store.create_collection()

    # Check for idempotency
    new_embeddings = vector_store.check_idempotency(embeddings)

    # Store the new embeddings
    return vector_store.store_embeddings(new_embeddings, batch_size)