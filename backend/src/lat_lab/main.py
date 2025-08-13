#!/usr/bin/env python3
"""
LAT-LAB 主程序入口
"""
import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, List, Any, Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.lat_lab.api import api_router
from src.lat_lab.core.config import settings, DATA_DIR
from src.lat_lab.core.database import create_db_and_tables
from src.lat_lab.core.rate_limiter import rate_limiter

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
# 附加文件日志处理器（避免重复添加）
try:
    log_file_path = (DATA_DIR / "lat_lab.log")
    root_logger = logging.getLogger()
    file_handler_exists = any(
        hasattr(h, "baseFilename") and str(getattr(h, "baseFilename", "")).lower() == str(log_file_path).lower()
        for h in root_logger.handlers
    )
    if not file_handler_exists:
        file_handler = RotatingFileHandler(
            filename=str(log_file_path),
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        root_logger.addHandler(file_handler)
except Exception:
    # 静默失败，确保不影响主流程
    pass
logger = logging.getLogger("lat_lab")

# 创建FastAPI应用
app = FastAPI(
    title="LAT-LAB API",
    description="LAT-LAB博客系统API",
    version=settings.VERSION,
    # 根据环境变量禁用文档
    docs_url=None if not settings.DEBUG else "/docs",
    redoc_url=None if not settings.DEBUG else "/redoc"
)

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器 - 防止内部错误信息泄露"""
    from src.lat_lab.utils.security import SecurityError
    
    # 记录详细错误到日志
    SecurityError.log_error_safe(
        exc,
        "全局异常捕获",
        {
            "url": str(request.url),
            "method": request.method,
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    # 返回安全的错误消息
    return JSONResponse(
        status_code=500,
        content={"detail": SecurityError.GENERIC_ERROR}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    if settings.DEBUG:
        detail = exc.detail
    else:
        if exc.status_code == 500:
            detail = "内部服务器错误"
        else:
            detail = exc.detail
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    if settings.DEBUG:
        # 开发环境显示详细错误
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()}
        )
    else:
        # 生产环境简化错误
        return JSONResponse(
            status_code=422,
            content={"detail": "请求数据格式错误"}
        )

# 添加全局速率限制中间件
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """全局速率限制中间件"""
    # 跳过静态文件和非API请求
    if (request.url.path.startswith("/uploads") or 
        request.url.path.startswith("/docs") or 
        request.url.path.startswith("/redoc") or
        request.url.path.startswith("/openapi.json") or
        not request.url.path.startswith("/api")):
        return await call_next(request)
    
    # 如果速率限制被禁用，直接通过
    if not settings.RATE_LIMIT_ENABLED:
        return await call_next(request)
    
    # 检查全局API速率限制
    allowed, retry_after = rate_limiter.is_allowed(
        request, 
        "global_api", 
        settings.RATE_LIMIT_API_REQUESTS, 
        settings.RATE_LIMIT_API_WINDOW
    )
    
    if not allowed:
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        return JSONResponse(
            status_code=429,
            content={"detail": "API请求过于频繁，请稍后重试"},
            headers=headers
        )
    
    return await call_next(request)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")

# 注册API路由
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """应用启动时执行的事件"""
    logger.info("正在初始化应用...")
    
    # 确保上传目录存在
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    os.makedirs(settings.AVATARS_DIR, exist_ok=True)
    
    # 确保插件目录存在
    os.makedirs(settings.PLUGIN_DIR, exist_ok=True)
    os.makedirs(settings.PLUGIN_EXAMPLES_DIR, exist_ok=True)
    
    # 数据库初始化
    try:
        create_db_and_tables()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
    
    # 加载插件市场配置
    try:
        from src.lat_lab.services.marketplace import marketplace_service
        marketplace_data = marketplace_service.get_marketplace_data(force_refresh=True)
        if marketplace_data:
            logger.info(f"成功加载插件市场数据，共{len(marketplace_data.get('plugins', []))}个插件")
        else:
            logger.warning("未能加载插件市场数据")
    except Exception as e:
        logger.error(f"加载插件市场配置失败: {str(e)}")
    
    # 初始化插件管理器
    try:
        from src.lat_lab.utils.plugin_manager import plugin_manager
        from src.lat_lab.core.database import SessionLocal
        db = SessionLocal()
        try:
            plugin_manager.init_plugins(db)
        finally:
            db.close()
        logger.info("插件管理器初始化完成")
    except Exception as e:
        logger.error(f"初始化插件管理器失败: {str(e)}")
    
    logger.info("应用初始化完成!")

@app.get("/")
def root():
    """API根路径"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "欢迎使用LAT-LAB博客系统API，访问/docs查看API文档",
    }

@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "ok"}

def run_app():
    """命令行入口点"""
    uvicorn.run(
        "src.lat_lab.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

if __name__ == "__main__":
    run_app() 