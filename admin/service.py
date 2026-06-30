from sqlalchemy.ext.asyncio import AsyncSession
from admin import repo


async def get_dashboard_metrics(db: AsyncSession):
    total_borrowed = await repo.count_total_borrowed(db)
    active_users = await repo.count_active_users(db)
    overdue_items = await repo.count_overdue_items(db)
    popular_genre = await repo.get_most_popular_genre(db)

    return {
        "total_borrowed": total_borrowed,
        "active_users": active_users,
        "overdue_items": overdue_items,
        "most_popular_genre": popular_genre,
    }


async def get_circulation_trends(db: AsyncSession, range: str):
    return await repo.get_circulation_trends(db, range)


async def get_recent_activities(db: AsyncSession, range: str = "30d"):
    return await repo.get_recent_activities(db, range)


async def get_inventory_summary(db: AsyncSession):
    return await repo.get_inventory_summary(db)


async def get_top_books(db: AsyncSession):
    return await repo.get_top_books(db)


async def get_shelf_sage(db: AsyncSession):
    return await repo.get_shelf_sage(db)
