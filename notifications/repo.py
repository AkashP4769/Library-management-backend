"""
Database operations for Request.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.notifications import NotificationType, Notifications, NotificationStatus
from notifications.schema import NotificationUpdateRequest


async def create_notification(
    db: AsyncSession,
    notification: Notifications,
) -> Notifications:
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def get_notification_by_id(
    db: AsyncSession,
    notification_id: int,
) -> Notifications | None:
    result = await db.execute(
        select(Notifications).where(
            Notifications.id == notification_id,
            Notifications.resolved_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def get_all_notifications(
    db: AsyncSession,
) -> list[Notifications]:
    result = await db.execute(
        select(Notifications).where(
            Notifications.resolved_at.is_(None),
        )
    )
    return list(result.scalars().all())


async def get_user_notifications(
    db: AsyncSession,
    user_id: int,
    status: NotificationStatus | None = None,
    notification_type: NotificationType | None = None,
    resolved: bool | None = None,
    book_copy_id: int | None = None,
) -> list[Notifications]:
    query = select(Notifications).where(
        Notifications.receiver_id == user_id,
    )

    if status:
        query = query.where(
            Notifications.status == status,
        )

    if notification_type:
        query = query.where(
            Notifications.notification_type == notification_type,
        )

    if book_copy_id:
        query = query.where(
            Notifications.book_copy_id == book_copy_id,
        )

    if resolved is True:
        query = query.where(
            Notifications.resolved_at.is_not(None),
        )

    elif resolved is False:
        query = query.where(
            Notifications.resolved_at.is_(None),
        )

    query = query.order_by(
        Notifications.created_at.desc(),
    )

    result = await db.execute(query)

    return list(result.scalars().all())


async def update_notification(
    db: AsyncSession,
    notification: Notifications,
    payload: NotificationUpdateRequest,
) -> Notifications:

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(notification, field, value)

    await db.commit()
    await db.refresh(notification)

    return notification


async def create_bulk_notifications(
    db: AsyncSession,
    notifications: list[Notifications],
) -> list[Notifications]:
    db.add_all(notifications)
    await db.commit()

    for notification in notifications:
        await db.refresh(notification)

    return notifications
