from typing import Any


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split a single document's text into overlapping character-level chunks.

    Args:
        text: The full text content of a single document.
        chunk_size: Maximum number of characters per chunk.
        overlap: Number of characters that overlap between consecutive chunks.

    Returns:
        A list of text chunks (strings), each at most chunk_size characters long.

    """

    chunks: list[str] = []
    left, right = 0, chunk_size

    while right <= len(text):
        chunk = text[left:right]
        chunks.append(chunk)

        left = right - overlap
        right += chunk_size - overlap

    # last item
    right = left
    while right <= len(text) - 1:
        right += 1

    chunk = text[left:right]
    if chunk != "":
        chunks.append(chunk)

    return chunks


def chunk_all_documents(
    documents: dict[str, str],
    chunk_size: int = 300,
    overlap: int = 50,
) -> list[dict[str, str]]:
    """Apply chunking to every document and tag each chunk with its source.

    Args:
        documents: Dictionary mapping filename → full text (output of load_documents).
        chunk_size: Maximum characters per chunk (passed to chunk_text).
        overlap: Overlap characters between chunks (passed to chunk_text).

    Returns:
        A list of dictionaries, each with keys:
            - "text": the chunk content (str)
            - "source": the filename it came from (str)
            - "chunk_id": a unique identifier like "college_handbook.txt_chunk_0" (str)

    """

    res: list[dict[str, str]] = []

    for filename, text in documents.items():
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        print("len of chunks: ", len(chunks))

        for idx, chunk in enumerate(chunks):
            chunk_data = {}
            chunk_data["text"] = chunk
            chunk_data["source"] = filename
            chunk_data["chunk_id"] = f"{filename}_chunk_{idx}"

            res.append(chunk_data)

    return res


# EMBEDDING


def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> Any:
    """Load a SentenceTransformer model for generating embeddings.

    Args:
        model_name: The HuggingFace model identifier to load.
            Defaults to "all-MiniLM-L6-v2" (384-dimensional embeddings).

    Returns:
        A loaded SentenceTransformer model object ready to encode text.

    """

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

    encoded_embedding = model.encode(query)
    encoded_embedding_as_list = encoded_embedding.tolist()

    return encoded_embedding_as_list


# retrieval
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
