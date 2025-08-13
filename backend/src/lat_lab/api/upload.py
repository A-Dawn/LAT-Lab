from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import uuid
from src.lat_lab.core.deps import get_db, get_current_user
from src.lat_lab.core.rate_limiter import create_rate_limit_dependency
from src.lat_lab.core.config import settings
from src.lat_lab.models.user import User
from src.lat_lab.utils.security import secure_filename

# 创建上传目录
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

router = APIRouter(prefix="/upload", tags=["upload"])

# 上传速率限制依赖
upload_rate_limit = create_rate_limit_dependency(
    "upload_image", 
    settings.RATE_LIMIT_UPLOAD_REQUESTS, 
    settings.RATE_LIMIT_UPLOAD_WINDOW
)

@router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _rate_limit: bool = Depends(upload_rate_limit)
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
        from src.lat_lab.utils.security import SecurityError
        SecurityError.log_error_safe(e, "文件上传", {"filename": secure_filename})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件上传失败"
        )
    finally:
        file.file.close()
    
    # 返回文件URL
    file_url = f"/uploads/{unique_filename}"
    
    return {"url": file_url, "filename": unique_filename} 