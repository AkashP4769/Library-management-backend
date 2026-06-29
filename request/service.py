"""
Business logic for Request.
"""

from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from book import repo as book_repo
from borrowed_book import repo as borrowed_book_repo
from exceptions import (
    BadRequestException,
    ConflictException,
    DBException,
    NotFoundException,
)
from models.requests import Request, RequestStatus
from request import repo
from request.schema import RequestCreateRequest


async def create_request(
    db: AsyncSession,
    payload: RequestCreateRequest,
) -> Request:
    try:
        book = await book_repo.get_by_isbn(
            db,
            payload.isbn,
        )

        if book is None:
            raise NotFoundException("Book not found.")

        borrowed_book = await borrowed_book_repo.get_borrowed_book(
            db,
            payload.borrowed_books_id,
        )

        if borrowed_book is None:
            raise NotFoundException("Borrowed book not found.")

        existing = await repo.get_pending_request(
            db,
            payload.requester_id,
            payload.borrowed_books_id,
        )

        if existing:
            raise ConflictException(
                "A pending request already exists."
            )

        request = Request(
            requester_id=payload.requester_id,
            borrowed_books_id=payload.borrowed_books_id,
            isbn=payload.isbn,
            status=RequestStatus.PENDING,
        )

        return await repo.create_request(
            db,
            request,
        )

    except SQLAlchemyError:
        await db.rollback()
        raise DBException("Failed to create request.")


async def get_request(
    db: AsyncSession,
    request_id: int,
) -> Request:

    request = await repo.get_request_by_id(
        db,
        request_id,
    )

    if request is None:
        raise NotFoundException("Request not found.")

    return request


async def get_all_requests(
    db: AsyncSession,
) -> list[Request]:

    return await repo.get_all_requests(db)


async def get_my_requests(
    db: AsyncSession,
    requester_id: int,
) -> list[Request]:

    return await repo.get_my_requests(
        db,
        requester_id,
    )


async def get_incoming_requests(
    db: AsyncSession,
    borrowed_book_id: int,
) -> list[Request]:

    return await repo.get_incoming_requests(
        db,
        borrowed_book_id,
    )


async def approve_request(
    db: AsyncSession,
    request_id: int,
) -> Request:

    try:
        request = await repo.get_request_by_id(
            db,
            request_id,
        )

        if request is None:
            raise NotFoundException("Request not found.")

        if request.status != RequestStatus.PENDING:
            raise BadRequestException(
                "Only pending requests can be approved."
            )

        request.status = RequestStatus.APPROVED
        request.resolved_at = datetime.utcnow()

        # TODO:
        # Transfer ownership of borrowed book
        # or create a new BorrowedBook record
        # depending on your business rules.

        return await repo.update_request(
            db,
            request,
        )

    except SQLAlchemyError:
        await db.rollback()
        raise DBException("Failed to approve request.")


async def reject_request(
    db: AsyncSession,
    request_id: int,
) -> Request:

    try:
        request = await repo.get_request_by_id(
            db,
            request_id,
        )

        if request is None:
            raise NotFoundException("Request not found.")

        if request.status != RequestStatus.PENDING:
            raise BadRequestException(
                "Only pending requests can be rejected."
            )

        request.status = RequestStatus.REJECTED
        request.resolved_at = datetime.utcnow()

        return await repo.update_request(
            db,
            request,
        )

    except SQLAlchemyError:
        await db.rollback()
        raise DBException("Failed to reject request.")


async def cancel_request(
    db: AsyncSession,
    request_id: int,
) -> Request:

    try:
        request = await repo.get_request_by_id(
            db,
            request_id,
        )

        if request is None:
            raise NotFoundException("Request not found.")

        if request.status != RequestStatus.PENDING:
            raise BadRequestException(
                "Only pending requests can be cancelled."
            )

        request.status = RequestStatus.REJECTED
        request.resolved_at = datetime.utcnow()

        return await repo.update_request(
            db,
            request,
        )

    except SQLAlchemyError:
        await db.rollback()
        raise DBException("Failed to cancel request.")