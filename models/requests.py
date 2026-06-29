"""
Database model for Request.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Entity


def _datetime_to_iso(value: datetime |None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Request(Entity):
    __tablename__ = "requests"

    requester_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    borrowed_books_id: Mapped[int | None] = mapped_column(
    ForeignKey("borrowed_books.id"),
    nullable=True,
    )

    isbn: Mapped[str] = mapped_column(
    String(20),
    ForeignKey("books.isbn"),
    nullable=False,
    )

    status: Mapped[RequestStatus] = mapped_column(
        SQLEnum(RequestStatus, name="request_status"),
        default=RequestStatus.PENDING,
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    requester: Mapped["User"] = relationship(
    "User",
    back_populates="requests",
    )

    borrowed_book: Mapped["BorrowedBook"] = relationship(
        "BorrowedBook",
        back_populates="request",
    )

    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="requests",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "requester_id": self.requester_id,
            "borrowed_books_id": self.borrowed_books_id,
            "isbn": self.isbn,
            "status": self.status.value,
            "created_at": _datetime_to_iso(self.created_at),
            "updated_at": _datetime_to_iso(self.updated_at),
            "deleted_at": _datetime_to_iso(self.deleted_at),
            "resolved_at": _datetime_to_iso(self.resolved_at),
        }