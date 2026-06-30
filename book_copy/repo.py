"""
Database operations for Book Copy.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.book import Book
from models.book_copy import BookCopy, BookCopyStatus
from models.review import Review
from models.shelf import Shelf

from book_copy.schema import BookCopyCreateRequest, BookCopyUpdateRequest, BulkBookCopyCreateRequest
from models.book_copy import BookCopy, BookCopyStatus


async def create_book_copy(
    db: AsyncSession,
    payload: list[BulkBookCopyCreateRequest],
) -> list[BookCopy]:

    book_copies = []
    for bulk_request in payload:
        book_copies.extend([
            BookCopy(
                isbn=bulk_request.isbn,
                shelf_id=bulk_request.shelf_id,
            )
            for _ in range(bulk_request.quantity)
        ])

    db.add_all(book_copies)
    await db.commit()
    refreshed_book_copies = []
    for book_copy in book_copies:
        await db.refresh(book_copy)
        refreshed_book_copies.append(book_copy)

    return refreshed_book_copies


async def get_book_copy(
    db: AsyncSession,
    copy_id: int,
) -> BookCopy | None:

    result = await db.execute(select(BookCopy).where(BookCopy.id == copy_id))

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

    total = await db.scalar(select(func.count(BookCopy.id)))

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
        select(func.count(BookCopy.id)).where(BookCopy.status == BookCopyStatus.DAMAGED)
    )

    lost = await db.scalar(
        select(func.count(BookCopy.id)).where(BookCopy.status == BookCopyStatus.LOST)
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



async def get_inventory(
    db: AsyncSession,
    page: int = 1,
    limit: int = 10,
) -> tuple[list, int]:

    offset = (page - 1) * limit

    total_query = (
        select(
            func.count()
        )
        .select_from(
            select(
                BookCopy.isbn,
                BookCopy.shelf_id,
            )
            .group_by(
                BookCopy.isbn,
                BookCopy.shelf_id,
            )
            .subquery()
        )
    )

    total = (
        await db.execute(total_query)
    ).scalar_one()

    query = (
        select(
            Book.isbn,
            Book.title,
            Book.author,
            Book.genre,
            Book.publisher,
            Book.language,

            Shelf.id.label("shelf_id"),
            Shelf.shelf_code,
            Shelf.office_location,

            func.count(BookCopy.id).label("total_copies"),

            func.sum(
                case(
                    (
                        BookCopy.status == BookCopyStatus.AVAILABLE,
                        1,
                    ),
                    else_=0,
                )
            ).label("available_copies"),

            func.sum(
                case(
                    (
                        BookCopy.status == BookCopyStatus.BORROWED,
                        1,
                    ),
                    else_=0,
                )
            ).label("borrowed_copies"),

            func.avg(
                Review.rating
            ).label("average_rating"),
        )
        .join(
            Book,
            BookCopy.isbn == Book.isbn,
        )
        .join(
            Shelf,
            BookCopy.shelf_id == Shelf.id,
        )
        .outerjoin(
            Review,
            Review.isbn == Book.isbn,
        )
        .group_by(
            Book.isbn,
            Book.title,
            Book.author,
            Book.genre,
            Book.publisher,
            Book.language,

            Shelf.id,
            Shelf.shelf_code,
            Shelf.office_location,
        )
        .order_by(
            Book.title
        )
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)

    return result.all(), total