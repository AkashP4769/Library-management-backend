"""
API routes for Audit Logs.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from audit import service
from audit.schema import AuditLogListResponse, AuditLogResponse
from database import get_db
from models.audit import AuditAction

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get(
    "",
    response_model=AuditLogListResponse,
)
async def get_audit_logs(
    actor_user_id: int | None = Query(default=None),
    action_type: AuditAction | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> AuditLogListResponse:

    audit_logs, total = await service.get_audit_logs(
        db=db,
        actor_user_id=actor_user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        offset=offset,
        limit=limit,
    )

    return AuditLogListResponse(
        audit_logs=audit_logs,
        total=total,
    )


@router.get(
    "/{audit_id}",
    response_model=AuditLogResponse,
)
async def get_audit_log(
    audit_id: int,
    db: AsyncSession = Depends(get_db),
) -> AuditLogResponse:

    audit_log = await service.get_audit_log(
        db=db,
        audit_id=audit_id,
    )

    return AuditLogResponse.model_validate(audit_log)