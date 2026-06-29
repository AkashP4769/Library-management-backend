"""
Pydantic schemas for Book.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    isbn: str = Field(..., max_length=20)
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    genre: str | None = Field(default=None, max_length=100)
    publisher: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, max_length=50)
    description: str | None = None
    links: str | None = None


class BookCreateRequest(BookBase):
    """Schema used to create a new book."""

    pass


class BookUpdateRequest(BaseModel):
    """Schema used to update an existing book."""

    isbn: str | None = Field(default=None, max_length=20)
    title: str | None = Field(default=None, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    genre: str | None = Field(default=None, max_length=100)
    publisher: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, max_length=50)
    description: str | None = None
    links: str | None = None


class BookResponse(BookBase):
    """Schema returned by the API."""

    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class BookAPIResponse(BaseModel):
    """Schema returned by OpenLibrary API"""
    isbn: str = Field(..., max_length=20)
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    pages:str | None = Field(default=None, max_length=255)
    publisher: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, max_length=50)
    cover_urls: list[str | None] | None = None
