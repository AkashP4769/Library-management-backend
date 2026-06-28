"""
Repository layer for Shelf.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.shelf import Shelf


async def create(
    db: AsyncSession,
    shelf: Shelf,
) -> Shelf:
    db.add(shelf)
    await db.commit()
    await db.refresh(shelf)

    return shelf


async def get_all(
    db: AsyncSession,
) -> list[Shelf]:
    result = await db.execute(
        select(Shelf)
    )

    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession,
    shelf_id: int,
) -> Shelf | None:
    result = await db.execute(
        select(Shelf).where(
            Shelf.id == shelf_id,
        )
    )

    return result.scalar_one_or_none()


async def get_by_shelf_code(
    db: AsyncSession,
    shelf_code: str,
) -> Shelf | None:
    result = await db.execute(
        select(Shelf).where(
            Shelf.shelf_code == shelf_code,
        )
    )

    return result.scalar_one_or_none()


async def update(
    db: AsyncSession,
    shelf: Shelf,
) -> Shelf:
    await db.commit()
    await db.refresh(shelf)

    return shelf


async def delete(
    db: AsyncSession,
    shelf: Shelf,
) -> None:
    await db.delete(shelf)
    await db.commit()