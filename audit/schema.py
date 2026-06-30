
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from models.audit import AuditAction


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_user_id: int
    action_type: AuditAction
    entity_type: str
    entity_id: str
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    audit_logs: list[AuditLogResponse]
    total: int