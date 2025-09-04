from sqlalchemy import Column, Integer, String, Enum, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from src.lat_lab.core.database import Base

class RoleEnum(str, enum.Enum):
    visitor = "visitor"      # 访客
    user = "user"            # 正常用户
    admin = "admin"          # 管理员

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)
    avatar = Column(Text, nullable=True)  # 用户头像URL
    bio = Column(Text, nullable=True)     # 用户简介
    
    # 邮箱验证相关字段
    is_verified = Column(Boolean, default=False)  # 是否已验证邮箱
    verification_token = Column(String(128), nullable=True)  # 验证令牌
    token_created_at = Column(DateTime, nullable=True)  # 令牌创建时间
    
    # 关联关系
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    plugins = relationship("Plugin", back_populates="creator", cascade="all, delete-orphan") 