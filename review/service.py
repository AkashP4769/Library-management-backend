"""
Business logic for Review.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from models.review import Review
from review import repo
from review.schema import (
    ReviewBookResponse,
    ReviewCreateRequest,
    ReviewUpdateRequest,
)
from exceptions import NotFoundException
from book import repo as book_repo


async def create_review(
    db: AsyncSession,
    payload: ReviewCreateRequest,
) -> Review:
    """
    Create a review.
    """
    book = await book_repo.get_by_isbn(
        db=db,
        isbn=payload.isbn,
    )
    # user = await user_repo.get_user(
    # db=db,
    # user_id=payload.user_id,
    # )

    # if user is None:
    #     raise NotFoundException("User not found.")

    if book is None:
        raise ValueError("Book with this ISBN does not exist.")

    return await repo.create_review(
        db=db,
        payload=payload,
    )


async def get_reviews(
    db: AsyncSession,
    isbn: str | None = None,
    user_id: int | None = None,
    page: int = 1,
    limit: int = 10,
) -> list[Review]:
    """
    Get reviews with optional filters.
    """

    return await repo.get_reviews(
        db=db,
        isbn=isbn,
        user_id=user_id,
        page=page,
        limit=limit,
    )


async def get_review(
    db: AsyncSession,
    review_id: int,
) -> Review:
    """
    Get review by ID.
    """

    review = await repo.get_review(
        db=db,
        review_id=review_id,
    )

    if review is None:
        raise ValueError("Review Not Found")

    return review


async def get_book_review(
    db: AsyncSession,
    isbn: str,
) -> list[ReviewBookResponse]:

    reviews = await repo.get_book_review(
        db=db,
        isbn=isbn,
    )
    print("ser isbn: ", isbn)
    if not reviews:
        raise ValueError("Review Not Found")

    return [
        ReviewBookResponse(
            name=review.user.name,  # <-- comes from selectinload
            content=review.content,
            rating=review.rating,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )
        for review in reviews
    ]


async def update_review(
    db: AsyncSession,
    review_id: int,
    payload: ReviewUpdateRequest,
) -> Review:
    """
    Update a review.
    """

    review = await repo.get_review(
        db=db,
        review_id=review_id,
    )

    if review is None:
        raise ValueError("Review Not Found")

    return await repo.update_review(
        db=db,
        review=review,
        payload=payload,
    )


async def delete_review(
    db: AsyncSession,
    review_id: int,
) -> None:
    """
    Delete a review.
    """

    review = await repo.get_review(
        db=db,
        review_id=review_id,
    )

    if review is None:
        raise ValueError("Review Not Found")

    await repo.delete_review(
        db=db,
        review=review,
    )
