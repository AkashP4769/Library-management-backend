"""
Vector Store Module for the IITD Helpdesk RAG Pipeline.

This module manages ChromaDB — our persistent vector database. ChromaDB stores
three things together for each chunk: the raw text, its embedding vector, and
metadata (which file it came from, its chunk ID).
"""

from typing import Any
import chromadb


def get_chroma_client(persist_directory: str = "agent/storage/chroma_db") -> Any:
    """Initialise and return a persistent ChromaDB client.

    Args:
        persist_directory: Path to the directory where ChromaDB stores its files.
            Defaults to "chroma_db" in the project root.

    Returns:
        A ChromaDB PersistentClient instance.

    """

    client = chromadb.PersistentClient(path=persist_directory)

    return client


def create_collection(client: any, collection_name: str = "lumina_helpdesk") -> Any:
    """Create or retrieve a named ChromaDB collection.

    Args:
        client: A ChromaDB client instance (from get_chroma_client).
        collection_name: Name for the vector collection.
            Defaults to "lumina_helpdesk".

    Returns:
        A ChromaDB Collection object.

    """
    collection = client.get_or_create_collection(name=collection_name)

    return collection


def add_chunks(
    collection: Any,
    chunks: list[dict[str, str]],
    embeddings: list[list[float]],
) -> None:
    """Add document chunks with their embeddings and metadata to the collection.

    Args:
        collection: A ChromaDB Collection (from create_collection).
        chunks: List of chunk dictionaries, each with "text", "source", "chunk_id".
        embeddings: Corresponding embedding vectors (same order as chunks).

    Returns:
        None. Chunks are added to the collection as a side effect.

    """

    ids = [chunk["chunk_id"] for chunk in chunks]
    metadatas = [{"filename": chunk["source"]} for chunk in chunks]
    texts = [chunk["text"] for chunk in chunks]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
