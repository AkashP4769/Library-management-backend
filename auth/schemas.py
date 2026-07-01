from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    contact_number: str | None = None
    role: str | None = "employee"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

    user_id: int | None = None
    name: str | None = None
    email: str | None = None
    contact_number: str | None = None
    role: str | None = None


class TokenPayload(BaseModel):
    id: int
    email: str
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    contact_number: str | None = None
    role: str | None = None


class UpdateUserRequest(BaseModel):
    name: str
    email: str
    contact_number: str | None = None
