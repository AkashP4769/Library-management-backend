"""
Business logic for Book.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from book import repo
from book.schemas import BookCreateRequest, BookUpdateRequest
from models.book import Book


async def create_book(
    
    db: AsyncSession,
    payload: BookCreateRequest,
) -> Book:

    existing = await repo.get_by_isbn(db, payload.isbn)

    if existing:
        raise ValueError("Book with this ISBN already exists.")

    return await repo.create(db, payload)

async def get_book(
   
    db: AsyncSession,
    book_id: int,
) -> Book:

    book = await repo.get_by_id(db, book_id)

    if not book:
        raise ValueError("Book not found.")

    return book

async def get_books(
    
    db: AsyncSession,
) -> list[Book]:

    return await repo.get_all(db)

async def get_by_isbn(
    
    db: AsyncSession,
    isbn: str,
) -> Book:
    book = await repo.get_by_isbn(db, isbn)

    if not book:
        raise ValueError("Book not found.")

    return book
async def update_book(
    
    db: AsyncSession,
    book_id: int,
    payload: BookUpdateRequest,
) -> Book:

    book = await repo.get_by_id(db, book_id)

    if not book:
        raise ValueError("Book not found.")

    if payload.isbn:

        existing = await repo.get_by_isbn(db, payload.isbn)

        if existing and existing.id != book.id:
            raise ValueError("ISBN already exists.")

    return await repo.update(
        db,
        book,
        payload,
    )

async def delete_book(
    
    db: AsyncSession,
    book_id: int,
) -> None:

    book = await repo.get_by_id(db, book_id)

    if not book:
        raise ValueError("Book not found.")

    await repo.delete(
        db,
        book,
    )