

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from exceptions import (AppException,
    NotFoundException,
    ConflictException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    DBException )
from book.schemas import (
    BookCreateRequest,
    BookResponse,
    BookUpdateRequest,
    BookAPIResponse
)
from book import service
from database.connection import get_db


router = APIRouter(
    prefix="/books",
    tags=["Books"],
)



@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    payload: BookCreateRequest = Depends(
        BookCreateRequest.as_form

    ),
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):

    try:
        return await service.create_book(
            db,
            payload,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[BookResponse],
)
async def get_books(
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):

    return await service.get_books(db)
@router.get(
        "/isbn/api/{isbn}",
        response_model=BookAPIResponse
)
async def get_book_by_isbn_by_api(
     isbn: str,
     _current_user: TokenPayload = Depends(get_current_user),
):
    try:
        return await service.get_by_isbn_by_api(
            isbn=isbn
        )
    except :
        print("yessssss")
        raise NotFoundException("Book Not Found")


@router.get(
    "/isbn/{isbn}",
    response_model=BookResponse,
)
async def get_book_by_isbn(
    isbn: str,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):
    try:
        return await service.get_by_isbn(
            db=db,
            isbn=isbn,
        )
    except ValueError:
        raise NotFoundException("Book Not Found")
@router.get(
    "/{book_id}",
    response_model=BookResponse,
)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):

    try:
        return await service.get_book(
            db,
            book_id,
        )

    except ValueError as e:
        raise NotFoundException("Book Not Found")


@router.patch(
    "/{book_id}",
    response_model=BookResponse,
)
async def update_book(
    book_id: int,
    payload: BookUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):

    try:
        return await service.update_book(
            db,
            book_id,
            payload,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):

    try:
        await service.delete_book(
            db,
            book_id,
        )

    except ValueError as e:
        raise NotFoundException("Book Not Found")