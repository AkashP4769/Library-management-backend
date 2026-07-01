"""
Business logic for Review.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from audit import service as audit_service
from auth.schemas import TokenPayload
from book import repo as book_repo
from exceptions import NotFoundException
from models.audit import AuditAction
from models.review import Review
from review import repo
from review.schema import (
    ReviewBookResponse,
    ReviewCreateRequest,
    ReviewUpdateRequest,
)


async def create_review(
    db: AsyncSession,
    payload: ReviewCreateRequest,
    current_user: TokenPayload,
) -> Review:
    """
    Create a review.
    """

    book = await book_repo.get_by_isbn(
        db=db,
        isbn=payload.isbn,
    )

    if book is None:
        raise NotFoundException("Book with this ISBN does not exist.")

    review = await repo.create_review(
        db=db,
        payload=payload,
        current_user=current_user,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=current_user.user_id,
        action_type=AuditAction.CREATE,
        entity_type="REVIEW",
        entity_id=str(review.id),
        new_value=review.to_api_dict(),
    )

    return review


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
        raise NotFoundException("Review Not Found")

    return review


async def get_book_review(
    db: AsyncSession,
    isbn: str,
) -> list[ReviewBookResponse]:

    reviews = await repo.get_book_review(
        db=db,
        isbn=isbn,
    )

    if not reviews:
        raise NotFoundException("Review Not Found")

    return [
        ReviewBookResponse(
            name=review.user.name,
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
    actor_user_id: int = 1,
) -> Review:
    """
    Update a review.
    """

    review = await repo.get_review(
        db=db,
        review_id=review_id,
    )

    if review is None:
        raise NotFoundException("Review Not Found")

    old_value = review.to_api_dict().copy()

    updated_review = await repo.update_review(
        db=db,
        review=review,
        payload=payload,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.UPDATE,
        entity_type="REVIEW",
        entity_id=str(updated_review.id),
        old_value=old_value,
        new_value=updated_review.to_api_dict(),
    )

    return updated_review


async def delete_review(
    db: AsyncSession,
    review_id: int,
    actor_user_id: int = 1,
) -> None:
    """
    Delete a review.
    """

    review = await repo.get_review(
        db=db,
        review_id=review_id,
    )

    if review is None:
        raise NotFoundException("Review Not Found")

    old_value = review.to_api_dict().copy()

    await repo.delete_review(
        db=db,
        review=review,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.DELETE,
        entity_type="REVIEW",
        entity_id=str(review.id),
        old_value=old_value,
    )
