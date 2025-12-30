#!/usr/bin/env python3
"""
Script to clear the Qdrant collection before re-ingesting with updated content extraction
"""
import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config import get_config

def clear_qdrant_collection():
    """Clear the Qdrant collection to start fresh with updated content extraction."""
    config = get_config()

    # Connect to Qdrant
    client = QdrantClient(
        url=config.qdrant_host,
        api_key=config.qdrant_api_key,
        https=True
    )

    collection_name = config.qdrant_collection_name

    print(f"Connecting to Qdrant collection: {collection_name}")

    try:
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]

        if collection_name in collection_names:
            print(f"Deleting existing collection: {collection_name}")
            client.delete_collection(collection_name)
            print(f"Collection {collection_name} deleted successfully")
        else:
            print(f"Collection {collection_name} does not exist, will be created fresh")

        # Create a new collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)  # Assuming Cohere embeddings
        )
        print(f"New collection {collection_name} created successfully")

        # Verify the collection exists and is empty
        collection_info = client.get_collection(collection_name)
        print(f"Collection info: {collection_info}")
        print(f"Points count: {collection_info.points_count}")

    except Exception as e:
        print(f"Error managing Qdrant collection: {e}")
        return False

    return True

if __name__ == "__main__":
    success = clear_qdrant_collection()
    if success:
        print("Qdrant collection cleared successfully. Ready for fresh ingestion.")
    else:
        print("Failed to clear Qdrant collection.")
        sys.exit(1)