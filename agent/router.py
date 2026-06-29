"""API routes for agent operations.

Endpoints for:
- Processing prompts
- Streaming responses
- Uploading documents
- Processing book covers
"""

import json
import logging
from typing import Any

from fastapi import Depends, APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from agent.library_agent import get_agent
from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from database.connection import get_db
from agent import service
from agent.schemas import (
    AgentMessage,
    AgentResponse,
    DocumentUploadRequest,
    DocumentUploadResponse,
    CoverUploadResponse,
)

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/prompt", response_model=AgentResponse)
async def process_prompt(
    body: AgentMessage,
    db: AsyncSession = Depends(get_db),
    # _current_user: TokenPayload = Depends(get_current_user),
) -> AgentResponse:
    """
    Process a user prompt through the agent.

    Args:
        body: User's prompt and metadata
        db: Database session

    Returns:
        Agent's response to the prompt

    Raises:
        HTTPException: If prompt processing fails
    """
    try:
        agent = get_agent()
        response = await service.process_prompt(db, agent, body.prompt)
        return AgentResponse(**response)
    except ValueError as e:
        logger.warning(f"Invalid prompt: {e}")
        raise
    except Exception as e:
        logger.error(f"Prompt processing error: {e}")
        raise


@router.post("/stream", response_model=AgentResponse)
async def stream_prompt(
    body: AgentMessage,
    db: AsyncSession = Depends(get_db),
    # _current_user: TokenPayload = Depends(get_current_user),
) -> StreamingResponse:
    """
    Stream agent response for a prompt in real-time.

    Args:
        body: User's prompt and metadata
        db: Database session

    Returns:
        Server-Sent Events stream of response chunks

    Raises:
        HTTPException: If streaming fails
    """

    async def event_generator():
        """Generate SSE events for streaming response."""
        try:
            agent = get_agent()
            async for chunk in service.stream_prompt(db, agent, body.prompt):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(
    document: DocumentUploadRequest,
    db: AsyncSession = Depends(get_db),
    # _current_user: TokenPayload = Depends(get_current_user),
) -> DocumentUploadResponse:
    """
    Upload a document to the knowledge base.

    Args:
        document: Document with filename and content
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If upload fails
    """
    try:
        result = await service.upload_document(db, document)
        return result
    except ValueError as e:
        logger.warning(f"Invalid document: {e}")
        raise
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise


@router.post("/cover", response_model=CoverUploadResponse)
async def upload_cover(
    cover_page: UploadFile = File(...),
    _current_user: TokenPayload = Depends(get_current_user),
) -> CoverUploadResponse:
    """
    Upload a book cover image and extract ISBN/metadata.

    Args:
        cover_page: Book cover image file
        db: Database session

    Returns:
        Extracted book information

    Raises:
        HTTPException: If cover processing fails
    """
    try:
        result = await service.upload_cover(cover_page)
        return result
    except ValueError as e:
        logger.warning(f"Invalid cover file: {e}")
        raise
    except Exception as e:
        logger.error(f"Cover upload error: {e}")
        raise
