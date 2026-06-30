"""
Repository functions for AuditLog.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.audit import AuditAction, AuditLog


async def create_audit_log(
    db: AsyncSession,
    audit_log: AuditLog,
) -> AuditLog:
    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)
    return audit_log


async def get_audit_log_by_id(
    db: AsyncSession,
    audit_id: int,
) -> AuditLog | None:
    result = await db.execute(
        select(AuditLog).where(AuditLog.id == audit_id)
    )
    return result.scalar_one_or_none()


async def get_audit_logs(
    db: AsyncSession,
    actor_user_id: int | None = None,
    action_type: AuditAction | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[AuditLog], int]:

    query = select(AuditLog)

    count_query = select(func.count()).select_from(AuditLog)

    if actor_user_id is not None:
        query = query.where(AuditLog.actor_user_id == actor_user_id)
        count_query = count_query.where(
            AuditLog.actor_user_id == actor_user_id
        )

    if action_type is not None:
        query = query.where(AuditLog.action_type == action_type)
        count_query = count_query.where(
            AuditLog.action_type == action_type
        )

    if entity_type is not None:
        query = query.where(AuditLog.entity_type == entity_type)
        count_query = count_query.where(
            AuditLog.entity_type == entity_type
        )

    if entity_id is not None:
        query = query.where(AuditLog.entity_id == entity_id)
        count_query = count_query.where(
            AuditLog.entity_id == entity_id
        )

    query = (
        query.order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    audit_logs = (await db.execute(query)).scalars().all()

    total = (await db.execute(count_query)).scalar_one()

    return audit_logs, total