"""
Repository layer for Book.
"""

from datetime import datetime
import requests 
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.book import Book
from book.schemas import BookAPIResponse, BookCreateRequest, BookUpdateRequest
async def create(
    db: AsyncSession,
    payload: BookCreateRequest,
) -> Book:
    book = Book(**payload.model_dump())

    db.add(book)
    await db.commit()
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

async def get_by_isbn_api(
        isbn:str
):
    result = response = requests.get(
    "https://openlibrary.org/api/books",
    params={
        "bibkeys": f"ISBN:{isbn}",
        "format": "json",
        "jscmd": "data"
    }
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
    author = 'N/A'
    if(data.get("author")):
        author = data["authors"][0]["name"]
    publisher = data.get("publishers", [{}])[0].get("name")
    olid = data["key"]
    pages= data.get("number_of_pages")
    cover = data.get("cover", {})
    pic_large=''
    pic_medium=''
    if(cover):
        pic_medium = cover.get("medium")
        pic_large = cover.get("large")
    edition = requests.get(f"https://openlibrary.org{olid}.json").json()
    
    languages = edition.get("languages",[])
    print(languages)
    if(languages):
        languagekey = languages[0].get("key")

    else:
        languagekey = 'N/A'
        language = 'N/A'
    if languagekey!='N/A':
        language = LANGUAGE_MAP[languagekey]
    
    return BookAPIResponse(
    isbn=isbn,
    title=title,
    author=author,
    pages=str(pages),
    publisher=publisher,
    language=language,
    cover_urls = [pic_medium,pic_large]
)
    
async def get_all(
    
    db: AsyncSession,
) -> list[Book]:

    result = await db.execute(
        select(Book).where(
            Book.deleted_at.is_(None)
        )
    )

    return result.scalars().all()

async def update(
    
    db: AsyncSession,
    book: Book,
    payload: BookUpdateRequest,
) -> Book:

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, key, value)

    await db.commit()
    await db.refresh(book)

    return book

async def delete(
    
    db: AsyncSession,
    book: Book,
) -> None:

    book.deleted_at = datetime.utcnow()

    await db.commit()