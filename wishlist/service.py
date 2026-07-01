"""
Service layer for Wishlist.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import TokenPayload
from exceptions import ConflictException, NotFoundException
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

    wishlist = await repo.create_wishlist(
        db=db,
        wishlist=wishlist,
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
):

    wishlist = await repo.get_wishlist_by_user_and_book(
        db=db,
        user_id=current_user.id,
        book_id=book_id,
    )

    if wishlist is None:
        raise NotFoundException(
            detail="Book not found in wishlist."
        )

    await repo.delete_wishlist(
        db=db,
        wishlist=wishlist,
    )


async def get_user_wishlist(
    db: AsyncSession,
    current_user: TokenPayload,
) -> list[WishlistBookResponse]:

    books = await repo.get_user_wishlist(
        db=db,
        user_id=current_user.id,
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