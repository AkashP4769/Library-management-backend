"""
Service layer for Wishlist.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from audit import service as audit_service
from auth.schemas import TokenPayload
from book import repo as book_repo
from exceptions import ConflictException, NotFoundException
from models.audit import AuditAction
from models.wishlist import Wishlist
from wishlist import repo
from wishlist.schemas import (
    WishlistBookResponse,
    WishlistCreateRequest,
    WishlistResponse,
)


async def add_to_wishlist(
    db: AsyncSession,
    current_user: TokenPayload,
    request: WishlistCreateRequest,
) -> WishlistResponse:
    # Check that the book exists
    book = await book_repo.get_by_id(
        db=db,
        book_id=request.book_id,
    )

    if book is None:
        raise NotFoundException(
            detail="Book not found."
        )

    # Check for duplicate wishlist entry
    existing = await repo.get_wishlist_by_user_and_book(
        db=db,
        user_id=current_user.id,
        book_id=request.book_id,
    )

    if existing:
        raise ConflictException(
            detail="Book already exists in wishlist."
        )

    wishlist = Wishlist(
        user_id=current_user.id,
        book_id=request.book_id,
    )

    try:
        wishlist = await repo.create_wishlist(
            db=db,
            wishlist=wishlist,
        )
    except IntegrityError:
        await db.rollback()
        raise ConflictException(
            detail="Unable to add book to wishlist."
        )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=current_user.id,
        action_type=AuditAction.CREATE,
        entity_type="WISHLIST",
        entity_id=str(wishlist.id),
        new_value=wishlist.to_api_dict(),
    )

    return WishlistResponse(
        id=wishlist.id,
        user_id=wishlist.user_id,
        book_id=wishlist.book_id,
    )


async def remove_from_wishlist(
    db: AsyncSession,
    current_user: TokenPayload,
    book_id: int,
) -> None:
    # Check that the book exists
    book = await book_repo.get_by_id(
        db=db,
        book_id=book_id,
    )

    if book is None:
        raise NotFoundException(
            detail="Book not found."
        )

    wishlist = await repo.get_wishlist_by_user_and_book(
        db=db,
        user_id=current_user.id,
        book_id=book_id,
    )

    if wishlist is None:
        raise NotFoundException(
            detail="Book not found in wishlist."
        )

    try:
        await repo.delete_wishlist(
            db=db,
            wishlist=wishlist,
        )
    except IntegrityError:
        await db.rollback()
        raise ConflictException(
            detail="Unable to remove book from wishlist."
        )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=current_user.id,
        action_type=AuditAction.DELETE,
        entity_type="WISHLIST",
        entity_id=str(wishlist.id),
        old_value=wishlist.to_api_dict(),
    )


async def get_user_wishlist(
    db: AsyncSession,
    current_user: TokenPayload,
) -> list[WishlistBookResponse]:
    try:
        books = await repo.get_user_wishlist(
            db=db,
            user_id=current_user.id,
        )
    except IntegrityError:
        await db.rollback()
        raise ConflictException(
            detail="Unable to retrieve wishlist."
        )

    return [
        WishlistBookResponse(
            id=book.book_id,
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            genre=book.genre,
            publisher=book.publisher,
            language=book.language,
            description=book.description,
            image_url=book.image_url,
            average_rating=float(book.average_rating)
            if book.average_rating is not None
            else None,
            available_copies=book.available_copies,
            total_copies=book.total_copies,
        )
        for book in books
    ]