"""
Repository layer for Book.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.book import Book
from book.schemas import BookCreateRequest, BookUpdateRequest
async def create(
    db: AsyncSession,
    payload: BookCreateRequest,
) -> Book:
    book = Book(**payload.model_dump())

    db.add(book)
    await db.commit()
    await db.refresh(book)

    return book

async def get_by_id(
    
    db: AsyncSession,
    book_id: int,
) -> Book | None:

    result = await db.execute(
        select(Book).where(
            Book.id == book_id,
            Book.deleted_at.is_(None),
        )
    )

    return result.scalar()

async def get_by_isbn(
    
    db: AsyncSession,
    isbn: str,
) -> Book | None:

    result = await db.execute(
        select(Book).where(
            Book.isbn == isbn,
            Book.deleted_at.is_(None),
        )
    )

    return result.scalar()

async def get_all(
    
    db: AsyncSession,
) -> list[Book]:

    result = await db.execute(
        select(Book).where(
            Book.deleted_at.is_(None)
        )
    )

    return result.scalars().all()

async def update(
    
    db: AsyncSession,
    book: Book,
    payload: BookUpdateRequest,
) -> Book:

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, key, value)

    await db.commit()
    await db.refresh(book)

    return book

async def delete(
    
    db: AsyncSession,
    book: Book,
) -> None:

    book.deleted_at = datetime.utcnow()

    await db.commit()