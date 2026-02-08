from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: Optional[str] = None
    fullName: str


class UserLogin(BaseModel):
    email: EmailStr
    password: Optional[str] = None


class User(BaseModel):
    userId: UUID
    email: EmailStr
    fullName: str
    createdAt: datetime
    profession: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
