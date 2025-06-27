from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

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
    category_id: Optional[int] = None
    status: Optional[ArticleStatus] = ArticleStatus.published
    published_at: Optional[datetime] = None
    visibility: Optional[ArticleVisibility] = ArticleVisibility.public
    password: Optional[str] = None

class ArticleCreate(ArticleBase):
    tags: Optional[List[str]] = []

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    is_pinned: Optional[bool] = None
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

    class Config:
        from_attributes = True

class ArticleDetail(Article):
    author: Dict[str, Any]

    class Config:
        from_attributes = True
        
        @classmethod
        def from_orm(cls, obj):
            if hasattr(obj, 'author') and obj.author is not None:
                data = {
                    attr: getattr(obj, attr)
                    for attr in [a for a in dir(obj) if not a.startswith('_') and a != 'metadata']
                    if hasattr(obj, attr)
                }
                
                if isinstance(obj.author, object) and hasattr(obj.author, '__dict__'):
                    author_dict = {
                        "id": obj.author.id,
                        "username": obj.author.username,
                        "email": obj.author.email,
                        "role": obj.author.role
                    }
                    data['author'] = author_dict
                
                return super().from_orm(type('TempObj', (object,), data))
            
            return super().from_orm(obj) 