import pytest

from book import repo
from models.book import Book


@pytest.mark.asyncio
async def test_get_book_by_isbn(db_session):
    book = Book(
        isbn="9780132350882",
        title="Clean Code",
        author="Robert C. Martin",
        genre="Programming",
        publisher="Prentice Hall",
        language="English",
        description="Test book",
    )

    db_session.add(book)
    await db_session.commit()

    result = await repo.get_book_by_isbn(
        db=db_session,
        isbn="9780132350882",
    )

    assert result is not None
    assert result.isbn == "9780132350882"
    assert result.title == "Clean Code"