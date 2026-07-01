"""
Database model for Wishlist.
"""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Entity


class Wishlist(Entity):
    __tablename__ = "wishlists"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_user_book_wishlist",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="wishlists",
    )

    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="wishlists",
    )
    def to_api_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": (
                self.deleted_at.isoformat()
                if self.deleted_at
                else None
            ),
        }
    def to_return_dict(self):
        return self.to_api_dict()