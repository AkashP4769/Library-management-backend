"""
API routes for Shelf.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from shelf.schema import (
    ShelfCreateRequest,
    ShelfResponse,
    ShelfUpdateRequest,
)
from exceptions import (AppException,
    NotFoundException,
    ConflictException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    DBException )
from shelf.service import (
    create_shelf,
    delete_shelf,
    get_shelf,
    get_shelves,
    update_shelf,
)

router = APIRouter(
    prefix="/shelves",
    tags=["Shelves"],
)


@router.post(
    "/",
    response_model=ShelfResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    payload: ShelfCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    shelf = await create_shelf(db, payload)
    return shelf.to_api_dict()


@router.get(
    "/",
    response_model=list[ShelfResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    db: AsyncSession = Depends(get_db),
):
    shelves = await get_shelves(db)
    return [shelf.to_api_dict() for shelf in shelves]


@router.get(
    "/{shelf_id}",
    response_model=ShelfResponse,
    status_code=status.HTTP_200_OK,
)
async def get(
    shelf_id: int,
    db: AsyncSession = Depends(get_db),
):
    shelf = await get_shelf(db, shelf_id)

    if shelf is None:
        raise NotFoundException("Shelf With this id does not exist")

    return shelf.to_api_dict()


@router.patch(
    "/{shelf_id}",
    response_model=ShelfResponse,
    status_code=status.HTTP_200_OK,
)
async def update(
    shelf_id: int,
    payload: ShelfUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    shelf = await update_shelf(
        db=db,
        shelf_id=shelf_id,
        payload=payload,
    )

    if shelf is None:
        raise NotFoundException("Shelf Not Found")
    return shelf.to_api_dict()


@router.delete(
    "/{shelf_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(
    shelf_id: int,
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_shelf(db, shelf_id)

    if not deleted:
        raise NotFoundException("Shelf Not Found")

    return