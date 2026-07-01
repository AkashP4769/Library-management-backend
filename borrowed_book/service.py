"""
Business logic for BorrowedBook.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from audit import service as audit_service
from auth.schemas import TokenPayload
from book_copy import repo as book_copy_repo
from borrowed_book import repo
from borrowed_book.schema import BorrowBookRequest, BorrowedBookDetailsResponse
from exceptions import (
    BadRequestException,
    ConflictException,
    DBException,
    NotFoundException,
)
from models.audit import AuditAction
from models.book_copy import BookCopyStatus
from models.borrowed_book import BorrowStatus, BorrowedBook
from user import repository as user_repo


async def get_borrowed_books_details(
    db: AsyncSession,
    user_id: int | None = None,
    status: BorrowStatus | None = None,
    page: int = 1,
    limit: int = 10,
) -> list[BorrowedBookDetailsResponse]:

    try:
        if page < 1:
            raise BadRequestException("Page number must be greater than 0.")

        if limit < 1:
            raise BadRequestException("Limit must be greater than 0.")

        borrowed_books = await repo.get_borrowed_books_details(
            db=db,
            user_id=user_id,
            status=status,
            page=page,
            limit=limit,
        )

        if not borrowed_books:
            raise NotFoundException("No borrowed books found.")

        return [
            BorrowedBookDetailsResponse(
                id=borrowed_book.id,
                user_id=borrowed_book.user.id,
                user_name=borrowed_book.user.name,
                user_email=borrowed_book.user.email,
                book_copy_id=borrowed_book.book_copy.id,
                isbn=borrowed_book.book_copy.book.isbn,
                title=borrowed_book.book_copy.book.title,
                image_url=borrowed_book.book_copy.book.image_url,
                author=borrowed_book.book_copy.book.author,
                genre=borrowed_book.book_copy.book.genre,
                image_url=borrowed_book.book_copy.book.image_url,
                # publisher=borrowed_book.book_copy.book.publisher,
                # language=borrowed_book.book_copy.book.language,
                # shelf_id=borrowed_book.book_copy.shelf.id,
                shelf_code=borrowed_book.book_copy.shelf.shelf_code,
                # office_location=borrowed_book.book_copy.shelf.office_location,
                borrowed_at=borrowed_book.borrowed_at,
                due_date=borrowed_book.due_date,
                returned_at=borrowed_book.returned_at,
                status=borrowed_book.status,
                renewal_count=borrowed_book.renewal_count,
                fine_amount=float(borrowed_book.fine_amount),
                # created_at=borrowed_book.created_at,
                # updated_at=borrowed_book.updated_at,
            )
            for borrowed_book in borrowed_books
        ]

    except (BadRequestException, NotFoundException):
        raise

    except SQLAlchemyError as e:
        raise DBException(f"Failed to fetch borrowed book details: {e}")


async def borrow_book(
    db: AsyncSession,
    payload: BorrowBookRequest,
    current_user: TokenPayload,
) -> BorrowedBook:

    book_copy = await book_copy_repo.get_available_book_copy(
        db=db,
        isbn=payload.isbn,
        shelf_id=payload.shelf_id,
    )

    if book_copy is None:
        raise NotFoundException("No available copy found for the given ISBN and shelf.")

    user = await user_repo.get_by_id(
        db=db,
        user_id=current_user.id,
    )

    if user is None:
        raise NotFoundException("User not found.")

    existing = await repo.get_active_borrow(
        db=db,
        book_copy_id=book_copy.id,
    )

    if existing:
        raise ConflictException("Book copy is already borrowed.")

    borrowed_book = await repo.borrow_book(
        db=db,
        book_copy_id=book_copy.id,
        user_id=current_user.id,
    )

    await book_copy_repo.update_status(
        db=db,
        book_copy=book_copy,
        status=BookCopyStatus.BORROWED,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=current_user.id,
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
    shelf_id: int,
    current_user: TokenPayload,
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
        copy_id=borrowed_book.book_copy_id,
    )

    if book_copy is not None:
        await book_copy_repo.update_status(
            db=db,
            book_copy=book_copy,
            status=BookCopyStatus.AVAILABLE,
            shelf_id=shelf_id,
        )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=current_user.id,
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
    actor_user_id: int = 1,
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
