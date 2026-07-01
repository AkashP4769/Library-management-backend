from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import TokenPayload
from exceptions import (
    BadRequestException,
    DBException,
    NotFoundException,
)

from models.notifications import (
    Notifications,
    NotificationStatus,
    NotificationType,
)

from notifications import repo
from notifications.schema import (
    CreateBorrowRequest,
    NotificationCreateRequest,
    NotificationUpdateRequest,
)

from user import repository as user_repo
from book_copy import repo as book_copy_repo
from borrowed_book import repo as borrow_repo
from models.book_copy import BookCopy, BookCopyStatus
from models.borrowed_book import BorrowedBook


async def _validate_receiver(
    db: AsyncSession,
    receiver_id: int,
):
    receiver = await user_repo.get_by_id(
        db,
        receiver_id,
    )

    if not receiver:
        raise NotFoundException("Receiver not found.")


async def _validate_book_copy(
    db: AsyncSession,
    book_copy_id: int | None,
):
    if book_copy_id is None:
        return None

    book_copy = await book_copy_repo.get_book_copy(
        db,
        book_copy_id,
    )

    if not book_copy:
        raise NotFoundException("Book copy not found.")

    return book_copy


async def broadcast_admin_notification(
    db: AsyncSession,
    payload: NotificationCreateRequest,
):
    if (
        payload.notification_type != NotificationType.ADMIN_NOTIFICATION
        and payload.receiver_id is None
    ):
        raise BadRequestException(
            "Broadcast notification is only supported for admin notifications."
        )

    users = await user_repo.get_all_users(db)

    notifications = []

    for user in users:
        notifications.append(
            Notifications(
                receiver_id=user.id,
                sender_id=payload.sender_id,
                message=payload.message,
                notification_type=NotificationType.ADMIN_NOTIFICATION,
                status=NotificationStatus.PENDING,
            )
        )

    return await repo.create_bulk_notifications(
        db,
        notifications,
    )


async def _validate_notification_type_rules(
    db: AsyncSession,
    payload: NotificationCreateRequest,
):
    if payload.notification_type == NotificationType.ADMIN_NOTIFICATION:
        if not payload.message:
            raise BadRequestException("Admin notification requires a message.")
        return

    book_copy = await _validate_book_copy(
        db,
        payload.book_copy_id,
    )

    if payload.notification_type == NotificationType.REQUEST_BOOK:
        if book_copy.is_available:
            raise BadRequestException("Book is already available.")

    elif payload.notification_type == NotificationType.DUE_DATE_REMINDER:
        borrow = await borrow_repo.get_active_borrow(
            db,
            payload.receiver_id,
            payload.book_copy_id,
        )

        if not borrow:
            raise BadRequestException("No active borrowing found.")

    elif payload.notification_type == NotificationType.IN_STOCK_NOTIFICATION:
        if not book_copy.is_available:
            raise BadRequestException("Book is not yet in stock.")


async def create_notification(
    db: AsyncSession,
    payload: NotificationCreateRequest,
):
    try:
        if (
            payload.notification_type == NotificationType.ADMIN_NOTIFICATION
            and payload.receiver_id is None
        ):
            raise BadRequestException("Broadcast notification not supported here.")

        await _validate_receiver(
            db,
            payload.receiver_id,
        )

        await _validate_notification_type_rules(
            db,
            payload,
        )

        existing = await repo.get_user_notifications(
            db,
            user_id=payload.receiver_id,
            book_copy_id=payload.book_copy_id,
            notification_type=payload.notification_type,
            status=NotificationStatus.PENDING,
            resolved=False,
        )

        if existing:
            raise BadRequestException("Pending notification already exists.")

        notification = Notifications(
            receiver_id=payload.receiver_id,
            sender_id=payload.sender_id,
            book_copy_id=payload.book_copy_id,
            message=payload.message,
            notification_type=payload.notification_type,
            status=NotificationStatus.PENDING,
        )

        return await repo.create_notification(
            db,
            notification,
        )

    except SQLAlchemyError as e:
        await db.rollback()
        raise DBException(f"Failed to create notification: {str(e)}")


async def get_notification(
    db: AsyncSession,
    notification_id: int,
):
    notification = await repo.get_notification_by_id(
        db,
        notification_id,
    )

    if not notification:
        raise NotFoundException("Notification not found.")

    return notification


async def get_user_notifications(
    db: AsyncSession,
    user_id: int,
):
    await _validate_receiver(
        db,
        user_id,
    )

    return await repo.get_user_notifications(
        db,
        user_id,
    )


async def resolve_notification(
    db: AsyncSession,
    notification_id: int,
    payload: NotificationUpdateRequest,
):
    try:
        notification = await repo.get_notification_by_id(
            db,
            notification_id,
        )

        if not notification:
            raise NotFoundException("Notification not found.")

        if notification.status != NotificationStatus.PENDING:
            raise BadRequestException("Notification already resolved.")

        notification.status = payload.status
        notification.resolved_at = datetime.utcnow()

        if notification.notification_type == NotificationType.REQUEST_BOOK:
            request_status = (
                NotificationType.BOOK_BORROW_ACCEPTED
                if payload.status == NotificationStatus.ACCEPTED
                else NotificationType.BOOK_BORROW_REJECTED
            )
            borrow_action = Notifications(
                receiver_id=notification.sender_id,
                sender_id=notification.receiver_id,
                book_copy_id=notification.book_copy_id,
                notification_type=request_status,
                status=NotificationStatus.PENDING,
            )
            await repo.create_notification(db, borrow_action)

        return await repo.update_notification(db, notification, payload)

    except SQLAlchemyError:
        await db.rollback()
        raise DBException("Failed to resolve notification.")


async def create_request_notification(
    db: AsyncSession,
    payload: CreateBorrowRequest,
    current_user: TokenPayload,
):
    try:
        # Prevent duplicate request from same sender
        existing_request = await repo.get_user_requests(
            db=db,
            user_id=current_user.id,
            status=NotificationStatus.PENDING,
            isbn=payload.isbn,
            resolved=False,
        )

        if existing_request:
            raise BadRequestException("Already requested for this book.")

        # Step 1: Get all borrowed books with the given ISBN
        borrowed_books = await borrow_repo.get_active_borrows_by_isbn(
            db=db,
            isbn=payload.isbn,
        )

        if not borrowed_books:
            raise BadRequestException("No users currently hold this book.")

        created_notifications = []

        # Step 2: Notify all current holders
        for borrowed in borrowed_books:
            notification = Notifications(
                sender_id=current_user.id,
                receiver_id=borrowed.user_id,
                book_copy_id=borrowed.book_copy_id,
                notification_type=NotificationType.REQUEST_BOOK,
                status=NotificationStatus.PENDING,
                resolved=False,
            )

            created = await repo.create_notification(db, notification)
            created_notifications.append(created)

        await db.commit()

        return created_notifications

    except SQLAlchemyError as e:
        await db.rollback()
        raise DBException(f"Failed to create request notifications.{e}")
