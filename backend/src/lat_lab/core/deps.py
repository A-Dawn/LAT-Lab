from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.lat_lab.core.database import SessionLocal
from src.lat_lab.core.security import SECRET_KEY, ALGORITHM
from src.lat_lab.schemas.user import TokenData
from src.lat_lab.models.user import User, RoleEnum
from src.lat_lab.crud.user import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限",
        )
    return current_user

# 简化的管理员依赖，用于标签管理等API
get_current_admin = get_current_admin_user

async def get_current_author_or_admin(
    current_user: User = Depends(get_current_user), 
    author_id: Optional[int] = None
) -> User:
    if current_user.role == RoleEnum.admin or (author_id and current_user.id == author_id):
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="权限不足，需要作者或管理员权限",
    ) 