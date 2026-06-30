"""
User entity — ORM mapped class for table `user`.
"""

from datetime import datetime
from typing import Any
import enum

from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Entity


def _datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"


class User(Entity):
    __abstract__ = False
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[int] = mapped_column(String(255), nullable=False)
    contact_number: Mapped[str] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="role",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
        server_default=UserRole.EMPLOYEE.value,
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    borrowed_books: Mapped[list["BorrowedBook"]] = relationship(
        "BorrowedBook",
        back_populates="user",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
    "AuditLog",
    back_populates="user",
    )

    received_notifications: Mapped[list["Notifications"]] = relationship(
        "Notifications",
        foreign_keys="Notifications.receiver_id",
        back_populates="receiver",
    )

    sent_notifications: Mapped[list["Notifications"]] = relationship(
        "Notifications",
        foreign_keys="Notifications.sender_id",
        back_populates="sender",
    )

    def to_api_dict(self) -> dict[str, Any]:
        """JSON-friendly representation (ISO 8601 for timestamps)."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "contact_number": self.contact_number,
            "role": self.role.value,
            "created_at": _datetime_to_iso(self.created_at),
            "updated_at": _datetime_to_iso(self.updated_at),
            "deleted_at": _datetime_to_iso(self.deleted_at),
        }

    def __repr__(self):
        return f"User(id: {self.id}, name: {self.name}, email: {self.email}, contact_number: {self.contact_number}, role: {self.role.value})"
