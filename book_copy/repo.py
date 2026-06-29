"""
Database operations for Book Copy.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from book_copy.schema import BookCopyCreateRequest, BookCopyUpdateRequest
from models.book_copy import BookCopy, BookCopyStatus


async def create_book_copy(
    db: AsyncSession,
    payload: BookCopyCreateRequest,
) -> BookCopy:

    book_copy = BookCopy(
        isbn=payload.isbn,
        shelf_id=payload.shelf_id,
        
    )

    db.add(book_copy)
    await db.commit()
    await db.refresh(book_copy)

    return book_copy


async def get_book_copy(
    db: AsyncSession,
    copy_id: int,
) -> BookCopy | None:

    result = await db.execute(
        select(BookCopy).where(BookCopy.id == copy_id)
    )

    return result.scalar_one_or_none()





async def get_book_copies(
    db: AsyncSession,
    isbn: str | None = None,
    shelf_id: int | None = None,
    
    status: BookCopyStatus | None = None,
) -> list[BookCopy]:

    query = select(BookCopy)

    if isbn is not None:
        query = query.where(BookCopy.isbn == isbn)

    if shelf_id is not None:
        query = query.where(BookCopy.shelf_id == shelf_id)


    if status is not None:
        query = query.where(BookCopy.status == status)

    result = await db.execute(query)

    return result.scalars().all()


async def update_book_copy(
    db: AsyncSession,
    book_copy: BookCopy,
    payload: BookCopyUpdateRequest,
) -> BookCopy:

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(book_copy, key, value)

    await db.commit()
    await db.refresh(book_copy)

    return book_copy


async def delete_book_copy(
    db: AsyncSession,
    book_copy: BookCopy,
) -> None:

    await db.delete(book_copy)
    await db.commit()


async def get_book_copy_statistics(
    db: AsyncSession,
) -> dict:

    total = await db.scalar(
        select(func.count(BookCopy.id))
    )

    available = await db.scalar(
        select(func.count(BookCopy.id)).where(
            BookCopy.status == BookCopyStatus.AVAILABLE
        )
    )

    borrowed = await db.scalar(
        select(func.count(BookCopy.id)).where(
            BookCopy.status == BookCopyStatus.BORROWED
        )
    )

    damaged = await db.scalar(
        select(func.count(BookCopy.id)).where(
            BookCopy.status == BookCopyStatus.DAMAGED
        )
    )

    lost = await db.scalar(
        select(func.count(BookCopy.id)).where(
            BookCopy.status == BookCopyStatus.LOST
        )
    )

    return {
        "total": total or 0,
        "available": available or 0,
        "borrowed": borrowed or 0,
        "damaged": damaged or 0,
        "lost": lost or 0,
    }

async def update_status(
    db: AsyncSession,
    book_copy: BookCopy,
    status: BookCopyStatus,
) -> BookCopy:
    book_copy.status = status

    await db.commit()
    await db.refresh(book_copy)

    return book_copy