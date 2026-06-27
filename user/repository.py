
from select import select

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from exceptions import ConflictException


async def create(db: AsyncSession, user: User) -> User:
    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(detail=f"Email '{user.email}' is already in use")

    await db.refresh(user)
    return user

async def get_by_email(db: AsyncSession, email: str) -> User:
    stmt = select(User).where(
        User.email == email, User.deleted_at.is_(None)
    )

    res = await db.scalars(stmt)

    return res.first()