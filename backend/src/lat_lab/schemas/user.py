from pydantic import BaseModel, EmailStr
from typing import Optional
from src.lat_lab.models.user import RoleEnum
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None

class UserOut(UserBase):
    id: int
    role: RoleEnum
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool = False

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[RoleEnum] = None 

class EmailVerification(BaseModel):
    token: str

# 添加重置密码的Schema
class PasswordReset(BaseModel):
    new_password: str 