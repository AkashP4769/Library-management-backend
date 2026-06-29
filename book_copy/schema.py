from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class BookCopyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    LOST = "LOST"
    DAMAGED = "DAMAGED"


class BookCopyCreateRequest(BaseModel):
    isbn: str
    shelf_id: int
    


class BookCopyUpdateRequest(BaseModel):
    shelf_id: int | None = None
    
    status: BookCopyStatus | None = None

class BookCopyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    isbn: str
    shelf_id: int
    
    status: BookCopyStatus
    created_at: datetime
    updated_at: datetime


class BookCopyStatisticsResponse(BaseModel):
    total: int
    available: int
    borrowed: int
    damaged: int
    lost: int