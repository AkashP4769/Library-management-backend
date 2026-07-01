"""
Database operations for Review.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.schemas import TokenPayload
from models.review import Review
from review.schema import (
    ReviewCreateRequest,
    ReviewUpdateRequest,
)


async def create_review(
    db: AsyncSession,
    payload: ReviewCreateRequest,
    current_user: TokenPayload,
) -> Review:
    review = Review(
        isbn=payload.isbn,
        user_id=current_user.id,
        content=payload.content,
        rating=payload.rating,
    )

    db.add(review)
    await db.commit()
    await db.refresh(review)

    return review


async def get_reviews(
    db: AsyncSession,
    isbn: str | None = None,
    user_id: int | None = None,
    page: int = 1,
    limit: int = 10,
) -> list[Review]:

    stmt = select(Review)

    if isbn is not None:
        stmt = stmt.where(Review.isbn == isbn)

    if user_id is not None:
        stmt = stmt.where(Review.user_id == user_id)

    stmt = stmt.offset((page - 1) * limit).limit(limit)

    result = await db.execute(stmt)

    return result.scalars().all()


async def get_review(
    db: AsyncSession,
    review_id: int,
) -> Review | None:

    stmt = select(Review).where(Review.id == review_id)

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def get_book_review(
    db: AsyncSession,
    isbn: str,
) -> list[Review] | None:
    print("ISBN: ", isbn)
    stmt = select(Review).options(selectinload(Review.user)).where(Review.isbn == isbn)
    print("stmt ", stmt)
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_review(
    db: AsyncSession,
    review: Review,
    payload: ReviewUpdateRequest,
) -> Review:

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(review, field, value)

    await db.commit()
    await db.refresh(review)

    return review


async def delete_review(
    db: AsyncSession,
    review: Review,
) -> None:

    await db.delete(review)
    await db.commit()
