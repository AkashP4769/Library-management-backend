"""
Business logic for BorrowedBook.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from book_copy import repo as book_copy_repo
from borrowed_book import repo
from models.borrowed_book import BorrowStatus
from borrowed_book.schema import BorrowBookRequest
from models.borrowed_book import BorrowedBook
from user import repository as user_repo
from models.book_copy import BookCopyStatus

async def borrow_book(
    db: AsyncSession,
    payload: BorrowBookRequest,
) -> BorrowedBook:

    book_copy = await book_copy_repo.get_book_copy(
        db=db,
        book_copy_id=payload.book_copy_id,
    )

    if book_copy is None:
        raise ValueError("Book copy not found.")

    user = await user_repo.get_user(
        db=db,
        user_id=payload.user_id,
    )

    if user is None:
        raise ValueError("User not found.")

    if book_copy.status != BookCopyStatus.AVAILABLE:
        raise ValueError("Book copy is not available.")

    existing = await repo.get_active_borrow(
        db=db,
        book_copy_id=payload.book_copy_id,
    )

    if existing:
        raise ValueError("Book copy is already borrowed.")

    borrowed_book = await repo.borrow_book(
        db=db,
        payload=payload,
    )

    await book_copy_repo.update_status(
        db=db,
        book_copy=book_copy,
        status=BookCopyStatus.BORROWED,
    )

    return borrowed_book

async def get_borrowed_books(
    db: AsyncSession,
    user_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    limit: int = 10,
) -> list[BorrowedBook]:
    """
    Get borrowed books.
    """

    return await repo.get_borrowed_books(
        db=db,
        user_id=user_id,
        status=status,
        page=page,
        limit=limit,
    )


async def get_borrowed_book(
    db: AsyncSession,
    borrow_id: int,
) -> BorrowedBook:
    """
    Get borrowed book by ID.
    """

    borrowed_book = await repo.get_borrowed_book(
        db=db,
        borrow_id=borrow_id,
    )

    if borrowed_book is None:
        raise ValueError("Borrow record not found.")

    return borrowed_book


async def return_book(
    db: AsyncSession,
    borrow_id: int,
) -> BorrowedBook:

    borrowed_book = await repo.get_borrowed_book(
        db=db,
        borrow_id=borrow_id,
    )

    if borrowed_book is None:
        raise ValueError("Borrow record not found.")

    if borrowed_book.status == BorrowStatus.RETURNED:
        raise ValueError("Book already returned.")

    borrowed_book = await repo.return_book(
        db=db,
        borrowed_book=borrowed_book,
    )

    book_copy = await book_copy_repo.get_book_copy(
        db=db,
        book_copy_id=borrowed_book.book_copy_id,
    )

    if book_copy is not None:
        await book_copy_repo.update_status(
            db=db,
            book_copy=book_copy,
            status=BookCopyStatus.AVAILABLE,
        )

    return borrowed_book

async def renew_book(
    db: AsyncSession,
    borrow_id: int,
) -> BorrowedBook:
    """
    Renew a borrowed book.
    """

    borrowed_book = await repo.get_borrowed_book(
        db=db,
        borrow_id=borrow_id,
    )

    if borrowed_book is None:
        raise ValueError("Borrow record not found.")

    if borrowed_book.status == BorrowStatus.RETURNED:
        raise ValueError("Returned books cannot be renewed.")

    if borrowed_book.status == BorrowStatus.OVERDUE:
        raise ValueError("Overdue books cannot be renewed.")

    if borrowed_book.renewal_count >= 3:
        raise ValueError("Maximum renewal limit reached.")

    return await repo.renew_book(
        db=db,
        borrowed_book=borrowed_book,
    )