"""
Business logic for BorrowedBook.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from audit import service as audit_service
from book_copy import repo as book_copy_repo
from borrowed_book import repo
from borrowed_book.schema import BorrowBookRequest
from exceptions import ConflictException, NotFoundException
from models.audit import AuditAction
from models.book_copy import BookCopyStatus
from models.borrowed_book import BorrowStatus, BorrowedBook
from user import repository as user_repo


async def borrow_book(
    db: AsyncSession,
    payload: BorrowBookRequest,
    actor_user_id: int,
) -> BorrowedBook:

    book_copy = await book_copy_repo.get_book_copy(
        db=db,
        book_copy_id=payload.book_copy_id,
    )

    if book_copy is None:
        raise NotFoundException("Book copy not found.")

    user = await user_repo.get_user(
        db=db,
        user_id=payload.user_id,
    )

    if user is None:
        raise NotFoundException("User not found.")

    if book_copy.status != BookCopyStatus.AVAILABLE:
        raise ConflictException("Book copy is not available.")

    existing = await repo.get_active_borrow(
        db=db,
        book_copy_id=payload.book_copy_id,
    )

    if existing:
        raise ConflictException("Book copy is already borrowed.")

    borrowed_book = await repo.borrow_book(
        db=db,
        payload=payload,
    )

    await book_copy_repo.update_status(
        db=db,
        book_copy=book_copy,
        status=BookCopyStatus.BORROWED,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.BORROW,
        entity_type="BORROWED_BOOK",
        entity_id=str(borrowed_book.id),
        old_value={
            "book_copy_status": BookCopyStatus.AVAILABLE.value,
        },
        new_value={
            "book_copy_status": BookCopyStatus.BORROWED.value,
            "borrow": borrowed_book.to_api_dict(),
        },
    )

    return borrowed_book


async def get_borrowed_books(
    db: AsyncSession,
    user_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    limit: int = 10,
) -> list[BorrowedBook]:

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

    borrowed_book = await repo.get_borrowed_book(
        db=db,
        borrow_id=borrow_id,
    )

    if borrowed_book is None:
        raise NotFoundException("Borrow record not found.")

    return borrowed_book


async def return_book(
    db: AsyncSession,
    borrow_id: int,
    actor_user_id: int,
) -> BorrowedBook:

    borrowed_book = await repo.get_borrowed_book(
        db=db,
        borrow_id=borrow_id,
    )

    if borrowed_book is None:
        raise NotFoundException("Borrow record not found.")

    if borrowed_book.status == BorrowStatus.RETURNED:
        raise ConflictException("Book already returned.")

    old_value = borrowed_book.to_api_dict().copy()

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

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.RETURN,
        entity_type="BORROWED_BOOK",
        entity_id=str(borrowed_book.id),
        old_value=old_value,
        new_value=borrowed_book.to_api_dict(),
    )

    return borrowed_book


async def renew_book(
    db: AsyncSession,
    borrow_id: int,
    actor_user_id: int,
) -> BorrowedBook:

    borrowed_book = await repo.get_borrowed_book(
        db=db,
        borrow_id=borrow_id,
    )

    if borrowed_book is None:
        raise NotFoundException("Borrow record not found.")

    if borrowed_book.status == BorrowStatus.RETURNED:
        raise ConflictException("Returned books cannot be renewed.")

    if borrowed_book.status == BorrowStatus.OVERDUE:
        raise ConflictException("Overdue books cannot be renewed.")

    if borrowed_book.renewal_count >= 3:
        raise ConflictException("Maximum renewal limit reached.")

    old_value = borrowed_book.to_api_dict().copy()

    borrowed_book = await repo.renew_book(
        db=db,
        borrowed_book=borrowed_book,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.UPDATE,
        entity_type="BORROWED_BOOK",
        entity_id=str(borrowed_book.id),
        old_value=old_value,
        new_value=borrowed_book.to_api_dict(),
    )

    return borrowed_book