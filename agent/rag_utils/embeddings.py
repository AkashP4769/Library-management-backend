"""
Embedding Module for the IITD Helpdesk RAG Pipeline.

This module converts text into numerical vectors (embeddings) that capture
semantic meaning. Texts with similar meanings end up at nearby coordinates
in a high-dimensional space, enabling semantic search.
"""

from typing import Any


def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> Any:
    """Load a SentenceTransformer model for generating embeddings.

    Args:
        model_name: The HuggingFace model identifier to load.
            Defaults to "all-MiniLM-L6-v2" (384-dimensional embeddings).

    Returns:
        A loaded SentenceTransformer model object ready to encode text.

    """
    # SAMPLE RETURN:
    #   model = load_embedding_model()
    #   →  <SentenceTransformer object>

    # TODO 1 — Import and instantiate SentenceTransformer with model_name.
    # from sentence_transformers import SentenceTransformer, then return the instance.
    # ---

    from sentence_transformers import SentenceTransformer
    # import torch

    # print("cuda avail: ", torch.cuda.is_available())

    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    return model


def embed_texts(model: Any, texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of text strings.

    Args:
        model: A loaded SentenceTransformer model (from load_embedding_model).
        texts: A list of text strings to embed (typically our document chunks).

    Returns:
        A list of embedding vectors, where each vector is a list of 384 floats.
        The order matches the input texts — embeddings[i] corresponds to texts[i].

    """
    # SAMPLE RETURN:
    #   embed_texts(model, ["hello", "world"])
    #   →  [[0.0123, -0.0456, ..., 0.0789],   ← 384 floats
    #       [0.0321, -0.0654, ..., 0.0987]]

    # TODO 2 — Encode the texts using the model and return as a Python list.
    # Note: model.encode() returns a numpy array — ChromaDB and JSON need
    # plain Python lists. Check numpy docs for array → list conversion.
    # ---

    # import numpy as np

    embeddings = []

    for text in texts:
        encoded_embedding = model.encode(text)
        encoded_embedding_as_list = encoded_embedding.tolist()

        embeddings.append(encoded_embedding_as_list)

    return embeddings


def embed_query(model: Any, query: str) -> list[float]:
    """Embed a single query string for retrieval.

    Args:
        model: A loaded SentenceTransformer model (from load_embedding_model).
        query: A single question or search string from the user.

    Returns:
        A single embedding vector (list of 384 floats) for the query.

    """
    # SAMPLE RETURN:
    #   embed_query(model, "What is the attendance policy?")
    #   →  [0.0123, -0.0456, ..., 0.0789]   ← 384 floats

    # TODO 3 — Encode the single query string and return as a Python list.
    # Same approach as embed_texts but for a single string.
    # ---

    encoded_embedding = model.encode(query)
    encoded_embedding_as_list = encoded_embedding.tolist()

    return encoded_embedding_as_list
