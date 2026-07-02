"""
Business logic for Book.
"""

from pathlib import Path
import shutil
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from audit import service as audit_service
from book import repo
from book.schemas import BookCreateRequest, BookUpdateRequest, RequestedBookCopySchema
from exceptions import ConflictException, NotFoundException
from models.audit import AuditAction
from models.book import Book
from models.book_copy import BookCopy
from models.shelf import Shelf
from shelf.repo import get_books_by_shelf
from utils import save_image


async def create_book(
    db: AsyncSession,
    payload: BookCreateRequest,
    actor_user_id: int,
) -> Book:

    existing = await repo.get_by_isbn(db, payload.isbn)

    if existing:
        raise ConflictException("Book with this ISBN already exists.")

    # save image file if provided convert the image to webp format and save it to the static folder and save the path in the database
    image_path = None
    image = payload.image

    if image:
        image_path = save_image(image)

    payload.image_url = image_path

    book = await repo.create(db, payload)

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.CREATE,
        entity_type="BOOK",
        entity_id=book.isbn,
        new_value=book.to_api_dict(),
    )

    
    await db.commit()        # book + audit log persist together, atomically
    await db.refresh(book)
    return book


async def get_book(
    db: AsyncSession,
    book_id: int,
) -> Book:

    book = await repo.get_by_id(db, book_id)

    if not book:
        raise NotFoundException("Book not found.")

    return book


async def get_books(
    db: AsyncSession,
    q: str | None = None,
    genre: str | None = None,
    language: str | None = None,

) -> list[Book]:

    return await repo.get_all(db, q=q, genre=genre, language=language)


async def get_by_isbn(
    db: AsyncSession,
    isbn: str,
) -> Book:

    book = await repo.get_by_isbn(db, isbn)

    if not book:
        raise NotFoundException("Book not found.")

    return book


async def get_by_isbn_by_api(
    isbn: str,
):

    book = await repo.get_by_isbn_api(isbn)

    if not book:
        raise NotFoundException("Book not found.")

    return book


async def update_book(
    db: AsyncSession,
    book_id: int,
    payload: BookUpdateRequest,
    actor_user_id: int,
) -> Book:

    book = await repo.get_by_id(db, book_id)

    if not book:
        raise NotFoundException("Book not found.")

    if payload.isbn:
        existing = await repo.get_by_isbn(db, payload.isbn)

        if existing and existing.id != book.id:
            raise ConflictException("Book with this ISBN already exists.")

    old_value = book.to_api_dict().copy()

    updated_book = await repo.update(
        db,
        book,
        payload,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.UPDATE,
        entity_type="BOOK",
        entity_id=updated_book.isbn,
        old_value=old_value,
        new_value=updated_book.to_api_dict(),
    )

    
    await db.commit()        # book + audit log persist together, atomically
    await db.refresh(updated_book)
    return updated_book

async def delete_book_from_shelf(db,shelf_id: int, isbn: str, quantity: int):
    books = await get_books_by_shelf(db, shelf_id)
    book = next(
    (b for b in books if b.isbn == isbn),
    None,
)

    if book is None:
        raise NotFoundException("Book not found on this shelf.")

    if book.available_copies < quantity:
        raise ConflictException("Not enough available copies to delete.")
    
    quantity = await repo.delete_book_copies(db, isbn, shelf_id, quantity)
    return quantity


async def delete_book(
    db: AsyncSession,
    book_id: int,
    actor_user_id: int,
) -> None:

    book = await repo.get_by_id(db, book_id)

    if not book:
        raise NotFoundException("Book not found.")

    old_value = book.to_api_dict().copy()

    await repo.delete(
        db,
        book,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.DELETE,
        entity_type="BOOK",
        entity_id=book.isbn,
        old_value=old_value,
    )
    await db.commit()        # book + audit log persist together, atomically
    await db.refresh(book)


async def search_books(
    db: AsyncSession,
    **filters,
):

    return await repo.search(
        db,
        **filters,
    )


async def search_book_by_genre(genre: str, book_id: int, db: AsyncSession):
    return await repo.search_book_by_genre(genre=genre, book_id=book_id, db=db)


async def get_shelves_of_book(
    db: AsyncSession,
    isbn: str,
) -> list[Shelf]:
    return await repo.get_shelves_of_book(db=db, isbn=isbn)


async def get_user_requested_books(
    db: AsyncSession,
    user_id: int,
) -> list[BookCopy]:
    return await repo.get_user_requested_books(
        db=db,
        user_id=user_id,
    )
