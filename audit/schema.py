
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from models.audit import AuditAction


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    actor_user_id: int
    actor_user_name: str | None = None
    action_type: AuditAction
    entity_type: str
    entity_id: str
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    audit_metadata: dict[str, Any] | None = Field(
        default=None,
        serialization_alias="metadata",
    )
    created_at: datetime


class AuditLogListResponse(BaseModel):
    audit_logs: list[AuditLogResponse]
    total: int
