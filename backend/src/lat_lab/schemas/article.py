from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from src.lat_lab.schemas.user import UserOut

class ArticleStatus(str, Enum):
    draft = "draft"
    published = "published"

class ArticleVisibility(str, Enum):
    public = "public"
    private = "private"
    password = "password"

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    is_pinned: Optional[bool] = False
    is_approved: Optional[bool] = False
    category_id: Optional[int] = None
    status: Optional[ArticleStatus] = ArticleStatus.published
    published_at: Optional[datetime] = None
    visibility: Optional[ArticleVisibility] = ArticleVisibility.public
    password: Optional[str] = Field(None, exclude=True)

class ArticleCreate(ArticleBase):
    tags: Optional[List[str]] = []

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_approved: Optional[bool] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    status: Optional[ArticleStatus] = None
    published_at: Optional[datetime] = None
    visibility: Optional[ArticleVisibility] = None
    password: Optional[str] = None

class Article(ArticleBase):
    id: int
    author_id: int
    view_count: int
    likes_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime
    tags: List[Tag] = []
    category: Optional[Category] = None
    author: Optional[UserOut] = None

    class Config:
        from_attributes = True

class ArticleDetail(Article):
    author: Optional[UserOut] = None

    class Config:
        from_attributes = True