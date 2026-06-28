from agent.schemas import DocumentUploadRequest, DocumentUploadResponse
from agent.rag_utils import chunk_all_documents
from agent.rag_utils import load_embedding_model, embed_texts, embed_query
from agent.rag_utils import get_chroma_client, create_collection, add_chunks
from agent.rag_utils import retrieve_chunks, format_context


async def process_prompt(db, agent, prompt: str) -> dict[str:any]:
    content = await agent.process_prompt(db, prompt)
    return {"content": content}


async def stream_prompt(db, agent, prompt):
    async for chunk in agent.stream(prompt, db):
        # splitted_chunks = chunk.split('\n')
        yield chunk


async def upload_document(
    db, document: DocumentUploadRequest
) -> DocumentUploadResponse:

    chunks = chunk_all_documents(
        documents={document.filename: document.content},
        chunk_size=300,
        overlap=50,
    )

    embedding_model = load_embedding_model()
    embedded_texts_vector = embed_texts(
        embedding_model, [chunk["text"] for chunk in chunks]
    )

    chroma_client = get_chroma_client()
    collection = create_collection(chroma_client, "documents")
    add_chunks(collection, chunks, embedded_texts_vector)

    return {"message": "Document uploaded successfully"}


def search_in_documents(query: str) -> str:
    embedding_model = load_embedding_model()
    query_embedding = embed_query(embedding_model, query)

    chroma_client = get_chroma_client()
    collection = create_collection(chroma_client, "documents")

    results = retrieve_chunks(collection, query_embedding, n_results=5)
    context = format_context(results)

    return context
