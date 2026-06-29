"""
Database operations for Request.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.requests import Request, RequestStatus


async def create_request(
    db: AsyncSession,
    request: Request,
) -> Request:
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request


async def get_request_by_id(
    db: AsyncSession,
    request_id: int,
) -> Request | None:
    result = await db.execute(
        select(Request).where(
            Request.id == request_id,
            Request.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def get_all_requests(
    db: AsyncSession,
) -> list[Request]:
    result = await db.execute(
        select(Request).where(
            Request.deleted_at.is_(None),
        )
    )
    return list(result.scalars().all())


async def get_my_requests(
    db: AsyncSession,
    requester_id: int,
) -> list[Request]:
    result = await db.execute(
        select(Request).where(
            Request.requester_id == requester_id,
            Request.deleted_at.is_(None),
        )
    )
    return list(result.scalars().all())


async def get_incoming_requests(
    db: AsyncSession,
    borrowed_book_id: int,
) -> list[Request]:
    result = await db.execute(
        select(Request).where(
            Request.borrowed_books_id == borrowed_book_id,
            Request.deleted_at.is_(None),
        )
    )
    return list(result.scalars().all())


async def get_pending_request(
    db: AsyncSession,
    requester_id: int,
    borrowed_book_id: int,
) -> Request | None:
    result = await db.execute(
        select(Request).where(
            Request.requester_id == requester_id,
            Request.borrowed_books_id == borrowed_book_id,
            Request.status == RequestStatus.PENDING,
            Request.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_request(
    db: AsyncSession,
    request: Request,
) -> Request:
    await db.commit()
    await db.refresh(request)
    return request


async def delete_request(
    db: AsyncSession,
    request: Request,
) -> None:
    await db.delete(request)
    await db.commit()