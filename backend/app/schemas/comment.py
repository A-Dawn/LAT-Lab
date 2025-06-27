from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CommentBase(BaseModel):
    content: str
    article_id: int
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    user_id: int
    likes: int
    is_approved: bool
    created_at: datetime
    user: Dict[str, Any]
    replies: List['Comment'] = []

    class Config:
        from_attributes = True

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    is_approved: Optional[bool] = None

class CommentLike(BaseModel):
    comment_id: int 