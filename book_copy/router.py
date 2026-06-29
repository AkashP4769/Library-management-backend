"""
Book Copy API routes.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from exceptions import NotFoundException
from book_copy import service
from book_copy.schema import (
    BookCopyCreateRequest,
    BookCopyUpdateRequest,
    BookCopyResponse,
    BookCopyStatisticsResponse,
    BookCopyStatus,
)

router = APIRouter(
    prefix="/book-copies",
    tags=["Book Copies"],
)


# -----------------------
# CRUD
# -----------------------

@router.post(
    "",
    response_model=BookCopyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_book_copy(
    payload: BookCopyCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_book_copy(db, payload)


@router.get(
    "",
    response_model=list[BookCopyResponse],
)
async def get_book_copies(
    isbn: str | None = Query(default=None),
    shelf_id: int | None = Query(default=None),
    status: BookCopyStatus | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_book_copies(
        db=db,
        isbn=isbn,
        shelf_id=shelf_id,
        status=status,
    )


@router.get(
    "/statistics",
    response_model=BookCopyStatisticsResponse,
)
async def get_book_copy_statistics(
    db: AsyncSession = Depends(get_db),
):
    return await service.get_book_copy_statistics(db)


@router.get(
    "/{copy_id}",
    response_model=BookCopyResponse,
)
async def get_book_copy(
    copy_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.get_book_copy(
            db,
            copy_id,
        )
    except ValueError:
        raise NotFoundException("Book Copy Not Found")


@router.patch(
    "/{copy_id}",
    response_model=BookCopyResponse,
)
async def update_book_copy(
    copy_id: int,
    payload: BookCopyUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.update_book_copy(
            db,
            copy_id,
            payload,
        )
    except ValueError:
        raise NotFoundException("Book Copy Not Found")


@router.delete(
    "/{copy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book_copy(
    copy_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        await service.delete_book_copy(
            db,
            copy_id,
        )
    except ValueError:
        raise NotFoundException("Book Copy Not Found")


# -----------------------
# Admin Statistics
# -----------------------
