"""
Business logic for Book.
"""

from pathlib import Path
import shutil
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from audit import service as audit_service
from book import repo
from book.schemas import BookCreateRequest, BookUpdateRequest
from exceptions import ConflictException, NotFoundException
from models.audit import AuditAction
from models.book import Book



UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

async def create_book(
    db: AsyncSession,
    payload: BookCreateRequest,
    actor_user_id: int = 1,
) -> Book:

    existing = await repo.get_by_isbn(db, payload.isbn)

    if existing:
        raise ConflictException("Book with this ISBN already exists.")
    
    # save image file if provided convert the image to webp format and save it to the static folder and save the path in the database
    image_path = None
    image = payload.image

    if image:
        extension = Path(image.filename).suffix
    
        filename = f"{uuid.uuid4()}{extension}"

        file_path = UPLOAD_DIR / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_path = f"/uploads/{filename}"

    payload.image_url = image_path
    print(payload.image_url)

    book = await repo.create(db, payload)

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action_type=AuditAction.CREATE,
        entity_type="BOOK",
        entity_id=book.isbn,
        new_value=book.to_api_dict(),
    )

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
) -> list[Book]:

    return await repo.get_all(db)


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
            raise ConflictException(
                "Book with this ISBN already exists."
            )

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

    return updated_book


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


async def search_books(
    db: AsyncSession,
    **filters,
):

    return await repo.search(
        db,
        **filters,
    )