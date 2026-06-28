import json

from fastapi import APIRouter


from fastapi import Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from agent.employee_agent import get_agent
from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from database.connection import get_db

import agent.service as service

from agent.schemas import (
    AgentMessage,
    AgentResponse,
    DocumentUploadRequest,
    DocumentUploadResponse,
)


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/prompt", response_model=AgentResponse)
async def process_prompt(
    body: AgentMessage,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
) -> AgentResponse:

    agent = get_agent(_current_user.id)
    return await service.process_prompt(db, agent, body.prompt)


@router.post("/stream", response_model=AgentResponse)
async def stream_prompt(
    body: AgentMessage,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
) -> AgentResponse:

    agent = get_agent(_current_user.id)

    async def event_generator():
        async for chunk in service.stream_prompt(
            db,
            agent,
            body.prompt,
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(
    document: DocumentUploadRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
) -> DocumentUploadResponse:

    return await service.upload_document(db, document)
