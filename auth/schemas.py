from pydantic import BaseModel

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

class TokenPayload(BaseModel):
    id: int
    email: str
    role: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str
