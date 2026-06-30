"""
API routes for Review.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from database.connection import get_db
from exceptions import NotFoundException
from review import service
from review.schema import (
    ReviewCreateRequest,
    ReviewResponse,
    ReviewUpdateRequest,
    ReviewBookResponse,
)

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    payload: ReviewCreateRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):
    try:
        return await service.create_review(
            db=db,
            payload=payload,
        )

    except ValueError as e:
        raise NotFoundException(str(e))


@router.get(
    "",
    response_model=list[ReviewResponse],
)
async def get_reviews(
    isbn: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):
    return await service.get_reviews(
        db=db,
        isbn=isbn,
        user_id=user_id,
        page=page,
        limit=limit,
    )


@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
)
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):
    try:
        return await service.get_review(
            db=db,
            review_id=review_id,
        )

    except ValueError:
        raise NotFoundException("Review Not Found")


@router.get("/book/{isbn}", response_model=list[ReviewBookResponse])
async def get_book_review(
    isbn: str,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):
    try:
        print("route isbn: ", isbn)
        return await service.get_book_review(
            db=db,
            isbn=isbn,
        )

    except ValueError:
        raise NotFoundException("No reviews for this book")


@router.patch(
    "/{review_id}",
    response_model=ReviewResponse,
)
async def update_review(
    review_id: int,
    payload: ReviewUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):
    try:
        return await service.update_review(
            db=db,
            review_id=review_id,
            payload=payload,
        )

    except ValueError as e:
        raise NotFoundException(str(e))


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):
    try:
        await service.delete_review(
            db=db,
            review_id=review_id,
        )

    except ValueError:
        raise NotFoundException("Review Not Found")
