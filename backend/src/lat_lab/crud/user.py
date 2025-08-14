from sqlalchemy.orm import Session
from src.lat_lab.models.user import User, RoleEnum
from src.lat_lab.schemas.user import UserCreate, UserUpdate
from src.lat_lab.core.security import get_password_hash, verify_password
from src.lat_lab.core.email import generate_verification_token, is_token_expired
from typing import Optional, List
from datetime import datetime

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_verification_token(db: Session, token: str):
    return db.query(User).filter(User.verification_token == token).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate, role: RoleEnum = RoleEnum.user, send_verification: bool = True):
    # 生成验证令牌
    verification_token = generate_verification_token()
    
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=role,
        verification_token=verification_token,
        token_created_at=datetime.now(),
        is_verified=False  # 默认未验证
    )
    
    # 如果是管理员，自动验证
    if role == RoleEnum.admin:
        db_user.is_verified = True
        db_user.verification_token = None
        db_user.token_created_at = None
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    # 不允许修改邮箱，确保邮箱作为固定的身份标识符
    if "email" in update_data:
        update_data.pop("email")
    
    if "role" in update_data and db_user.role != RoleEnum.admin:
        update_data.pop("role")
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_email(db: Session, token: str):
    """验证邮箱"""
    user = get_user_by_verification_token(db, token)
    
    if not user:
        return None
    
    # 检查令牌是否过期
    if is_token_expired(user.token_created_at):
        return None
    
    # 更新用户为已验证状态
    user.is_verified = True
    user.verification_token = None  # 清除令牌
    user.token_created_at = None
    
    db.commit()
    db.refresh(user)
    return user

def regenerate_verification_token(db: Session, user_id: int):
    """重新生成验证令牌"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    # 如果用户已验证，不需要重新生成
    if user.is_verified:
        return None
    
    # 生成新令牌
    user.verification_token = generate_verification_token()
    user.token_created_at = datetime.now()
    
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user 