"""
Database engine and session factory (async).

Uses SQLAlchemy async engine backed by asyncpg so every DB call is
non-blocking and stays on the event-loop thread instead of occupying a
thread-pool worker.
"""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import setting
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for ORM mapped classes (entities)."""


engine = create_async_engine(
    setting.database_url, echo=False, pool_size=10, max_overflow=20
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """One AsyncSession per request; closed after the request."""
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables() -> None:
    """Create tables for all ORM models that inherit from Base."""
    import models.employee  # noqa: F401 — registers the mapper before create_all

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
