"""
Business logic for Shelf.
"""

import shutil

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
    get_books_by_shelf
)
from shelf.schema import (
    ShelfBookResponse,
    ShelfCreateRequest,
    ShelfUpdateRequest,
)
from utils import save_image


async def create_shelf(
    db: AsyncSession,
    payload: ShelfCreateRequest,
    actor_user_id: int = 1,
) -> Shelf:

    existing = await get_by_shelf_code(
        db=db,
        shelf_code=payload.shelf_code,
    )

    if existing:
        raise ConflictException("Shelf with the same code already exists.")

    image_path = None
    image = payload.image

    if image:
        image_path = save_image(image)

    shelf = Shelf(
        shelf_code=payload.shelf_code,
        office_location=payload.office_location,
        capacity=payload.capacity,
        image_url=image_path,
    )

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
    actor_user_id: int = 1,
) -> Shelf:

    shelf = await get_by_id(
        db=db,
        shelf_id=shelf_id,
    )

    if shelf is None:
        raise NotFoundException("Shelf not found.")

    if payload.shelf_code is not None and payload.shelf_code != shelf.shelf_code:
        existing = await get_by_shelf_code(
            db=db,
            shelf_code=payload.shelf_code,
        )

        if existing:
            raise ConflictException("Shelf with the same code already exists.")

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
    actor_user_id: int = 1,
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


    


async def get_books_by_shelfs(
    db: AsyncSession,
    shelf_id: int,
    q: str | None = None,
    genre: str | None = None,
    language: str | None = None,
) -> list[ShelfBookResponse]:
    books = await get_books_by_shelf(
        db=db,
        shelf_id=shelf_id,
        q=q,
        genre=genre,
        language=language,
    )

    if not books:
        raise NotFoundException(
            detail="No books found on this shelf."
        )

    return [
        ShelfBookResponse(
            id=book.id,
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            genre=book.genre,
            publisher=book.publisher,
            language=book.language,
            description=book.description,
            image_url=book.image_url,
            total_copies=book.total_copies,
            available_copies=book.available_copies,
            borrowed_copies=book.borrowed_copies,
            damaged_copies=book.damaged_copies,
            lost_copies=book.lost_copies,
            average_rating=float(book.average_rating)
            if book.average_rating is not None
            else None,
        )
        for book in books
    ]