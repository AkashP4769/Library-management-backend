"""
Business logic for Shelf.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from audit import service as audit_service
from exceptions import (
    ConflictException,
    NotFoundException,
)
from models.audit import AuditAction
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
    actor_user_id: int,
) -> Shelf:

    existing = await get_by_shelf_code(
        db=db,
        shelf_code=payload.shelf_code,
    )

    if existing:
        raise ConflictException(
            "Shelf with the same code already exists."
        )

    shelf = Shelf(**payload.model_dump())

    shelf = await create(
        db=db,
        shelf=shelf,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.CREATE,
        entity_type="SHELF",
        entity_id=str(shelf.id),
        new_value=shelf.to_api_dict(),
    )

    return shelf


async def get_shelves(
    db: AsyncSession,
) -> list[Shelf]:

    return await get_all(db)


async def get_shelf(
    db: AsyncSession,
    shelf_id: int,
) -> Shelf:

    shelf = await get_by_id(
        db=db,
        shelf_id=shelf_id,
    )

    if shelf is None:
        raise NotFoundException("Shelf not found.")

    return shelf


async def update_shelf(
    db: AsyncSession,
    shelf_id: int,
    payload: ShelfUpdateRequest,
    actor_user_id: int,
) -> Shelf:

    shelf = await get_by_id(
        db=db,
        shelf_id=shelf_id,
    )

    if shelf is None:
        raise NotFoundException("Shelf not found.")

    if (
        payload.shelf_code is not None
        and payload.shelf_code != shelf.shelf_code
    ):
        existing = await get_by_shelf_code(
            db=db,
            shelf_code=payload.shelf_code,
        )

        if existing:
            raise ConflictException(
                "Shelf with the same code already exists."
            )

    old_value = shelf.to_api_dict().copy()

    for key, value in payload.model_dump(
        exclude_unset=True,
    ).items():
        setattr(
            shelf,
            key,
            value,
        )

    updated_shelf = await update(
        db=db,
        shelf=shelf,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.UPDATE,
        entity_type="SHELF",
        entity_id=str(updated_shelf.id),
        old_value=old_value,
        new_value=updated_shelf.to_api_dict(),
    )

    return updated_shelf


async def delete_shelf(
    db: AsyncSession,
    shelf_id: int,
    actor_user_id: int,
) -> bool:

    shelf = await get_by_id(
        db=db,
        shelf_id=shelf_id,
    )

    if shelf is None:
        raise NotFoundException("Shelf not found.")

    old_value = shelf.to_api_dict().copy()

    await delete(
        db=db,
        shelf=shelf,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.DELETE,
        entity_type="SHELF",
        entity_id=str(shelf.id),
        old_value=old_value,
    )

    return True