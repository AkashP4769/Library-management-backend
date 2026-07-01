"""
Pydantic schemas for Book.
"""

from datetime import datetime

from fastapi import File, Form, Form, UploadFile
from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    isbn: str = (Form(...),)
    title: str = (Form(...),)
    author: str = (Form(...),)
    genre: str = (Form(""),)
    publisher: str = (Form(""),)
    language: str = (Form(""),)
    description: str = (Form(""),)
    image_url: str | None = None


class BookCreateRequest(BaseModel):
    isbn: str
    title: str
    author: str
    genre: str = ""
    publisher: str = ""
    language: str = ""
    description: str = ""
    image: UploadFile | None = None
    image_url: str | None = None

    @classmethod
    def as_form(
        cls,
        isbn: str = Form(...),
        title: str = Form(...),
        author: str = Form(...),
        genre: str = Form(""),
        publisher: str = Form(""),
        language: str = Form(""),
        description: str = Form(""),
        image: UploadFile | None = File(None),
        image_url: str | None = Form(None),
    ):
        return cls(
            isbn=isbn,
            title=title,
            author=author,
            genre=genre,
            publisher=publisher,
            language=language,
            description=description,
            image=image,
            image_url=image_url,
        )


class BookUpdateRequest(BaseModel):
    """Schema used to update an existing book."""

    isbn: str | None = Field(default=None, max_length=20)
    title: str | None = Field(default=None, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    genre: str | None = Field(default=None, max_length=100)
    publisher: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, max_length=50)
    description: str | None = None
    image_url: str | None = None


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
    pages: str | None = Field(default=None, max_length=255)
    publisher: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, max_length=50)
    cover_urls: list[str | None] | None = None


class RequestedBookCopySchema(BaseModel):
    id: int
    status: str
    book: BookResponse

    model_config = ConfigDict(from_attributes=True)
