"""
RAG Pipeline: Retrieve extracted data and test end-to-end functionality

This module contains the RAGRetriever class for handling retrieval of book content
from Qdrant using semantic search.
"""
import os
import sys
import time
from typing import List, Dict, Any, Optional
import logging

from ..config.config import Config, get_config
from ..tools.vector_store import QdrantVectorStore
from ..embedders.embedders import CohereEmbedder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGRetriever:
    """
    Class to handle retrieval of book content from Qdrant using semantic search.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the RAG retriever with Qdrant and Cohere clients.

        Args:
            config: Configuration object. If None, loads from environment
        """
        self.config = config or get_config()

        # Initialize vector store
        self.vector_store = QdrantVectorStore(self.config)

        # Initialize embedder
        self.embedder = CohereEmbedder(self.config)

        # Verify collection exists
        try:
            collection_info = self._retry_operation(self.vector_store.get_collection_info)
            logger.info(f"Connected to Qdrant collection: {self.config.qdrant_collection_name}")
            logger.info(f"Collection has {collection_info['point_count']} points")
        except Exception as e:
            logger.error(f"Could not connect to collection {self.config.qdrant_collection_name}: {e}")
            raise

    def _retry_operation(self, operation, max_retries: int = 3, delay: float = 1.0):
        """
        Execute an operation with retry logic.

        Args:
            operation: Function to execute
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries in seconds

        Returns:
            Result of the operation

        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None

        for attempt in range(max_retries + 1):  # +1 to include the initial attempt
            try:
                return operation()
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    # Exponential backoff: delay doubles with each attempt
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Operation failed after {max_retries + 1} attempts: {e}")

        # If we get here, all retries have failed
        raise last_exception

    def query_embeddings(self, query_text: str, top_k: int = 5,
                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query Qdrant for relevant text chunks based on semantic similarity.

        Args:
            query_text: The text query to search for
            top_k: Number of top results to return
            filters: Optional metadata filters to apply

        Returns:
            List of dictionaries containing the retrieved chunks with metadata

        Raises:
            Exception: If query processing fails at any step
        """
        try:
            # Validate inputs
            if not query_text or not query_text.strip():
                logger.warning("Empty query provided")
                return []

            if top_k <= 0:
                logger.warning(f"Invalid top_k value: {top_k}, using default of 5")
                top_k = 5

            # Preprocess the query text
            from ..utils.utils import add_query_preprocessing
            processed_query = add_query_preprocessing(query_text)

            # Generate embedding for the processed query text with retry logic
            query_embedding_obj = self._retry_operation(
                lambda: self.embedder.embed_text(processed_query),
                max_retries=3,
                delay=1.0
            )
            query_embedding = query_embedding_obj.vector

            # Perform the search with retry logic
            search_results = self._retry_operation(
                lambda: self.vector_store.search_similar(
                    query_vector=query_embedding,
                    top_k=top_k
                ),
                max_retries=3,
                delay=1.0
            )

            # Apply metadata filters if provided
            if filters:
                # Validate filters
                if not isinstance(filters, dict):
                    logger.warning(f"Invalid filters format: {filters}. Expected dict, got {type(filters)}")
                    filters = {}

                for key, value in filters.items():
                    if key is None or str(key).strip() == "":
                        logger.warning(f"Invalid filter key: {key}. Skipping this filter.")
                        continue
                    if value is None:
                        logger.warning(f"Filter value for key '{key}' is None. This may cause unexpected behavior.")

                filtered_results = []
                for result in search_results:
                    # Check if result matches all filter criteria
                    matches = True
                    for key, value in filters.items():
                        if key is not None and str(key).strip() != "":
                            if result['payload'].get(key) != value:
                                matches = False
                                break
                    if matches:
                        filtered_results.append(result)

                search_results = filtered_results

            # Format results
            results = []
            for result in search_results:
                chunk_data = {
                    "content": result['payload'].get("content", ""),
                    "source_url": result['payload'].get("source_url", ""),
                    "chunk_id": result['payload'].get("chunk_id", ""),
                    "similarity_score": result.get("score", 0.0),
                    "metadata": {k: v for k, v in result['payload'].items()
                               if k not in ["content", "source_url", "chunk_id"]}
                }
                results.append(chunk_data)

            logger.info(f"Successfully retrieved {len(results)} results for query: '{query_text[:50]}{'...' if len(query_text) > 50 else ''}'")
            return results

        except Exception as e:
            logger.error(f"Error during query processing: {e}")
            raise

    def reconstruct_context(self, chunk_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Reconstruct full contexts from specific chunk IDs.

        Args:
            chunk_ids: List of chunk IDs to retrieve

        Returns:
            List of dictionaries containing the full context for each chunk
        """
        if not chunk_ids:
            logger.info("No chunk IDs provided for context reconstruction")
            return []

        try:
            # Retrieve specific points by ID from Qdrant
            records = self.vector_store.qdrant_client.retrieve(
                collection_name=self.config.qdrant_collection_name,
                ids=chunk_ids
            )

            contexts = []
            for record in records:
                payload = record.payload
                context = {
                    "source_url": payload.get("source_url", ""),
                    "content": payload.get("content", ""),
                    "chunk_id": payload.get("chunk_id", ""),
                    "chunk_index": payload.get("chunk_index"),
                    "total_chunks": payload.get("total_chunks"),
                    "chapter": payload.get("chapter"),
                    "section": payload.get("section"),
                    "metadata": {k: v for k, v in payload.items()
                               if k not in ["content", "source_url", "chunk_id",
                                          "chunk_index", "total_chunks", "chapter", "section"]}
                }
                contexts.append(context)

            logger.info(f"Successfully reconstructed context for {len(contexts)} chunks")
            return contexts

        except Exception as e:
            logger.error(f"Error reconstructing context for chunk IDs {chunk_ids}: {e}")
            # Fallback: try to get by searching for chunks with these IDs
            contexts = []
            all_records = self.vector_store.qdrant_client.scroll(
                collection_name=self.config.qdrant_collection_name,
                limit=10000  # Adjust limit as needed
            )[0]

            for chunk_id in chunk_ids:
                for record in all_records:
                    if record.payload.get("chunk_id") == chunk_id:
                        payload = record.payload
                        context = {
                            "source_url": payload.get("source_url", ""),
                            "content": payload.get("content", ""),
                            "chunk_id": payload.get("chunk_id", ""),
                            "chunk_index": payload.get("chunk_index"),
                            "total_chunks": payload.get("total_chunks"),
                            "chapter": payload.get("chapter"),
                            "section": payload.get("section"),
                            "metadata": {k: v for k, v in payload.items()
                                       if k not in ["content", "source_url", "chunk_id",
                                                  "chunk_index", "total_chunks", "chapter", "section"]}
                        }
                        contexts.append(context)
                        break

            logger.info(f"Successfully reconstructed context for {len(contexts)} chunks using fallback method")
            return contexts

    def search_by_metadata(self, metadata_filters: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for chunks based on metadata filters only (without semantic similarity).

        Args:
            metadata_filters: Dictionary of metadata filters to apply
            top_k: Maximum number of results to return

        Returns:
            List of dictionaries containing the filtered chunks
        """
        if not metadata_filters:
            logger.info("No metadata filters provided")
            return []

        try:
            from qdrant_client.http import models

            # Create filter conditions
            filter_conditions = []
            for key, value in metadata_filters.items():
                filter_conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    )
                )

            # Create the filter
            qdrant_filter = models.Filter(must=filter_conditions)

            # Search in Qdrant using the filter
            search_results = self.vector_store.qdrant_client.search(
                collection_name=self.config.qdrant_collection_name,
                query_filter=qdrant_filter,
                limit=top_k
            )

            # Format results
            results = []
            for result in search_results:
                chunk_data = {
                    "content": result.payload.get("content", ""),
                    "source_url": result.payload.get("source_url", ""),
                    "chunk_id": result.payload.get("chunk_id", ""),
                    "similarity_score": result.score,
                    "metadata": {k: v for k, v in result.payload.items()
                               if k not in ["content", "source_url", "chunk_id"]}
                }
                results.append(chunk_data)

            logger.info(f"Metadata-only search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error during metadata-only search: {e}")
            return []


