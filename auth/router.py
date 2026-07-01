from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from auth import service as auth_service
from auth import TokenResponse
from auth.dependencies import get_current_user
from auth.schemas import (
    RegisterRequest,
    RefreshTokenRequest,
    TokenPayload,
    UpdateUserRequest,
    UserResponse,
)
from database import get_db
from exceptions import NotFoundException


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    access_token, refresh_token = await auth_service.login(
        db, form.username, form.password
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/signup", response_model=TokenResponse)
async def signup(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register(db, body)

    access_token, refresh_token = await auth_service.login(
        db, user.email, body.password
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshTokenRequest):
    token = await auth_service.refresh(body.refresh_token)

    return TokenResponse(access_token=token, refresh_token=body.refresh_token)


@router.get("/user", response_model=UserResponse)
async def getUserbyId(
    db: AsyncSession = Depends(get_db),
    _current_user: TokenPayload = Depends(get_current_user),
):
    user_id = _current_user.id
    try:
        details = await auth_service.getUserbyId(db, user_id)
    except ValueError as e:
        raise NotFoundException(str(e))

    return details


@router.patch("/user/update", response_model=UserResponse)
async def update_user(
    payload: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    try:
        return await auth_service.update_user(
            payload=payload,
            db=db,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise NotFoundException(str(e))
