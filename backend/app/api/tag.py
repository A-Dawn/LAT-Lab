from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_db, get_current_admin
from app.models.tag import Tag
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/admin/tags", tags=["tags"])

# 标签模型
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    article_count: int = 0
    
    class Config:
        from_attributes = True

# 创建一个公开的API路由，用于获取所有标签
public_router = APIRouter(prefix="/articles", tags=["articles"])

@public_router.get("/tags", response_model=List[TagResponse])
def get_public_tags(db: Session = Depends(get_db)):
    """获取所有标签（公开API，不需要权限）"""
    # 查询所有标签
    tags = db.query(Tag).all()
    
    # 计算每个标签关联的文章数量
    result = []
    for tag in tags:
        tag_dict = {
            "id": tag.id,
            "name": tag.name,
            "article_count": len(tag.articles)
        }
        result.append(tag_dict)
    
    return result

# 获取所有标签（管理员）
@router.get("/", response_model=List[TagResponse])
def get_all_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取所有标签（需要管理员权限）"""
    # 查询所有标签及其关联的文章数量
    tags = db.query(Tag).all()
    
    # 计算每个标签关联的文章数量
    result = []
    for tag in tags:
        tag_dict = {
            "id": tag.id,
            "name": tag.name,
            "article_count": len(tag.articles)
        }
        result.append(tag_dict)
    
    return result

# 创建新标签
@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """创建新标签（需要管理员权限）"""
    # 检查标签是否已存在
    db_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if db_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签已存在"
        )
    
    # 创建新标签
    new_tag = Tag(name=tag.name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    
    return {
        "id": new_tag.id,
        "name": new_tag.name,
        "article_count": 0
    }

# 更新标签
@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """更新标签（需要管理员权限）"""
    # 查找标签
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    # 检查新名称是否与其他标签重复
    existing_tag = db.query(Tag).filter(Tag.name == tag.name, Tag.id != tag_id).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签名称已存在"
        )
    
    # 更新标签
    db_tag.name = tag.name
    db.commit()
    db.refresh(db_tag)
    
    return {
        "id": db_tag.id,
        "name": db_tag.name,
        "article_count": len(db_tag.articles)
    }

# 删除标签
@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """删除标签（需要管理员权限）"""
    # 查找标签
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    # 删除标签
    db.delete(db_tag)
    db.commit()
    
    return None 