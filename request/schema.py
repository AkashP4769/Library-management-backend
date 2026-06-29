"""
Pydantic schemas for Request.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.requests import RequestStatus


class RequestCreateRequest(BaseModel):
    requester_id: int
    borrowed_books_id: int
    isbn: str


class RequestUpdateRequest(BaseModel):
    status: RequestStatus


class RequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requester_id: int
    borrowed_books_id: int
    isbn: str
    status: RequestStatus
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    resolved_at: datetime | None