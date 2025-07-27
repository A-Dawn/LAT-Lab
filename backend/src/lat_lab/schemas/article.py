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
            try:
                # 创建原始数据的副本
                data = {}
                for attr in dir(obj):
                    if not attr.startswith('_') and attr != 'metadata' and hasattr(obj, attr):
                        try:
                            data[attr] = getattr(obj, attr)
                        except Exception:
                            # 忽略无法获取的属性
                            pass
                
                # 处理author字段
                if hasattr(obj, 'author') and obj.author is not None:
                    # 确保author被转换为字典
                    try:
                        author_obj = obj.author
                        author_dict = {
                            "id": author_obj.id,
                            "username": author_obj.username,
                            "email": author_obj.email,
                            "role": author_obj.role
                        }
                        
                        # 添加可能存在的头像和简介
                        if hasattr(author_obj, 'avatar') and author_obj.avatar is not None:
                            author_dict["avatar"] = author_obj.avatar
                        
                        if hasattr(author_obj, 'bio') and author_obj.bio is not None:
                            author_dict["bio"] = author_obj.bio
                            
                        data['author'] = author_dict
                    except Exception as e:
                        # 如果处理失败，创建最小化的作者信息
                        print(f"处理作者信息时出错: {str(e)}")
                        data['author'] = {"id": getattr(obj.author, 'id', 0), "username": "未知用户"}
                else:
                    # 如果没有作者信息，提供默认值
                    data['author'] = {"id": 0, "username": "匿名"}
                
                # 创建临时对象并使用父类方法处理
                temp_obj = type('TempObj', (object,), data)
                return super().from_orm(temp_obj)
                
            except Exception as e:
                print(f"文章详情转换错误: {str(e)}")
                # 发生错误时，尝试基本转换
                return super().from_orm(obj) 