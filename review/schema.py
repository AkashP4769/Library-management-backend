"""
Pydantic schemas for Review.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreateRequest(BaseModel):
    isbn: str
    content: str | None = None
    rating: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )


class ReviewUpdateRequest(BaseModel):
    content: str | None = None
    rating: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    isbn: str
    content: str | None
    rating: float | None
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None


class ReviewListResponse(BaseModel):
    reviews: list[ReviewResponse]


class ReviewBookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    isbn: str
    name: str
    user_id: int
    content: str | None
    rating: float | None
    created_at: datetime
    updated_at: datetime | None
