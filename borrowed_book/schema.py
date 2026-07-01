"""
Pydantic schemas for BorrowedBook.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.borrowed_book import BorrowStatus


class BorrowBookRequest(BaseModel):
    isbn: str
    shelf_id: int


class BorrowedBookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_copy_id: int
    user_id: int
    borrowed_at: datetime
    due_date: datetime
    returned_at: datetime | None
    status: BorrowStatus
    renewal_count: int
    fine_amount: float
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None


class BorrowedBookListResponse(BaseModel):
    borrowed_books: list[BorrowedBookResponse]


class BorrowedBookDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int
    user_name: str
    user_email: str

    book_copy_id: int
    book_id: int

    isbn: str
    title: str
    author: str
    genre: str | None = None
    image_url: str | None = None
    publisher: str | None = None
    language: str | None = None

    shelf_id: int
    shelf_code: str
    office_location: str | None = None

    borrowed_at: datetime
    due_date: datetime
    returned_at: datetime | None

    status: BorrowStatus
    renewal_count: int
    fine_amount: float
    created_at: datetime
    updated_at: datetime | None = None


class BorrowedBookDetailsListResponse(BaseModel):
    borrowed_books: list[BorrowedBookDetailsResponse]
