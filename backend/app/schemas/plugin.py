from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PluginTagBase(BaseModel):
    name: str

class PluginTag(PluginTagBase):
    class Config:
        from_attributes = True

class PluginCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class PluginCategoryCreate(PluginCategoryBase):
    pass

class PluginCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class PluginCategory(PluginCategoryBase):
    id: int
    
    class Config:
        from_attributes = True

class PluginReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class PluginReviewCreate(PluginReviewBase):
    pass

class PluginReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class PluginReview(PluginReviewBase):
    id: int
    plugin_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PluginBase(BaseModel):
    name: str
    description: Optional[str] = None
    code: str
    version: Optional[str] = "0.1.0"
    is_public: Optional[bool] = True

class PluginCreate(PluginBase):
    pass

class PluginUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None
    version: Optional[str] = None
    is_public: Optional[bool] = None

class Plugin(PluginBase):
    id: int
    creator_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PluginDetail(Plugin):
    """包含详细插件信息"""
    
    class Config:
        from_attributes = True

class PluginSearchQuery(BaseModel):
    query: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    creator_id: Optional[int] = None
    featured: Optional[bool] = None
    min_rating: Optional[float] = None
    sort_by: Optional[str] = "created_at"  # 可选值: created_at, updated_at, rating, downloads
    sort_order: Optional[str] = "desc"  # 可选值: asc, desc
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None 