def load_test_queries(file_path: str) -> List[Dict[str, Any]]:
    """
    Load test queries from a JSON file for validation.

    Args:
        file_path: Path to the JSON file containing test queries

    Returns:
        List of test query dictionaries
    """
    import json
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('queries', []) if isinstance(data, dict) else data
    except FileNotFoundError:
        logger.error(f"Test queries file not found: {file_path}")
        return [
            {"query": "What is Physical AI?", "expected_topic": "foundations"},
            {"query": "Humanoid robotics systems", "expected_topic": "humanoid"},
            {"query": "ROS 2 fundamentals", "expected_topic": "ros"},
            {"query": "Machine learning in robotics", "expected_topic": "ml"},
            {"query": "Sensor fusion techniques", "expected_topic": "sensors"}
        ]
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in test queries file: {file_path}")
        return []


def export_query_results(query: str, results: List[Dict[str, Any]], output_file: str) -> bool:
    """
    Export query results to a file for evaluation.

    Args:
        query: The original query text
        results: List of retrieved results
        output_file: Path to the output file

    Returns:
        bool: True if export was successful, False otherwise
    """
    import json
    try:
        import time
        export_data = {
            "query": query,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "result_count": len(results),
            "results": results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Query results exported to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error exporting query results to {output_file}: {e}")
        return False