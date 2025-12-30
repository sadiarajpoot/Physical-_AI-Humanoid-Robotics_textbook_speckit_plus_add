from typing import List, Dict, Any, Optional
from models import Embedding
from logger import logger
import json
import os
from pathlib import Path


class Resumer:
    """
    A class to handle resuming interrupted ingestion processes.
    """
    def __init__(self, resume_file: str = "ingestion_state.json"):
        """
        Initialize the resumer with a state file.

        Args:
            resume_file: Path to the file that stores ingestion state
        """
        self.resume_file = resume_file
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """
        Load the ingestion state from file.

        Returns:
            Dict: Ingestion state
        """
        if os.path.exists(self.resume_file):
            try:
                with open(self.resume_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load resume state from {self.resume_file}: {e}")
                return self._get_default_state()
        else:
            return self._get_default_state()

    def _get_default_state(self) -> Dict[str, Any]:
        """
        Get the default ingestion state.

        Returns:
            Dict: Default ingestion state
        """
        return {
            "last_processed_url": None,
            "processed_urls": [],
            "stored_embeddings_count": 0,
            "total_embeddings_to_process": 0,
            "ingestion_completed": False
        }

    def _save_state(self):
        """
        Save the current ingestion state to file.
        """
        try:
            with open(self.resume_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.info(f"Ingestion state saved to {self.resume_file}")
        except Exception as e:
            logger.error(f"Could not save resume state to {self.resume_file}: {e}")

    def update_last_processed_url(self, url: str):
        """
        Update the last processed URL in the state.

        Args:
            url: URL that was last processed
        """
        self.state["last_processed_url"] = url
        self.state["processed_urls"].append(url)
        self._save_state()

    def update_stored_embeddings_count(self, count: int):
        """
        Update the count of stored embeddings in the state.

        Args:
            count: Number of embeddings stored
        """
        self.state["stored_embeddings_count"] = count
        self._save_state()

    def set_total_embeddings_to_process(self, count: int):
        """
        Set the total number of embeddings to process.

        Args:
            count: Total number of embeddings to process
        """
        self.state["total_embeddings_to_process"] = count
        self._save_state()

    def mark_ingestion_completed(self):
        """
        Mark the ingestion process as completed.
        """
        self.state["ingestion_completed"] = True
        self._save_state()

    def get_state(self) -> Dict[str, Any]:
        """
        Get the current ingestion state.

        Returns:
            Dict: Current ingestion state
        """
        return self.state.copy()

    def should_resume(self) -> bool:
        """
        Check if the ingestion should resume from the last state.

        Returns:
            bool: True if ingestion should resume
        """
        return not self.state.get("ingestion_completed", False)

    def get_resume_point(self) -> Optional[str]:
        """
        Get the URL to resume from.

        Returns:
            str: URL to resume from, or None if starting fresh
        """
        return self.state.get("last_processed_url")

    def get_processed_urls(self) -> List[str]:
        """
        Get the list of already processed URLs.

        Returns:
            List[str]: List of processed URLs
        """
        return self.state.get("processed_urls", [])

    def get_stored_count(self) -> int:
        """
        Get the count of already stored embeddings.

        Returns:
            int: Number of stored embeddings
        """
        return self.state.get("stored_embeddings_count", 0)

    def reset_state(self):
        """
        Reset the ingestion state to default.
        """
        self.state = self._get_default_state()
        self._save_state()

    def filter_already_processed(self, embeddings: List[Embedding], book_content) -> List[Embedding]:
        """
        Filter out embeddings that have already been processed.

        Args:
            embeddings: List of embeddings to filter
            book_content: List of book content to reference

        Returns:
            List[Embedding]: List of embeddings that haven't been processed yet
        """
        processed_urls = set(self.get_processed_urls())
        filtered_embeddings = []

        for embedding in embeddings:
            if embedding.text_chunk.source_url not in processed_urls:
                filtered_embeddings.append(embedding)

        logger.info(f"Filtered out {len(embeddings) - len(filtered_embeddings)} already processed embeddings")
        return filtered_embeddings


def create_resumer(resume_file: str = "ingestion_state.json") -> Resumer:
    """
    Convenience function to create a Resumer instance.

    Args:
        resume_file: Path to the file that stores ingestion state

    Returns:
        Resumer: Resumer instance
    """
    return Resumer(resume_file)