"""
Database model for Request.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Entity


def _datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SEEN = "SEEN"


class NotificationType(str, Enum):
    REQUEST_BOOK = "REQUEST_BOOK"
    DUE_DATE_REMINDER = "DUE_DATE_REMINDER"
    ADMIN_NOTIFICATION = "ADMIN_NOTIFICATION"
    IN_STOCK_NOTIFICATION = "IN_STOCK_NOTIFICATION"
    BOOK_BORROW_ACCEPTED = "BOOK_BORROW_ACCEPTED"
    BOOK_BORROW_REJECTED = "BOOK_BORROW_REJECTED"
    BOOK_RETURN_ACCEPTED = "BOOK_RETURN_ACCEPTED"
    BOOK_RETURN_REJECTED = "BOOK_RETURN_REJECTED"


class Notifications(Entity):
    __tablename__ = "notifications"

    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    sender_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    message: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    notification_type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name="notification_type"),
        nullable=False,
    )

    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus, name="notification_status"),
        default=NotificationStatus.PENDING,
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    book_copy_id: Mapped[int | None] = mapped_column(
        ForeignKey("book_copies.id"),
        nullable=True,
    )

    receiver: Mapped["User"] = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_notifications",
    )

    sender: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_notifications",
    )

    book_copy: Mapped[Optional["BookCopy"]] = relationship(
        "BookCopy",
        back_populates="notifications",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "receiver_id": self.receiver_id,
            "sender_id": self.sender_id,
            "book_copy_id": self.book_copy_id,
            "notification_type": self.notification_type.value,
            "status": self.status.value,
            "message": self.message,
            "created_at": _datetime_to_iso(self.created_at),
            "resolved_at": _datetime_to_iso(self.resolved_at),
        }
