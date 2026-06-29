"""
Database model for BorrowedBook.
"""

from datetime import datetime
from enum import Enum
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Entity


def _datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class BorrowStatus(str, Enum):
    BORROWED = "BORROWED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class BorrowedBook(Entity):
    __tablename__ = "borrowed_books"

    book_copy_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("book_copies.id"),
    nullable=False,
)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[BorrowStatus] = mapped_column(
        SQLEnum(BorrowStatus),
        nullable=False,
        default=BorrowStatus.BORROWED,
    )

    renewal_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    fine_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    book_copy: Mapped["BookCopy"] = relationship(
        "BookCopy",
        back_populates="borrowed_books",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="borrowed_books",
    )

    request: Mapped["Request"] = relationship(
    "Request",
    back_populates="borrowed_book",
    )

    def to_api_dict(self) -> dict:
        return {
            "id": str(self.id),
            "book_copy_id": str(self.book_copy_id),
            "user_id": self.user_id,
            "borrowed_at": _datetime_to_iso(self.borrowed_at),
            "due_date": _datetime_to_iso(self.due_date),
            "returned_at": _datetime_to_iso(self.returned_at),
            "status": self.status.value,
            "renewal_count": self.renewal_count,
            "fine_amount": float(self.fine_amount),
            "created_at": _datetime_to_iso(self.created_at),
            "updated_at": _datetime_to_iso(self.updated_at),
            "deleted_at": _datetime_to_iso(self.deleted_at),
        }

    def __repr__(self):
        return (
            f"BorrowedBook("
            f"id={self.id}, "
            f"book_copy_id={self.book_copy_id}, "
            f"user_id={self.user_id}, "
            f"status={self.status.value}"
            f")"
        )