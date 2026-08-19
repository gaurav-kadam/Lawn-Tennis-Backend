from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    """
    Public self-registration payload (POST /auth/register - no auth required).
    Deliberately has NO role_id field: a caller who is not yet authenticated
    must never be able to choose their own role (that would let anyone
    self-assign "Supervisor" and get full access). The service always
    assigns the lowest-privilege role ("Scorer") to accounts created here.
    """
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class UserCreate(BaseModel):
    """
    Admin-created user (POST /users - Supervisor only, see base_routes.py).
    role_id is trusted here because the caller has already been authenticated
    AND authorized as Supervisor at the router level.
    """
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    role_id: int


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True
