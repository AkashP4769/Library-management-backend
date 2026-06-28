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
    # SAMPLE RETURN:
    #   retrieve_chunks(collection, query_embedding, n_results=2)
    #   →  [
    #       {"text": "Minimum attendance is 75%...", "source": "attendance_policy.txt",
    #        "chunk_id": "attendance_policy.txt_chunk_0", "distance": 0.4521},
    #       {"text": "Students whose attendance...", "source": "attendance_policy.txt",
    #        "chunk_id": "attendance_policy.txt_chunk_2", "distance": 0.6103},
    #   ]

    # TODO 1 — Call collection.query() with the embedding.
    # Note: query_embeddings expects a LIST of embeddings (batch interface).
    # Pass [query_embedding] (wrapped in a list) and n_results.
    # ---

    # TODO 2 — Parse ChromaDB's response format.
    # The response has shape: {"documents": [[...]], "metadatas": [[...]], "distances": [[...]]}
    # It's list-of-lists because the API supports multiple queries at once.
    # Since we pass one query, take index [0] from each.
    # ---

    # TODO 3 — Build and return the list of result dicts.
    # ---

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
    # SAMPLE RETURN:
    #   format_context([{"text": "Min attendance is 75%", "source": "attendance_policy.txt", ...}])
    #   →  "[Source: attendance_policy.txt]\nMin attendance is 75%\n---"

    # TODO 4 — Loop through chunks, format each as:
    #   "[Source: {source}]\n{text}\n---"
    #   Join them with newlines.
    # ---

    res = ""

    for chunk in chunks:
        res += f"[Source: {chunk['source']}\ntext: {chunk['text']}]---"

    return res
