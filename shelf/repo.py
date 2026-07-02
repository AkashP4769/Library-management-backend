"""
Repository layer for Shelf.
"""

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.book import Book
from models.book_copy import BookCopy, BookCopyStatus
from models.review import Review
from models.shelf import Shelf


async def create(
    db: AsyncSession,
    shelf: Shelf,
) -> Shelf:
    db.add(shelf)
    await db.commit()
    await db.refresh(shelf)

    return shelf


async def get_all(
    db: AsyncSession,
) -> list[Shelf]:
    result = await db.execute(
        select(Shelf)
    )

    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession,
    shelf_id: int,
) -> Shelf | None:
    result = await db.execute(
        select(Shelf).where(
            Shelf.id == shelf_id,
        )
    )

    return result.scalar_one_or_none()


async def get_by_shelf_code(
    db: AsyncSession,
    shelf_code: str,
) -> Shelf | None:
    result = await db.execute(
        select(Shelf).where(
            Shelf.shelf_code == shelf_code,
        )
    )

    return result.scalar_one_or_none()


async def update(
    db: AsyncSession,
    shelf: Shelf,
) -> Shelf:
    await db.commit()
    await db.refresh(shelf)

    return shelf



async def delete(
    db: AsyncSession,
    shelf: Shelf,
) -> None:
    await db.delete(shelf)
    await db.commit()


async def get_books_by_shelf(
    db: AsyncSession,
    shelf_id: int,
    q: str | None = None,
    genre: str |None = None,
    language: str | None = None,
):
    filters = [
        BookCopy.shelf_id == shelf_id,
        Book.deleted_at.is_(None),
    ]

    if q:
        filters.append(
        or_(
            Book.title.ilike(f"%{q}%"),
            Book.author.ilike(f"%{q}%"),
        )
    )

    if genre:
        filters.append(Book.genre.ilike(f"%{genre}%"))
    if language:
        filters.append(Book.language.ilike(f"%{language}%"))
    

    stmt = (
        select(
            Book.id,
            Book.isbn,
            Book.title,
            Book.author,
            Book.genre,
            Book.publisher,
            Book.language,
            Book.description,
            Book.image_url,

            func.count(BookCopy.id).label("total_copies"),

            func.sum(
                case(
                    (BookCopy.status == BookCopyStatus.AVAILABLE, 1),
                    else_=0,
                )
            ).label("available_copies"),

            func.sum(
                case(
                    (BookCopy.status == BookCopyStatus.BORROWED, 1),
                    else_=0,
                )
            ).label("borrowed_copies"),

            func.sum(
                case(
                    (BookCopy.status == BookCopyStatus.DAMAGED, 1),
                    else_=0,
                )
            ).label("damaged_copies"),

            func.sum(
                case(
                    (BookCopy.status == BookCopyStatus.LOST, 1),
                    else_=0,
                )
            ).label("lost_copies"),

            func.avg(Review.rating).label("average_rating"),
        )
        .join(Book, BookCopy.isbn == Book.isbn)
        .outerjoin(Review, Review.isbn == Book.isbn)
        .where(*filters)
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