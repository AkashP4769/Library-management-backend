from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from auth import service as auth_service
from auth import TokenResponse
from auth.schemas import RegisterRequest, RefreshTokenRequest
from database import get_db


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    access_token, refresh_token = await auth_service.login(
        db, form.username, form.password
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register(db, body)

    access_token, refresh_token = await auth_service.login(
        db, user.email, body.password
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshTokenRequest):
    token = await auth_service.refresh(body.refresh_token)

    return TokenResponse(access_token=token, refresh_token=body.refresh_token)
