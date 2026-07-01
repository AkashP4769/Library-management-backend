
from datetime import datetime

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict, Field


class ShelfBase(BaseModel):
    shelf_code: str = Field(..., max_length=50)
    office_location: str = Field(..., max_length=255)
    capacity: int = Field(..., ge=1)
    image_url: str | None = None


class ShelfCreateRequest(BaseModel):
    shelf_code: str = Field(..., max_length=50)
    office_location: str = Field(..., max_length=255)
    capacity: int = Field(..., ge=1)
    image: UploadFile | None = None
    image_url: str | None = None

    @classmethod
    def as_form(
        cls,
        shelf_code: str = Form(..., max_length=50),
        office_location: str = Form(..., max_length=255),
        capacity: int = Form(..., ge=1),
        image: UploadFile | None = File(None),
        image_url: str | None = Form(None),
    ):
        return cls(
            shelf_code=shelf_code,
            office_location=office_location,
            capacity=capacity,
            image=image,
            image_url=image_url,
        )


class ShelfUpdateRequest(BaseModel):
    shelf_code: str | None = Field(default=None, max_length=50)
    office_location: str | None = Field(default=None, max_length=255)
    capacity: int | None = Field(default=None, ge=1)
    image: UploadFile | None = None


class ShelfResponse(ShelfBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    image_url: str | None = None


class ShelfListResponse(BaseModel):
    shelves: list[ShelfResponse]

class ShelfBookResponse(BaseModel):
    isbn: str
    title: str
    author: str
    genre: str
    publisher: str
    language: str
    description: str | None
    image_url: str | None

    total_copies: int
    available_copies: int
    borrowed_copies: int

    average_rating: float | None