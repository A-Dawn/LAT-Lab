#!/usr/bin/env python3
"""
LAT-LAB 主程序入口
"""
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, List, Any, Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.lat_lab.api import api_router
from src.lat_lab.core.config import settings
from src.lat_lab.core.database import create_db_and_tables

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
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