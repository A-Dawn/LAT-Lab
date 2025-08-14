from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from src.lat_lab.schemas.user import UserOut, UserUpdate, Token, PasswordReset
from src.lat_lab.crud.user import get_user, get_users, update_user, delete_user
from src.lat_lab.core.deps import get_db, get_current_user, get_current_admin_user
from src.lat_lab.models.user import User
from src.lat_lab.core.security import get_password_hash
from src.lat_lab.utils.security import secure_filename

router = APIRouter(prefix="/users", tags=["users"])

# 头像上传目录
UPLOAD_DIR = os.path.join("uploads", "avatars")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=UserOut)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
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
    original_filename = file.filename or "avatar.jpg"
    file_extension = os.path.splitext(original_filename)[1] if original_filename else ".jpg"
    # 确保文件扩展名安全
    file_extension = secure_filename(file_extension)
    if not file_extension:
        file_extension = ".jpg"  # 默认扩展名
        
    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4()}{file_extension}"
    
    # 使用安全路径构建
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()  # 读取文件内容
            buffer.write(content)  # 写入文件
    except Exception as e:
        from src.lat_lab.utils.security import SecurityError
        SecurityError.log_error_safe(e, "头像上传", {"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="头像上传失败"
        )
    
    # 更新用户头像URL，确保路径正确
    avatar_url = f"/uploads/avatars/{unique_filename}"
    
    # 更新用户信息
    user_update = UserUpdate(avatar=avatar_url)
    updated_user = update_user(db, current_user.id, user_update)
    
    return {"url": avatar_url, "success": True}

@router.get("", response_model=List[UserOut])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有用户（需要管理员权限）"""
    return get_users(db, skip=skip, limit=limit)

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

@router.post("/{user_id}/reset-password", response_model=dict)
def reset_user_password(
    user_id: int,
    password_reset: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员重置用户密码"""
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新密码
    hashed_password = get_password_hash(password_reset.new_password)
    db_user.hashed_password = hashed_password
    db.commit()
    
    return {"detail": "密码重置成功"}

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