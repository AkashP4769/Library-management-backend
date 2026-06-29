
from datetime import datetime
from enum import Enum

from sqlalchemy import  Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Entity


def _datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class BookCopyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    LOST = "LOST"
    DAMAGED = "DAMAGED"

class BookCopy(Entity):
    __tablename__ = "book_copies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    isbn: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("books.isbn"),
        nullable=False,
    )

    shelf_id: Mapped[int] = mapped_column(
        ForeignKey("shelves.id"),
        nullable=False,
    )
    status: Mapped[BookCopyStatus] = mapped_column(
    SQLEnum(
        BookCopyStatus,
        name="bookcopystatus",
        values_callable=lambda enum_cls: [e.value for e in enum_cls],
    ),
    nullable=False,
    server_default=BookCopyStatus.AVAILABLE.value,
    )
    book: Mapped["Book"] = relationship(
    "Book",
    back_populates="book_copies",
    )

    shelf: Mapped["Shelf"] = relationship(
        "Shelf",
        back_populates="book_copies",
    )
    borrowed_books: Mapped[list["BorrowedBook"]] = relationship(
    "BorrowedBook",
    back_populates="book_copy",
    )

    def to_api_dict(self) -> dict:
        return {
            "id": self.id,
            "isbn": self.isbn,
            "shelf_id": self.shelf_id,
            "status":self.status.value,
            "created_at": _datetime_to_iso(self.created_at),
            "updated_at": _datetime_to_iso(self.updated_at),
            "deleted_at": _datetime_to_iso(self.deleted_at),
        }

    def __repr__(self):
        return (
            f"BookCopy("
            f"id={self.id}, "
            f"isbn={self.isbn}, "
            f"shelf_id={self.shelf_id})"
            f"status={self.status.value}"
        )