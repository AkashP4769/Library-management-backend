"""
Repository functions for Wishlist.
"""

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.book import Book
from models.book_copy import BookCopy, BookCopyStatus
from models.review import Review
from models.wishlist import Wishlist


async def get_wishlist_by_user_and_book(
    db: AsyncSession,
    user_id: int,
    book_id: int,
):
    stmt = select(Wishlist).where(
        Wishlist.user_id == user_id,
        Wishlist.book_id == book_id,
    )

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def create_wishlist(
    db: AsyncSession,
    wishlist: Wishlist,
):
    db.add(wishlist)
    await db.commit()
    await db.refresh(wishlist)

    return wishlist


async def delete_wishlist(
    db: AsyncSession,
    wishlist: Wishlist,
):
    await db.delete(wishlist)
    await db.commit()


async def get_user_wishlist(
    db: AsyncSession,
    user_id: int,
):
    stmt = (
        select(
            Book.id.label("book_id"),
            Book.isbn,
            Book.title,
            Book.author,
            Book.genre,
            Book.publisher,
            Book.language,
            Book.description,
            Book.image_url,
            func.avg(Review.rating).label("average_rating"),
            func.count(BookCopy.id).label("total_copies"),
            func.sum(
                case(
                    (BookCopy.status == BookCopyStatus.AVAILABLE, 1),
                    else_=0,
                )
            ).label("available_copies"),
        )
        .join(
            Wishlist,
            Wishlist.book_id == Book.id,
        )
        .outerjoin(
            Review,
            Review.isbn == Book.isbn,
        )
        .outerjoin(
            BookCopy,
            BookCopy.isbn == Book.isbn,
        )
        .where(
            Wishlist.user_id == user_id,
        )
        .group_by(
            Book.id,
            Book.isbn,
            Book.title,
            Book.author,
            Book.genre,
            Book.publisher,
            Book.language,
            Book.description,
            Book.image_url,
        )
        .order_by(Book.title)
    )

    result = await db.execute(stmt)

    return result.all()