"""
API routes for Request.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from request.schema import (
    RequestCreateRequest,
    RequestResponse,
)
from request.service import (
    approve_request,
    cancel_request,
    create_request,
    get_all_requests,
    get_incoming_requests,
    get_my_requests,
    get_request,
    reject_request,
)

router = APIRouter(
    prefix="/requests",
    tags=["Requests"],
)


@router.post(
    "",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_request_route(
    payload: RequestCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    return await create_request(
        db=db,
        payload=payload,
    )


@router.get(
    "",
    response_model=list[RequestResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_requests_route(
    db: AsyncSession = Depends(get_db),
):
    return await get_all_requests(db)


@router.get(
    "/me/{requester_id}",
    response_model=list[RequestResponse],
    status_code=status.HTTP_200_OK,
)
async def get_my_requests_route(
    requester_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_my_requests(
        db=db,
        requester_id=requester_id,
    )


@router.get(
    "/incoming/{borrowed_book_id}",
    response_model=list[RequestResponse],
    status_code=status.HTTP_200_OK,
)
async def get_incoming_requests_route(
    borrowed_book_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_incoming_requests(
        db=db,
        borrowed_book_id=borrowed_book_id,
    )


@router.get(
    "/{request_id}",
    response_model=RequestResponse,
    status_code=status.HTTP_200_OK,
)
async def get_request_route(
    request_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_request(
        db=db,
        request_id=request_id,
    )


@router.patch(
    "/{request_id}/approve",
    response_model=RequestResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_request_route(
    request_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await approve_request(
        db=db,
        request_id=request_id,
    )


@router.patch(
    "/{request_id}/reject",
    response_model=RequestResponse,
    status_code=status.HTTP_200_OK,
)
async def reject_request_route(
    request_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await reject_request(
        db=db,
        request_id=request_id,
    )


@router.patch(
    "/{request_id}/cancel",
    response_model=RequestResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_request_route(
    request_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await cancel_request(
        db=db,
        request_id=request_id,
    )