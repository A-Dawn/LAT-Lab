from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import uuid
import re
from src.lat_lab.core.deps import get_db, get_current_user
from src.lat_lab.models.user import User

# 添加安全的路径验证函数
def secure_filename(filename):
    """安全地验证文件名，防止路径遍历攻击
    
    Args:
        filename (str): 要验证的文件名
        
    Returns:
        str: 安全的文件名（移除路径分隔符和特殊字符）
    """
    # 仅保留文件名，移除任何路径信息
    basename = os.path.basename(filename)
    
    # 移除可能导致问题的特殊字符
    basename = re.sub(r'[^a-zA-Z0-9_.-]', '', basename)
    
    # 确保不以点或破折号开头
    if basename.startswith(('.', '-')):
        basename = 'x' + basename
        
    # 确保不为空
    if not basename:
        basename = 'untitled'
        
    return basename

# 创建上传目录
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传图片（需要登录）"""
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能上传图片文件"
        )
    
    # 生成唯一文件名
    original_filename = file.filename or "image.jpg"
    file_extension = os.path.splitext(original_filename)[1]
    # 确保文件扩展名安全
    file_extension = secure_filename(file_extension)
    if not file_extension:
        file_extension = ".jpg"  # 默认扩展名
    
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # 使用安全路径构建
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )
    finally:
        file.file.close()
    
    # 返回文件URL
    file_url = f"/uploads/{unique_filename}"
    
    return {"url": file_url, "filename": unique_filename} 