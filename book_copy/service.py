from sqlalchemy.ext.asyncio import AsyncSession

from audit import service as audit_service
from book_copy import repo as BookCopyRepository
from book_copy.schema import (
    BookCopyCreateRequest,
    BookCopyUpdateRequest,
    BulkBookCopyCreateRequest,
    BulkBookCopyResponse,
)
from exceptions import NotFoundException
from models.audit import AuditAction
from models.book_copy import BookCopy

"""
Business logic for Inventory.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from book_copy import repo


async def create_book_copy(
    db: AsyncSession,
    payload: list[BulkBookCopyCreateRequest],
    actor_user_id: int = 1,
) -> list[BulkBookCopyResponse]:

    book_copies = await BookCopyRepository.create_book_copy(
        db=db,
        payload=payload,
    )

    for book_copy in book_copies:
        await audit_service.create_audit_log(
            db=db,
            actor_user_id=actor_user_id,
            action_type=AuditAction.CREATE,
            entity_type="BOOK_COPY",
            entity_id=str(book_copy.id),
            new_value=book_copy.to_api_dict(),
        )

    await db.commit()

    return payload


async def get_book_copies(
    db: AsyncSession,
    isbn: str | None = None,
    shelf_id: int | None = None,
    status: str | None = None,
) -> list[BookCopy]:

    return await BookCopyRepository.get_book_copies(
        db=db,
        isbn=isbn,
        shelf_id=shelf_id,
        status=status,
    )


async def get_book_copy(
    db: AsyncSession,
    copy_id: int,
) -> BookCopy:

    book_copy = await BookCopyRepository.get_book_copy(
        db=db,
        copy_id=copy_id,
    )

    if not book_copy:
        raise NotFoundException("Book Copy Not Found")

    return book_copy


async def update_book_copy(
    db: AsyncSession,
    copy_id: int,
    payload: BookCopyUpdateRequest,
    actor_user_id: int = 1,
) -> BookCopy:

    book_copy = await BookCopyRepository.get_book_copy(
        db=db,
        copy_id=copy_id,
    )

    if not book_copy:
        raise NotFoundException("Book Copy Not Found")

    old_value = book_copy.to_api_dict().copy()

    updated_book_copy = await BookCopyRepository.update_book_copy(
        db=db,
        book_copy=book_copy,
        payload=payload,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.UPDATE,
        entity_type="BOOK_COPY",
        entity_id=str(updated_book_copy.id),
        old_value=old_value,
        new_value=updated_book_copy.to_api_dict(),
    )

    return updated_book_copy


async def delete_book_copy(
    db: AsyncSession,
    copy_id: int,
    actor_user_id: int = 1,
) -> None:

    book_copy = await BookCopyRepository.get_book_copy(
        db=db,
        copy_id=copy_id,
    )

    if not book_copy:
        raise NotFoundException("Book Copy Not Found")

    old_value = book_copy.to_api_dict().copy()

    await BookCopyRepository.delete_book_copy(
        db=db,
        book_copy=book_copy,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.DELETE,
        entity_type="BOOK_COPY",
        entity_id=str(book_copy.id),
        old_value=old_value,
    )


async def get_book_copy_statistics(
    db: AsyncSession,
):

    return await BookCopyRepository.get_book_copy_statistics(db)


async def get_inventory(
    db: AsyncSession,
    page: int = 1,
    limit: int = 10,
):
    """
    Get inventory summary grouped by ISBN and Shelf.
    """

    inventory, total = await repo.get_inventory(
        db=db,
        page=page,
        limit=limit,
    )

    return inventory, total
