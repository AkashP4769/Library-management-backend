"""
Business logic for Book.
"""

from pathlib import Path
import shutil
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from book import repo
from book.schemas import BookCreateRequest, BookUpdateRequest
from exceptions import ConflictException, NotFoundException
from models.book import Book



UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

async def create_book(
    db: AsyncSession,
    payload: BookCreateRequest,
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

    return await repo.create(db, payload)


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
        raise NotFoundException("Book Not Found")

    return book


async def get_by_isbn_by_api(isbn: str):
    book = await repo.get_by_isbn_api(isbn)

    if not book:
        raise NotFoundException("Book Not Found")

    return book


async def update_book(
    db: AsyncSession,
    book_id: int,
    payload: BookUpdateRequest,
) -> Book:

    book = await repo.get_by_id(db, book_id)

    if not book:
        raise ValueError("Book not found.")

    if payload.isbn:
        existing = await repo.get_by_isbn(db, payload.isbn)

        if existing and existing.id != book.id:
            raise ConflictException("Book With this ISBN Already Exist")

    return await repo.update(
        db,
        book,
        payload,
    )


async def delete_book(
    db: AsyncSession,
    book_id: int,
) -> None:

    book = await repo.get_by_id(db, book_id)

    if not book:
        raise NotFoundException("Book Not Found")

    await repo.delete(
        db,
        book,
    )


async def search_books(db: AsyncSession, **filters):
    return await repo.search(db, **filters)
