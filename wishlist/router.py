"""
API routes for Wishlist.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from database.connection import get_db
from wishlist import service
from wishlist.schemas import (
    WishlistBookResponse,
    WishlistCreateRequest,
    WishlistResponse,
)

router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"],
)


@router.post(
    "",
    response_model=WishlistResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_to_wishlist(
    request: WishlistCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    return await service.add_to_wishlist(
        db=db,
        current_user=current_user,
        request=request,
    )


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_from_wishlist(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    await service.remove_from_wishlist(
        db=db,
        current_user=current_user,
        book_id=book_id,
    )


@router.get(
    "",
    response_model=list[WishlistBookResponse],
)
async def get_user_wishlist(
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    return await service.get_user_wishlist(
        db=db,
        current_user=current_user,
    )