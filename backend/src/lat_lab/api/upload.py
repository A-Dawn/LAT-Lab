from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from src.lat_lab.core.deps import get_db, get_current_user
from src.lat_lab.core.rate_limiter import create_rate_limit_dependency
from src.lat_lab.core.config import settings
from src.lat_lab.models.user import User
from src.lat_lab.utils.security import secure_filename, detect_image_type

# 确保上传目录存在（使用配置路径）
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)

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
    # 读取并限制文件大小
    content = await file.read(settings.MAX_UPLOAD_SIZE + 1)
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件内容为空")
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="文件过大")

    # 基于魔数检测图片类型（拒绝svg等非位图）
    mime, detected_ext = detect_image_type(content)
    if not mime or not detected_ext:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的图片格式")

    # 生成唯一安全文件名（基于检测到的扩展名）
    unique_filename = f"{uuid.uuid4()}{detected_ext}"

    # 保存到安全目录
    file_path = os.path.join(str(settings.UPLOADS_DIR), unique_filename)
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        try:
            os.chmod(file_path, 0o644)
        except Exception:
            # 非关键路径，忽略权限设置错误（不同平台可能不支持）
            pass
    except Exception as e:
        from src.lat_lab.utils.security import SecurityError
        SecurityError.log_error_safe(e, "文件上传", {"filename": unique_filename})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件上传失败"
        )
    finally:
        await file.close()
    
    # 返回文件URL
    file_url = f"/uploads/{unique_filename}"
    
    return {"url": file_url, "filename": unique_filename}