from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..models.models import TextChunk
import uuid


class TextChunker:
    """
    A class to handle text chunking for embedding generation.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the text chunker with specified parameters.

        Args:
            chunk_size: Size of each text chunk (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def chunk_text(self, text: str, source_url: str, chapter: str = None, section: str = None) -> List[TextChunk]:
        """
        Chunk the provided text into smaller segments.

        Args:
            text: Text to be chunked
            source_url: URL where the text originated
            chapter: Chapter name (optional)
            section: Section name (optional)

        Returns:
            List[TextChunk]: List of TextChunk objects
        """
        if not text or len(text.strip()) == 0:
            return []

        # Split the text into chunks
        split_texts = self.splitter.split_text(text)

        # Create TextChunk objects
        chunks = []
        for i, chunk_text in enumerate(split_texts):
            chunk = TextChunk(
                id=str(uuid.uuid4()),
                content=chunk_text,
                source_url=source_url,
                chapter=chapter,
                section=section,
                chunk_index=i,
                total_chunks=len(split_texts)
            )
            chunks.append(chunk)

        return chunks

    def chunk_book_content(self, book_content_list) -> List[TextChunk]:
        """
        Chunk a list of BookContent objects.

        Args:
            book_content_list: List of BookContent objects

        Returns:
            List[TextChunk]: List of TextChunk objects
        """
        all_chunks = []
        for content in book_content_list:
            chunks = self.chunk_text(
                content.content,
                content.url,
                content.chapter,
                content.section
            )
            all_chunks.extend(chunks)

        return all_chunks


def chunk_text(text: str, source_url: str, chunk_size: int = 1000, chunk_overlap: int = 200,
               chapter: str = None, section: str = None) -> List[TextChunk]:
    """
    Convenience function to chunk text.

    Args:
        text: Text to be chunked
        source_url: URL where the text originated
        chunk_size: Size of each text chunk (default: 1000)
        chunk_overlap: Overlap between chunks (default: 200)
        chapter: Chapter name (optional)
        section: Section name (optional)

    Returns:
        List[TextChunk]: List of TextChunk objects
    """
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_text(text, source_url, chapter, section)