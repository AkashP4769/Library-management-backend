"""
Database model for AuditLog.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import Enum as SQLEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Entity


def _datetime_to_iso(value: datetime |None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    BORROW = "BORROW"
    RETURN = "RETURN"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class AuditLog(Entity):
    __abstract__ = False
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    action_type: Mapped[AuditAction] = mapped_column(
        SQLEnum(AuditAction),
        nullable=False,
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    entity_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    old_value: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    new_value: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    audit_metadata: Mapped[dict[str, Any] | None] = mapped_column(
    "metadata",
    JSONB,
    nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="audit_logs",
    )

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "actor_user_id": self.actor_user_id,
            "action_type": self.action_type.value,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "metadata": self.metadata,
            "created_at": _datetime_to_iso(self.created_at),
            "updated_at": _datetime_to_iso(self.updated_at),
            "deleted_at": _datetime_to_iso(self.deleted_at),
        }

    def __repr__(self):
        return (
            f"AuditLog("
            f"id={self.id}, "
            f"actor_user_id={self.actor_user_id}, "
            f"action_type='{self.action_type.value}', "
            f"entity_type='{self.entity_type}', "
            f"entity_id='{self.entity_id}'"
            f")"
        )