"""
Business logic for AuditLog.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from audit import repo
from exceptions import NotFoundException
from models.audit import AuditAction, AuditLog


async def create_audit_log(
    db: AsyncSession,
    actor_user_id: int,
    action_type: AuditAction,
    entity_type: str,
    entity_id: str,
    old_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:

    if not entity_type.strip():
        raise ValueError("Entity type cannot be empty.")

    if not entity_id.strip():
        raise ValueError("Entity ID cannot be empty.")

    audit_log = AuditLog(
        actor_user_id=actor_user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        metadata=metadata,
    )

    return await repo.create_audit_log(
        db=db,
        audit_log=audit_log,
    )


async def get_audit_log(
    db: AsyncSession,
    audit_id: int,
) -> AuditLog:

    audit_log = await repo.get_audit_log_by_id(
        db=db,
        audit_id=audit_id,
    )

    if audit_log is None:
        raise NotFoundException("Audit log not found.")

    return audit_log


async def get_audit_logs(
    db: AsyncSession,
    actor_user_id: int | None = None,
    action_type: AuditAction | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[AuditLog], int]:

    if offset < 0:
        raise ValueError("Offset cannot be negative.")

    if limit <= 0:
        raise ValueError("Limit must be greater than zero.")

    return await repo.get_audit_logs(
        db=db,
        actor_user_id=actor_user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        offset=offset,
        limit=limit,
    )