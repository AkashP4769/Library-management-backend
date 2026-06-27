from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import RegisterRequest
from auth.utils import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    refresh_access_token,
)
from user import repository
from exceptions import UnauthorizedException
from models.user import User


async def login(db: AsyncSession, email: str, password: str) -> tuple[str, str]:
    user: User = await repository.get_by_email(db, email=email)

    if user is None:
        print("/login - user is None")
        raise UnauthorizedException("Invalid username or password")

    if not verify_password(password, user.password_hash):
        print("/login - invalid password")
        raise UnauthorizedException("Invalid username or password")

    access_token = create_access_token(
        {"id": user.id, "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(
        {"id": user.id, "email": user.email, "role": user.role}
    )

    print("/login - successful login")
    return access_token, refresh_token

async def register(db: AsyncSession, body: RegisterRequest) -> User:
    password_hash = hash_password(body.password)
    user = User(
        name=body.name,
        email=body.email,
        password_hash=password_hash,
        contact_number=body.contact_number,
        role=body.role,
    )

    user = await repository.create(db, user)
    return user


async def refresh(refresh_token: str) -> str:
    token = refresh_access_token(refresh_token)

    if token is None:
        raise UnauthorizedException("Invalid refresh token")

    return token
