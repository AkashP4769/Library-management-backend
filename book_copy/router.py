"""
Book Copy API routes.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from database.connection import get_db
from exceptions import NotFoundException
from book_copy import service
from book_copy.schema import (
    BookCopyCreateRequest,
    BookCopyUpdateRequest,
    BookCopyResponse,
    BookCopyStatisticsResponse,
    BookCopyStatus,
    BulkBookCopyCreateRequest,
    BulkBookCopyResponse,
)
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from book_copy import service
from book_copy.schema import (
    InventoryListResponse,
    InventoryResponse,
)
from database import get_db
router = APIRouter(
    prefix="/book-copies",
    tags=["Book Copies"],
)


# -----------------------
# CRUD
# -----------------------


@router.get(
    "/inventory",
    response_model=InventoryListResponse,
)
async def get_inventory(
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
) -> InventoryListResponse:
   

    inventory, total = await service.get_inventory(
        db=db,
        page=page,
        limit=limit,
    )

    return InventoryListResponse(
        inventory=[
            InventoryResponse(
                isbn=row.isbn,
                title=row.title,
                author=row.author,
                genre=row.genre,
                publisher=row.publisher,
                language=row.language,
                shelf_id=row.shelf_id,
                shelf_code=row.shelf_code,
                office_location=row.office_location,
                total_copies=row.total_copies,
                available_copies=row.available_copies,
                borrowed_copies=row.borrowed_copies,
                average_rating=float(row.average_rating)
                if row.average_rating is not None
                else None,
            )
            for row in inventory
        ],
        total=total,
    )


@router.post(
    "",
    response_model=list[BulkBookCopyResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_book_copy(
    payload: list[BulkBookCopyCreateRequest],
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
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
    _current_user: TokenPayload = Depends(get_current_user),
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
    _current_user: TokenPayload = Depends(get_current_user),
):
    return await service.get_book_copy_statistics(db)


@router.get(
    "/{copy_id}",
    response_model=BookCopyResponse,
)
async def get_book_copy(
    copy_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
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
    _current_user: TokenPayload = Depends(get_current_user),
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
    _current_user: TokenPayload = Depends(get_current_user),
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
"""
API routes for Inventory.
"""




