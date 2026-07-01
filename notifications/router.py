"""
API routes for Request.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from models.book import Book

from database.connection import get_db
from notifications.schema import (
    CreateBorrowRequest,
    NotificationCreateRequest,
    NotificationResponse,
    NotificationUpdateRequest,
)
from notifications.service import (
    broadcast_admin_notification,
    create_notification,
    create_request_notification,
    get_notification,
    get_user_notifications,
    resolve_notification,
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notifications_route(
    payload: NotificationCreateRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):
    payload.sender_id = _current_user.id
    return await create_notification(db=db, payload=payload)


@router.post(
    "/broadcast",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_broadcast_notifications_route(
    payload: NotificationCreateRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):
    payload.sender_id = _current_user.id
    return await broadcast_admin_notification(db=db, payload=payload)


@router.get(
    "/user/",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_notifications_route(
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    return await get_user_notifications(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_notification_route(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_notification(
        db=db,
        notification_id=notification_id,
    )


@router.patch(
    "/{notification_id}/resolve",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
async def resolve_notification_route(
    notification_id: int,
    payload: NotificationUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    return await resolve_notification(
        db=db,
        notification_id=notification_id,
        payload=payload,
    )


@router.post(
    "/request",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_request_notification_route(
    payload: CreateBorrowRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):

    return await create_request_notification(
        db=db, payload=payload, user_id=_current_user.id
    )
