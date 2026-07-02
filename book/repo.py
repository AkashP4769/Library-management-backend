"""
Repository layer for Book.
"""

from datetime import datetime
import requests
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from audit import service as audit_service
from models.book import Book
from models.shelf import Shelf
from book.schemas import BookAPIResponse, BookCreateRequest, BookUpdateRequest
from models.book_copy import BookCopy
from models.notifications import Notifications, NotificationType


async def create(
    db: AsyncSession,
    payload: BookCreateRequest,
) -> Book:
    book = Book(
        isbn=payload.isbn,
        title=payload.title,
        author=payload.author,
        genre=payload.genre,
        publisher=payload.publisher,
        language=payload.language,
        description=payload.description,
        image_url=payload.image_url,
    )

    db.add(book)
    await db.flush()
    await db.refresh(book)
    return book

async def get_by_id(
    db: AsyncSession,
    book_id: int,
) -> Book | None:

    result = await db.execute(
        select(Book).where(
            Book.id == book_id,
            Book.deleted_at.is_(None),
        )
    )

    return result.scalar()


async def get_by_isbn(
    db: AsyncSession,
    isbn: str,
) -> Book | None:

    result = await db.execute(
        select(Book).where(
            Book.isbn == isbn,
            Book.deleted_at.is_(None),
        )
    )

    return result.scalar()


async def get_by_isbn_api(isbn: str):
    result = response = requests.get(
        "https://openlibrary.org/api/books",
        params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"},
    ).json()
    LANGUAGE_MAP = {
        "/languages/eng": "English",
        "/languages/fre": "French",
        "/languages/spa": "Spanish",
        "/languages/ger": "German",
        "/languages/ita": "Italian",
        "/languages/jpn": "Japanese",
        "/languages/kor": "Korean",
        "/languages/hin": "Hindi",
        "/languages/tam": "Tamil",
        "/languages/tel": "Telugu",
        "/languages/mal": "Malayalam",
        "/languages/mar": "Marathi",
    }
    data = response[f"ISBN:{isbn}"]
    title = data["title"]
    author = "N/A"
    if data.get("authors"):
        author = data["authors"][0]["name"]
    publisher = data.get("publishers", [{}])[0].get("name")
    olid = data["key"]
    pages = data.get("number_of_pages")
    cover = data.get("cover", {})
    pic_large = ""
    pic_medium = ""
    if cover:
        pic_medium = cover.get("medium")
        pic_large = cover.get("large")
    edition = requests.get(f"https://openlibrary.org{olid}.json").json()

    languages = edition.get("languages", [])
    print(languages)
    if languages:
        languagekey = languages[0].get("key")

    else:
        languagekey = "N/A"
        language = "N/A"
    if languagekey != "N/A":
        language = LANGUAGE_MAP[languagekey]

    return BookAPIResponse(
        isbn=isbn,
        title=title,
        author=author,
        pages=str(pages),
        publisher=publisher,
        language=language,
        cover_urls=[pic_medium, pic_large],
    )


async def get_all(
    db: AsyncSession,
    q: str | None = None,
    genre: str | None = None,
    language: str | None = None,
) -> list[Book]:
    # Build the query with optional filters
    filters = [Book.deleted_at.is_(None)]
    if q:
        filters.append(
        or_(
            Book.title.ilike(f"%{q}%"),
            Book.author.ilike(f"%{q}%"),
        )
    )
    if genre:
        filters.append(Book.genre.ilike(f"%{genre}%"))
    if language:
        filters.append(Book.language.ilike(f"%{language}%"))
    result = await db.execute(select(Book).where(*filters).order_by(Book.title))

    return result.scalars().all()


async def update(
    db: AsyncSession,
    book: Book,
    payload: BookUpdateRequest,
) -> Book:

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, key, value)

    await db.flush()
    await db.refresh(book)
    return book


async def delete(
    db: AsyncSession,
    book: Book,
) -> None:

    book.deleted_at = datetime.utcnow()

    await db.flush()


async def search(
    db: AsyncSession,
    title: str | None = None,
    author: str | None = None,
    genre: str | None = None,
    isbn: str | None = None,
    language: str | None = None,
    available: bool | None = None,
    limit: int = 10,
) -> list[Book]:

    filters = [Book.deleted_at.is_(None)]

    if title:
        filters.append(Book.title.ilike(f"%{title}%"))

    if author:
        filters.append(Book.author.ilike(f"%{author}%"))

    if genre:
        filters.append(Book.genre.ilike(f"%{genre}%"))

    if isbn:
        filters.append(Book.isbn == isbn)

    if language:
        filters.append(Book.language.ilike(f"%{language}%"))

    if available is not None:
        filters.append(Book.available == available)

    stmt = select(Book).where(and_(*filters)).limit(limit)

    result = await db.execute(stmt)

    return result.scalars().all()


async def search_book_by_genre(
    genre: str, book_id: int, db: AsyncSession
) -> list[Book]:
    result = await db.execute(
        select(Book).where(
            Book.genre == genre,
            Book.id != book_id,
            Book.deleted_at.is_(None),
        )
    )

    return result.scalars().all()


async def get_shelves_of_book(
    db: AsyncSession,
    isbn: str,
) -> list[Shelf]:
    query = (
        # select distinct shelves that have available copies of the book with the given ISBN
        select(Shelf)
        .distinct()
        .join(BookCopy, BookCopy.shelf_id == Shelf.id)
        .where(
            BookCopy.isbn == isbn,
            BookCopy.status == "AVAILABLE",
        )
    )

    result = await db.execute(query)
    return result.scalars().all()


async def get_user_requested_books(
    db: AsyncSession,
    user_id: int,
):
    query = (
        select(BookCopy)
        .join(
            Notifications,
            Notifications.book_copy_id == BookCopy.id,
        )
        .where(
            Notifications.sender_id == user_id,
            Notifications.notification_type == NotificationType.REQUEST_BOOK,
        )
        .options(
            joinedload(BookCopy.book),
        )
        .order_by(Notifications.created_at.desc())
    )

    result = await db.execute(query)

    return list(result.scalars().unique().all())
