from datetime import datetime, timezone


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
        if book_copy.status == BookCopyStatus.AVAILABLE:
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

        if (
            notification.notification_type == NotificationType.REQUEST_BOOK
            and notification.status == NotificationStatus.APPROVED
        ):
            borrowed_book = await borrow_repo.get_active_borrow(
                db,
                notification.book_copy_id,
            )
            borrow_action = Notifications(
                receiver_id=notification.sender_id,
                sender_id=notification.receiver_id,
                book_copy_id=notification.book_copy_id,
                notification_type=NotificationType.BOOK_RETURN_ACCEPTED,
                status=NotificationStatus.PENDING,
            )
            await borrow_repo.return_book(db=db, borrowed_book=borrowed_book)
            await repo.create_notification(db, borrow_action)

            await _invalidate_other_requests(
                db,
                book_copy_id=notification.book_copy_id,
                exclude_notification_id=notification.id,
            )

        elif (
            notification.notification_type == NotificationType.BOOK_RETURN_ACCEPTED
            and notification.status == NotificationStatus.APPROVED
        ):
            await borrow_repo.borrow_book(
                db=db,
                book_copy_id=notification.book_copy_id,
                user_id=notification.receiver_id,
            )

        return await repo.update_notification(db, notification, payload)

    except SQLAlchemyError:
        await db.rollback()
        raise DBException("Failed to resolve notification.")


async def create_request_notification(
    db: AsyncSession,
    payload: CreateBorrowRequest,
    user_id: int,
):
    try:
        # Prevent duplicate request from same sender
        existing_request = await repo.get_user_requests(
            db=db,
            user_id=user_id,
            status=NotificationStatus.PENDING,
            isbn=payload.isbn,
            resolved=False,
        )

        if existing_request:
            raise BadRequestException("Already requested for this book.")

        # Step 1: Get all borrowed books with the given ISBN
        borrowed_books = await borrow_repo.get_active_borrows_by_filter(
            db=db,
            isbn=payload.isbn,
        )

        if not borrowed_books:
            raise BadRequestException("No users currently hold this book.")

        created_notifications = []

        # Step 2: Notify all current holders
        for borrowed in borrowed_books:
            notification = Notifications(
                sender_id=user_id,
                receiver_id=borrowed.user_id,
                book_copy_id=borrowed.book_copy_id,
                notification_type=NotificationType.REQUEST_BOOK,
                status=NotificationStatus.PENDING,
            )

            created = await repo.create_notification(db, notification)
            created_notifications.append(created)

        await db.commit()

        return created_notifications

    except SQLAlchemyError as e:
        await db.rollback()
        raise DBException(f"Failed to create request notifications.{e}")


async def check_due_date_notifications(
    db: AsyncSession,
    user_id: int,
):
    """
    Checks active borrowed books for due/overdue status
    and creates due-date reminders if not already created.
    """

    active_borrows = await borrow_repo.get_active_borrows_by_filter(db, user_id=user_id)

    if not active_borrows:
        return

    now = datetime.now(timezone.utc)
    for borrow in active_borrows:
        if borrow.due_date > now:
            continue

        existing = await repo.get_user_notifications(
            db,
            user_id=user_id,
            book_copy_id=borrow.book_copy_id,
            notification_type=NotificationType.DUE_DATE_REMINDER,
            status=NotificationStatus.PENDING,
            resolved=False,
        )

        if existing:
            continue

        due_notification = Notifications(
            receiver_id=user_id,
            sender_id=None,
            book_copy_id=borrow.book_copy_id,
            notification_type=NotificationType.DUE_DATE_REMINDER,
            status=NotificationStatus.PENDING,
        )

        await repo.create_notification(
            db,
            due_notification,
        )

    await db.commit()


async def _invalidate_other_requests(
    db: AsyncSession,
    *,
    book_copy_id: int,
    exclude_notification_id: int,
):
    """
    Reject all pending REQUEST_BOOK notifications
    except the accepted one.
    """

    pending_requests = await repo.get_pending_requests_by_book_copy(
        db,
        book_copy_id=book_copy_id,
        notification_type=NotificationType.REQUEST_BOOK,
        status=NotificationStatus.PENDING,
    )

    for req in pending_requests:
        if req.id == exclude_notification_id:
            continue

        req.status = NotificationStatus.REJECTED
        req.resolved_at = datetime.now(timezone.utc)

    await db.commit()
