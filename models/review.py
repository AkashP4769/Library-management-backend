"""
Database model for Review.
"""

from datetime import datetime
from sqlalchemy import Float
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Entity


def _datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class Review(Entity):
    __tablename__ = "reviews"

    isbn: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("books.isbn"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("users.id"),
    nullable=False,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    

    rating: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="reviews",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="reviews",
    )

    def to_api_dict(self) -> dict:
        return {
            "id": str(self.id),
            "isbn": self.isbn,
            "user_id": str(self.user_id),
            "content": self.content,
            "rating": self.rating,
            "created_at": _datetime_to_iso(self.created_at),
            "updated_at": _datetime_to_iso(self.updated_at),
            "deleted_at": _datetime_to_iso(self.deleted_at),
        }

    def __repr__(self):
        return (
            f"Review("
            f"id={self.id}, "
            f"isbn={self.isbn}, "
            f"user_id={self.user_id}, "
            f"rating={self.rating}"
            f")"
        )