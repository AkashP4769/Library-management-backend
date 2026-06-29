"""
Service layer for agent operations.

This module handles:
- Prompt processing and streaming
- Document uploads and RAG operations
- Cover image processing with ISBN extraction
"""

import logging
import shutil
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from agent.config import UPLOADS_DIR, ALLOWED_EXTENSIONS
from agent.rag_service import get_rag_service
from agent.isbn.pipeline import isbn_pipeline
from agent.schemas import (
    DocumentUploadRequest,
    DocumentUploadResponse,
    CoverUploadResponse,
)

logger = logging.getLogger(__name__)


async def process_prompt(db, agent, prompt: str) -> dict[str, Any]:
    """
    Process a user prompt through the agent.

    Args:
        db: Database session
        agent: LibraryAgent instance
        prompt: User's input prompt

    Returns:
        Dictionary with agent response content
    """
    try:
        logger.info("Processing prompt: %s", prompt[:100])
        content = await agent.process_prompt(db, prompt)
        return {"content": content}
    except Exception as e:
        logger.error("Prompt processing failed: %s", e)
        raise


async def stream_prompt(db, agent, prompt: str):
    """
    Stream agent responses for a prompt.

    Args:
        db: Database session
        agent: LibraryAgent instance
        prompt: User's input prompt

    Yields:
        Chunks of agent response as they become available
    """
    try:
        logger.info("Streaming prompt: %s", prompt[:100])
        async for chunk in agent.stream(prompt, db):
            yield f"{chunk}\n\n"
    except Exception as e:
        logger.error("Prompt streaming failed: %s", e)
        raise


async def upload_document(
    document: DocumentUploadRequest,
) -> DocumentUploadResponse:
    """
    Upload a document and index it in the vector store.

    Args:
        document: Document upload request with filename and content

    Returns:
        Response with success message

    Raises:
        ValueError: If document is invalid
        Exception: If upload or indexing fails
    """
    try:
        if not document.filename or not document.filename.strip():
            raise ValueError("Filename cannot be empty")

        if not document.content or not document.content.strip():
            raise ValueError("Document content cannot be empty")

        logger.info("Uploading document: %s", document.filename)

        # Use RAG service to handle document indexing
        rag_service = get_rag_service()
        result = rag_service.upload_document(document.filename, document.content)

        logger.info("Document uploaded: %s", document.filename)
        return DocumentUploadResponse(**result)

    except Exception as e:
        logger.error("Document upload failed: %s", e)
        raise


async def process_file_upload(file: UploadFile) -> Path:
    """
    Process a file upload to disk.

    Args:
        file: FastAPI UploadFile object

    Returns:
        Path to saved file

    Raises:
        ValueError: If file is invalid or too large
    """
    if not file.filename:
        raise ValueError("Filename is required")

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"File type '{file_ext}' not allowed. "
            f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        file_size_mb = 0
        file_path = UPLOADS_DIR / file.filename

        logger.info("Uploading file: %s", file.filename)

        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                file_size_mb += len(chunk) / (1024 * 1024)
                buffer.write(chunk)

        logger.info("File saved: %s", file_path)
        return file_path

    except Exception as e:
        logger.error("File upload failed: %s", e)
        if file_path.exists():
            file_path.unlink()
        raise


async def upload_cover(file: UploadFile) -> CoverUploadResponse:
    """
    Upload a book cover image and extract ISBN/metadata.

    Args:
        file: Cover image file

    Returns:
        Response with extracted book information

    Raises:
        ValueError: If file is invalid
        Exception: If processing fails
    """
    cover_path = None
    try:
        logger.info("Processing cover image: %s", file.filename)

        # Upload file to disk
        cover_path = await process_file_upload(file)

        # Extract ISBN and book metadata from image
        books = isbn_pipeline(str(cover_path))

        logger.info("Extracted %d books from cover image", len(books))
        return CoverUploadResponse(books=books)

    except Exception as e:
        logger.error("Cover upload failed: %s", e)
        raise
    finally:
        # Cleanup uploaded cover file
        if cover_path and cover_path.exists():
            try:
                cover_path.unlink()
                logger.info("Cleaned up cover file: %s", cover_path)
            except OSError as e:
                logger.warning("Failed to cleanup cover file: %s", e)
