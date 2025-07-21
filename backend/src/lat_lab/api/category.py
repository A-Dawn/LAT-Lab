from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.lat_lab.schemas.article import Category, CategoryCreate
from src.lat_lab.crud.category import get_category, get_categories, create_category, update_category, delete_category, get_category_by_name
from src.lat_lab.core.deps import get_db, get_current_user, get_current_admin_user
from src.lat_lab.models.user import User, RoleEnum

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有分类"""
    categories = get_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/{category_id}", response_model=Category)
def read_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """获取分类详情"""
    db_category = get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    return db_category

@router.post("/", response_model=Category)
def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建分类（需要管理员权限）"""
    # 检查分类名是否已存在
    if get_category_by_name(db, category.name):
        raise HTTPException(status_code=400, detail="分类名已存在")
    
    return create_category(db, category)

@router.put("/{category_id}", response_model=Category)
def update_category_by_id(
    category_id: int,
    category_update: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新分类（需要管理员权限）"""
    db_category = get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查更新后的分类名是否与其他分类冲突
    existing_category = get_category_by_name(db, category_update.name)
    if existing_category and existing_category.id != category_id:
        raise HTTPException(status_code=400, detail="分类名已存在")
    
    return update_category(db, category_id, category_update)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_by_id(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除分类（需要管理员权限）"""
    db_category = get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    delete_category(db, category_id)
    return None 