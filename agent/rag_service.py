"""
RAG (Retrieval-Augmented Generation) service for document processing.

This module provides a unified interface for:
- Document chunking and embedding
- Vector store operations
- Context retrieval for prompts
"""

import logging
from typing import Optional

from agent.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    COLLECTION_NAME,
)
from agent.rag_utils import (
    chunk_all_documents,
    load_embedding_model,
    embed_texts,
    embed_query,
    get_chroma_client,
    create_collection,
    add_chunks,
    retrieve_chunks,
    format_context,
)

logger = logging.getLogger(__name__)


class RAGService:
    """Service for managing RAG operations with vector stores."""

    def __init__(self):
        """Initialize RAG service with embedding model and vector store."""
        self._embedding_model = None
        self._chroma_client = None

    @property
    def embedding_model(self):
        """Lazy load embedding model."""
        if self._embedding_model is None:
            logger.info("Loading embedding model...")
            self._embedding_model = load_embedding_model()
        return self._embedding_model

    @property
    def chroma_client(self):
        """Lazy load Chroma client."""
        if self._chroma_client is None:
            logger.info("Initializing Chroma client...")
            self._chroma_client = get_chroma_client()
        return self._chroma_client

    def upload_document(
        self,
        filename: str,
        content: str,
    ) -> dict[str, str]:
        """
        Upload and process a document into vector store.

        Args:
            filename: Name of the document file
            content: Document text content

        Returns:
            dict with success message

        Raises:
            ValueError: If content is empty
            Exception: If embedding or storage fails
        """
        if not content or not content.strip():
            raise ValueError("Document content cannot be empty")

        try:
            logger.info(f"Processing document: {filename}")

            # Chunk document
            chunks = chunk_all_documents(
                documents={filename: content},
                chunk_size=CHUNK_SIZE,
                overlap=CHUNK_OVERLAP,
            )
            logger.info(f"Created {len(chunks)} chunks")

            # Embed chunks
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = embed_texts(self.embedding_model, chunk_texts)
            logger.info(f"Embedded {len(embeddings)} chunks")

            # Store in vector database
            collection = create_collection(
                self.chroma_client,
                COLLECTION_NAME,
            )
            add_chunks(collection, chunks, embeddings)
            logger.info("Chunks stored in vector database")

            return {"message": f"Document '{filename}' uploaded successfully"}

        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            raise

    def search_documents(self, query: str, n_results: int = 5) -> str:
        """
        Search documents using semantic similarity.

        Args:
            query: Natural language search query
            n_results: Number of results to retrieve

        Returns:
            Formatted context string with relevant passages

        Raises:
            ValueError: If query is empty
            Exception: If search fails
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        try:
            logger.info(f"Searching documents: {query[:100]}...")

            # Embed query
            query_embedding = embed_query(self.embedding_model, query)

            # Retrieve similar chunks
            collection = create_collection(
                self.chroma_client,
                COLLECTION_NAME,
            )
            results = retrieve_chunks(
                collection,
                query_embedding,
                n_results=n_results,
            )

            # Format results
            context = format_context(results)
            logger.info(f"Retrieved {len(results)} relevant chunks")

            return context

        except Exception as e:
            logger.error(f"Document search failed: {e}")
            raise

    def clear_documents(self) -> dict[str, str]:
        """
        Clear all documents from vector store.

        Returns:
            dict with success message
        """
        try:
            logger.info("Clearing document collection")
            client = self.chroma_client
            client.delete_collection(name=COLLECTION_NAME)
            logger.info("Document collection cleared")
            return {"message": "All documents cleared successfully"}
        except Exception as e:
            logger.error(f"Failed to clear documents: {e}")
            raise


# Singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get or create singleton RAG service instance.

    Returns:
        RAGService instance
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
