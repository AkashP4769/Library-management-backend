from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from admin import service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
):
    return await service.get_dashboard_metrics(db)


@router.get("/circulation-trends")
async def get_circulation_trends(
    range: str = "30d",
    db: AsyncSession = Depends(get_db),
):
    return await service.get_circulation_trends(db, range)


@router.get("/recent-activities")
async def get_recent_activities(db: AsyncSession = Depends(get_db), range: str = "30d"):
    return await service.get_recent_activities(db)


@router.get("/inventory-summary")
async def get_inventory_summary(
    db: AsyncSession = Depends(get_db),
):
    return await service.get_inventory_summary(db)


@router.get("/top-books")
async def get_top_books(
    db: AsyncSession = Depends(get_db),
):
    return await service.get_top_books(db)


@router.get("/shelf-sage")
async def get_shelf_sage(
    db: AsyncSession = Depends(get_db),
):
    return await service.get_shelf_sage(db)
