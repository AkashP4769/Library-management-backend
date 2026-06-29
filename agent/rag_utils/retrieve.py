"""
Retrieval Module for the IITD Helpdesk RAG Pipeline.

This module handles the "R" in RAG — Retrieval. Given a student's question
(as an embedding vector), it searches ChromaDB for the most semantically
similar document chunks.
"""

from typing import Any


def retrieve_chunks(
    collection: Any,
    query_embedding: list[float],
    n_results: int = 5,
) -> list[dict[str, Any]]:
    """Query ChromaDB for the top-n most similar chunks to a query.

    Args:
        collection: A ChromaDB Collection containing indexed document chunks.
        query_embedding: The embedding vector of the user's question.
        n_results: How many chunks to retrieve.

    Returns:
        A list of dictionaries, each containing:
            - "text": the chunk content
            - "source": the source filename
            - "chunk_id": the unique chunk identifier
            - "distance": the similarity distance (lower = more similar)

    """

    query_result = collection.query(
        query_embeddings=[query_embedding], n_results=n_results
    )

    ids = query_result["ids"][0]
    documents = query_result["documents"][0]
    metadatas = query_result["metadatas"][0]
    distances = query_result["distances"][0]

    res = [
        {
            "text": documents[i],
            "source": metadatas[i]["filename"],
            "chunk_id": ids[i],
            "distance": distances[i],
        }
        for i in range(len(documents))
    ]

    return res


def format_context(chunks: list[dict[str, Any]]) -> str:
    """Format retrieved chunks into a single context string for the LLM prompt.

    Args:
        chunks: List of retrieved chunk dictionaries (from retrieve_chunks).

    Returns:
        A single formatted string containing all chunk texts with source
        attribution, separated by dividers.

    """

    res = ""

    for chunk in chunks:
        res += f"[Source: {chunk['source']}\ntext: {chunk['text']}]---"

    return res
