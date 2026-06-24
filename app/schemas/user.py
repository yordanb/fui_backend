from pydantic import BaseModel
from datetime import datetime
from pydantic import EmailStr
from typing import List

class UserResponse(BaseModel):
    id: int
    username: str
    fullname: str | None = None
    email: str | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

class UserResponseWithRoles(UserResponse):
    roles: List[str] = []

class UserCreate(BaseModel):
    username: str
    fullname: str
    email: str
    password: str
    role_ids: List[int]
    is_active: bool = True

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserUpdate(BaseModel):
    fullname: str
    email: str
    role_ids: List[int]
    is_active: bool = True

class UserPasswordReset(BaseModel):
    password: str
