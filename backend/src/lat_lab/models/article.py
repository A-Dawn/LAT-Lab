from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .user import Base
import enum

class ArticleStatus(str, enum.Enum):
    draft = "draft"
    published = "published"

class ArticleVisibility(str, enum.Enum):
    public = "public"
    private = "private"
    password = "password"

# 用户文章点赞关联表
article_likes = Table(
    "article_likes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now())
)

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(200))
    is_pinned = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    status = Column(Enum(ArticleStatus), default=ArticleStatus.published, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    visibility = Column(Enum(ArticleVisibility), default=ArticleVisibility.public, nullable=False)
    password = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 外键
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # 关联关系
    author = relationship("User", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    tags = relationship("Tag", secondary="article_tags", back_populates="articles")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    
    # 添加点赞关联
    liked_by = relationship("User", secondary=article_likes, backref="liked_articles") 