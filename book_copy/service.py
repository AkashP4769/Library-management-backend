

from sqlalchemy.ext.asyncio import AsyncSession

from book_copy import repo as BookCopyRepository
from book_copy.schema import (
    BookCopyCreateRequest,
    BookCopyUpdateRequest,
)
from models.book_copy import BookCopy


async def create_book_copy(
    db: AsyncSession,
    payload: BookCopyCreateRequest,
) -> BookCopy:

    return await BookCopyRepository.create_book_copy(
        db=db,
        payload=payload,
    )


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
        raise ValueError("Book Copy Not Found")

    return book_copy


async def update_book_copy(
    db: AsyncSession,
    copy_id: int,
    payload: BookCopyUpdateRequest,
) -> BookCopy:

    book_copy = await BookCopyRepository.get_book_copy(
        db=db,
        copy_id=copy_id,
    )

    if not book_copy:
        raise ValueError("Book Copy Not Found")

    return await BookCopyRepository.update_book_copy(
        db=db,
        book_copy=book_copy,
        payload=payload,
    )


async def delete_book_copy(
    db: AsyncSession,
    copy_id: int,
) -> None:

    book_copy = await BookCopyRepository.get_book_copy(
        db=db,
        copy_id=copy_id,
    )

    if not book_copy:
        raise ValueError("Book Copy Not Found")

    await BookCopyRepository.delete_book_copy(
        db=db,
        book_copy=book_copy,
    )


async def get_book_copy_statistics(
    db: AsyncSession,
):

    return await BookCopyRepository.get_book_copy_statistics(db)