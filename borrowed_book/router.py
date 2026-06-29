"""
API routes for BorrowedBook.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from borrowed_book import service
from borrowed_book.schema import (
    BorrowBookRequest,
    BorrowedBookResponse,
)
from database.connection import get_db
from exceptions import NotFoundException

router = APIRouter(
    prefix="/borrowed-books",
    tags=["Borrowed Books"],
)


@router.post(
    "",
    response_model=BorrowedBookResponse,
    status_code=status.HTTP_201_CREATED,
)
async def borrow_book(
    payload: BorrowBookRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.borrow_book(
            db=db,
            payload=payload,
        )

    except ValueError as e:
        raise NotFoundException(str(e))


@router.get(
    "",
    response_model=list[BorrowedBookResponse],
)
async def get_borrowed_books(
    user_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_borrowed_books(
        db=db,
        user_id=user_id,
        status=status,
        page=page,
        limit=limit,
    )


@router.get(
    "/{borrow_id}",
    response_model=BorrowedBookResponse,
)
async def get_borrowed_book(
    borrow_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.get_borrowed_book(
            db=db,
            borrow_id=borrow_id,
        )

    except ValueError:
        raise NotFoundException("Borrow record not found")


@router.patch(
    "/{borrow_id}/return",
    response_model=BorrowedBookResponse,
)
async def return_book(
    borrow_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.return_book(
            db=db,
            borrow_id=borrow_id,
        )

    except ValueError as e:
        raise NotFoundException(str(e))


@router.patch(
    "/{borrow_id}/renew",
    response_model=BorrowedBookResponse,
)
async def renew_book(
    borrow_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.renew_book(
            db=db,
            borrow_id=borrow_id,
        )

    except ValueError as e:
        raise NotFoundException(str(e))