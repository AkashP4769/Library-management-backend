"""
Database operations for BorrowedBook.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from book_copy.schema import BookCopyStatus
from models.book_copy import BookCopy
from models.borrowed_book import BorrowStatus, BorrowedBook
from borrowed_book.schema import BorrowBookRequest
from models.borrowed_book import BorrowedBook
from models.book_copy import BookCopy
from models.book import Book


async def get_borrowed_books_details(
    db: AsyncSession,
    user_id: int | None = None,
    status: BorrowStatus | None = None,
    page: int = 1,
    limit: int = 10,
) -> list[BorrowedBook]:

    query = select(BorrowedBook).options(
        joinedload(BorrowedBook.user),
        joinedload(BorrowedBook.book_copy).joinedload(BookCopy.book),
        joinedload(BorrowedBook.book_copy).joinedload(BookCopy.shelf),
    )

    if user_id is not None:
        query = query.where(
            BorrowedBook.user_id == user_id,
        )

    if status is not None:
        query = query.where(
            BorrowedBook.status == status,
        )

    query = (
        query.order_by(BorrowedBook.borrowed_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    result = await db.execute(query)

    return result.scalars().unique().all()


async def find_available_book_copy(
    db: AsyncSession,
    isbn: str,
    shelf_id: int,
) -> BookCopy | None:
    """
    Find the first available copy for the given ISBN on the specified shelf.
    """

    stmt = (
        select(BookCopy)
        .where(
            BookCopy.isbn == isbn,
            BookCopy.shelf_id == shelf_id,
            BookCopy.status == BookCopyStatus.AVAILABLE,
        )
        .order_by(BookCopy.id)
        .limit(1)
    )

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def borrow_book(
    db: AsyncSession,
    book_copy_id: int,
    user_id: int,
) -> BorrowedBook:

    borrowed_book = BorrowedBook(
        book_copy_id=book_copy_id,
        user_id=user_id,
        borrowed_at=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status=BorrowStatus.BORROWED,
        renewal_count=0,
        fine_amount=0,
    )

    db.add(borrowed_book)
    await db.commit()
    await db.refresh(borrowed_book)

    return borrowed_book


async def get_borrowed_books(
    db: AsyncSession,
    user_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    limit: int = 10,
) -> list[BorrowedBook]:

    stmt = select(BorrowedBook)

    if user_id is not None:
        stmt = stmt.where(BorrowedBook.user_id == user_id)

    if status is not None:
        stmt = stmt.where(BorrowedBook.status == BorrowStatus(status))

    stmt = stmt.offset((page - 1) * limit).limit(limit)

    result = await db.execute(stmt)

    return result.scalars().all()


async def get_borrowed_book(
    db: AsyncSession,
    borrow_id: int,
) -> BorrowedBook | None:

    stmt = select(BorrowedBook).where(BorrowedBook.id == borrow_id)

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def get_active_borrow(
    db: AsyncSession,
    book_copy_id: int,
) -> BorrowedBook | None:

    stmt = select(BorrowedBook).where(
        BorrowedBook.book_copy_id == book_copy_id,
        BorrowedBook.status == BorrowStatus.BORROWED,
    )

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def return_book(
    db: AsyncSession,
    borrowed_book: BorrowedBook,
) -> BorrowedBook:

    borrowed_book.returned_at = datetime.now(timezone.utc)
    borrowed_book.status = BorrowStatus.RETURNED
    bookcopy = await db.get(BookCopy, borrowed_book.book_copy_id)
    bookcopy.status = BookCopyStatus.AVAILABLE
    if borrowed_book.returned_at > borrowed_book.due_date:
        overdue_days = (borrowed_book.returned_at - borrowed_book.due_date).days

        borrowed_book.fine_amount = overdue_days * 10

    await db.commit()
    await db.refresh(borrowed_book)
    await db.refresh(bookcopy)
    return borrowed_book


async def renew_book(
    db: AsyncSession,
    borrowed_book: BorrowedBook,
) -> BorrowedBook:

    borrowed_book.due_date += timedelta(days=14)
    borrowed_book.renewal_count += 1

    await db.commit()
    await db.refresh(borrowed_book)

    return borrowed_book


async def get_active_borrows_by_filter(
    db: AsyncSession,
    user_id: int | None = None,
    isbn: str | None = None,
    shelf_id: int | None = None,
) -> list[BorrowedBook]:
    filters = [
        BorrowedBook.status == BorrowStatus.BORROWED,
    ]

    if user_id:
        filters.append(BorrowedBook.user_id == user_id)

    if isbn:
        filters.append(BorrowedBook.book_copy.has(BookCopy.isbn == isbn))

    if shelf_id is not None:
        filters.append(BorrowedBook.shelf_id == shelf_id)

    stmt = (
        select(BorrowedBook)
        .join(BookCopy, BorrowedBook.book_copy_id == BookCopy.id)
        .where(and_(*filters))
    )

    result = await db.execute(stmt)

    return result.scalars().all()


async def get_user_borrow_history(
    db: AsyncSession,
    user_id: int,
) -> list[tuple[BorrowedBook, Book]]:

    stmt = (
        select(BorrowedBook, Book)
        .join(Book, BorrowedBook.book_id == Book.id)
        .where(BorrowedBook.user_id == user_id)
        .order_by(BorrowedBook.borrowed_at.desc())
        .limit(10)
    )

    result = await db.execute(stmt)

    return result.all()
