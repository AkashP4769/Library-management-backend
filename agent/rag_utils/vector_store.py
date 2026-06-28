"""
Vector Store Module for the IITD Helpdesk RAG Pipeline.

This module manages ChromaDB — our persistent vector database. ChromaDB stores
three things together for each chunk: the raw text, its embedding vector, and
metadata (which file it came from, its chunk ID).
"""

from typing import Any
import chromadb


def get_chroma_client(persist_directory: str = "chroma_db") -> Any:
    """Initialise and return a persistent ChromaDB client.

    Args:
        persist_directory: Path to the directory where ChromaDB stores its files.
            Defaults to "chroma_db" in the project root.

    Returns:
        A ChromaDB PersistentClient instance.

    """
    # SAMPLE RETURN:
    #   client = get_chroma_client("chroma_db")
    #   →  <chromadb.PersistentClient object>

    # TODO 1 — Create and return a ChromaDB persistent client.
    # Import chromadb, then use chromadb.PersistentClient(path=persist_directory).
    # ---

    client = chromadb.PersistentClient(path=persist_directory)

    return client


def create_collection(client: any, collection_name: str = "dholakpur_helpdesk") -> Any:
    """Create or retrieve a named ChromaDB collection.

    Args:
        client: A ChromaDB client instance (from get_chroma_client).
        collection_name: Name for the vector collection.
            Defaults to "dholakpur_helpdesk".

    Returns:
        A ChromaDB Collection object.

    """
    # SAMPLE RETURN:
    #   collection = create_collection(client, "dholakpur_helpdesk")
    #   →  <chromadb.Collection object>

    # TODO 2 — Use an idempotent method to get or create the collection.
    # client.get_or_create_collection(name=...) won't fail if it already exists.
    # ---

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
    # After calling add_chunks(collection, chunks, embeddings):
    #   collection.count()  →  len(chunks)

    # TODO 3 — Extract texts, ids, and metadata from the chunks list.
    # ---

    # TODO 4 — Add everything to the collection in one call.
    # The collection.add() method needs: ids, documents, embeddings, metadatas.
    # ---

    ids = [chunk["chunk_id"] for chunk in chunks]
    metadatas = [{"filename": chunk["source"]} for chunk in chunks]
    texts = [chunk["text"] for chunk in chunks]
    # text = [chunk["text"] for chunk in chunks]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
