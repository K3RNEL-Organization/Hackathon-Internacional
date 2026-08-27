from pydantic import BaseModel, EmailStr

from .models import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    name: str
    email: EmailStr


class UserOut(BaseModel):
    email: EmailStr
    name: str
    role: UserRole

    model_config = {"from_attributes": True}
