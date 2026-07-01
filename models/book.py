from datetime import datetime
from typing import Any

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Entity


def _datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class Book(Entity):
    __abstract__ = False
    __tablename__ = "books"

    isbn: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    author: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    genre: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    publisher: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    book_copies: Mapped[list["BookCopy"]] = relationship(
        "BookCopy",
        back_populates="book",
        cascade="all, delete-orphan",
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="book",
        cascade="all, delete-orphan",
    )
    wishlists: Mapped[list["Wishlist"]] = relationship(
    "Wishlist",
    back_populates="book",
    cascade="all, delete-orphan",
    )

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "publisher": self.publisher,
            "language": self.language,
            "description": self.description,
            "image_url": self.image_url,
            "created_at": _datetime_to_iso(self.created_at),
            "updated_at": _datetime_to_iso(self.updated_at),
            "deleted_at": _datetime_to_iso(self.deleted_at),
        }

    def __repr__(self):
        return (
            f"Book("
            f"id={self.id}, "
            f"isbn='{self.isbn}', "
            f"title='{self.title}', "
            f"author='{self.author}'"
            f")"
        )
