from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import uuid
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.crud.user import create_user, get_user, get_user_by_username, get_user_by_email, get_users, update_user, delete_user
from app.core.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User, RoleEnum

# 创建上传目录
UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # 使用exist_ok参数，确保目录存在

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return current_user

@router.put("/me", response_model=UserOut)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前登录用户信息"""
    # 普通用户不能修改自己的角色
    if user_update.role is not None and current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改用户角色"
        )
    
    # 不允许修改邮箱
    if user_update.email is not None and user_update.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱作为身份标识符不允许修改"
        )
    
    return update_user(db, current_user.id, user_update)

@router.post("/me/avatar", response_model=dict)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传用户头像"""
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能上传图片文件"
        )
    
    # 确保上传目录存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()  # 读取文件内容
            buffer.write(content)  # 写入文件
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )
    
    # 更新用户头像URL，确保路径正确
    avatar_url = f"/uploads/avatars/{unique_filename}"
    
    # 更新用户信息
    user_update = UserUpdate(avatar=avatar_url)
    updated_user = update_user(db, current_user.id, user_update)
    
    return {"url": avatar_url, "success": True}

@router.get("/{user_id}", response_model=UserOut)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定用户信息"""
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.get("/", response_model=List[UserOut])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有用户（仅管理员）"""
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.put("/{user_id}", response_model=UserOut)
def update_user_by_admin(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员更新用户信息"""
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 即使是管理员也不能修改用户邮箱
    if user_update.email is not None and user_update.email != db_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱作为身份标识符不允许修改"
        )
    
    return update_user(db, user_id, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员删除用户"""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")
    
    result = delete_user(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return None 