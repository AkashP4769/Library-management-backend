"""
Business logic for Shelf.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import (AppException,
    NotFoundException,
    ConflictException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    DBException )
from models.shelf import Shelf
from shelf.repo import (
    create,
    delete,
    get_all,
    get_by_id,
    get_by_shelf_code,
    update,
)
from shelf.schema import (
    ShelfCreateRequest,
    ShelfUpdateRequest,
)


async def create_shelf(
    db: AsyncSession,
    payload: ShelfCreateRequest,
) -> Shelf:
    existing = await get_by_shelf_code(
        db=db,
        shelf_code=payload.shelf_code,
    )

    if existing:
        raise ConflictException("Shelf With Same code already exists")

    shelf = Shelf(**payload.model_dump())

    return await create(
        db=db,
        shelf=shelf,
    )


async def get_shelves(
    db: AsyncSession,
) -> list[Shelf]:
    return await get_all(db)


async def get_shelf(
    db: AsyncSession,
    shelf_id: int,
) -> Shelf | None:
    return await get_by_id(
        db=db,
        shelf_id=shelf_id,
    )


async def update_shelf(
    db: AsyncSession,
    shelf_id: int,
    payload: ShelfUpdateRequest,
) -> Shelf | None:
    shelf = await get_by_id(
        db=db,
        shelf_id=shelf_id,
    )

    if shelf is None:
        return None

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(shelf, key, value)

    return await update(
        db=db,
        shelf=shelf,
    )


async def delete_shelf(
    db: AsyncSession,
    shelf_id: int,
) -> bool:
    shelf = await get_by_id(
        db=db,
        shelf_id=shelf_id,
    )

    if shelf is None:
        return False

    await delete(
        db=db,
        shelf=shelf,
    )

    return True