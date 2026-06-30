from sqlalchemy.ext.asyncio import AsyncSession

from audit import service as audit_service
from auth.schemas import RegisterRequest
from auth.utils import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    refresh_access_token,
)
from exceptions import (
    ConflictException,
    UnauthorizedException,
)
from models.audit import AuditAction
from models.user import User
from user import repository


async def login(
    db: AsyncSession,
    email: str,
    password: str,
) -> tuple[str, str]:

    user: User | None = await repository.get_by_email(
        db,
        email=email,
    )

    if user is None:
        raise UnauthorizedException(
            "Invalid username or password"
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise UnauthorizedException(
            "Invalid username or password"
        )

    access_token = create_access_token(
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
    )

    refresh_token = create_refresh_token(
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=user.id,
        action_type=AuditAction.LOGIN,
        entity_type="USER",
        entity_id=str(user.id),
        metadata={
            "email": user.email,
        },
    )

    return access_token, refresh_token


async def register(
    db: AsyncSession,
    body: RegisterRequest,
) -> User:

    existing = await repository.get_by_email(
        db=db,
        email=body.email,
    )

    if existing:
        raise ConflictException(
            "User with this email already exists."
        )

    password_hash = hash_password(
        body.password,
    )

    user = User(
        name=body.name,
        email=body.email,
        password_hash=password_hash,
        contact_number=body.contact_number,
        role=body.role,
    )

    user = await repository.create(
        db=db,
        user=user,
    )

    await audit_service.create_audit_log(
        db=db,
        actor_user_id=user.id,
        action_type=AuditAction.CREATE,
        entity_type="USER",
        entity_id=str(user.id),
        new_value=user.to_api_dict(),
    )

    return user


async def refresh(
    refresh_token: str,
) -> str:

    token = refresh_access_token(
        refresh_token,
    )

    if token is None:
        raise UnauthorizedException(
            "Invalid refresh token"
        )

    return token