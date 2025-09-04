from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.lat_lab.core.database import SessionLocal
from src.lat_lab.core.security import SECRET_KEY, ALGORITHM
from src.lat_lab.schemas.user import TokenData
from src.lat_lab.models.user import User, RoleEnum
from src.lat_lab.crud.user import get_user_by_username, get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# 可选的OAuth2方案，用于支持访客模式
class OptionalOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        try:
            return await super().__call__(request)
        except HTTPException:
            return None

oauth2_scheme_optional = OptionalOAuth2PasswordBearer(tokenUrl="auth/login")

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
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(username=email)  # 保持兼容性，但实际存储的是邮箱
    except JWTError:
        raise credentials_exception
    
    # 使用邮箱查找用户，确保token的稳定性
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_optional_user(
    request: Request,
    db: Session = Depends(get_db), 
    token: Optional[str] = Depends(oauth2_scheme_optional)
) -> Optional[User]:
    """
    获取可选用户，支持访客模式
    如果没有token或token无效，则返回None（访客模式）
    如果有有效token，则返回用户对象
    """
    # 检查是否是访客模式请求
    guest_mode = request.headers.get('X-Guest-Mode') == 'true'
    
    if not token:
        # 没有token，允许访客模式
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        
        # 使用邮箱查找用户
        user = get_user_by_email(db, email=email)
        return user
    except JWTError:
        # JWT解析失败，如果是访客模式则允许，否则返回None
        return None

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