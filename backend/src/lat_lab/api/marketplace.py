#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件市场API
提供插件市场相关的API端点
"""

import os
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
import logging
from src.lat_lab.services.marketplace import marketplace_service
from src.lat_lab.core.config import settings
from src.lat_lab.core.deps import get_current_user, get_current_admin_user
from src.lat_lab.models.user import User
from pydantic import BaseModel, Field

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketplace", tags=["插件市场"])

class Category(BaseModel):
    """分类模型"""
    id: int
    name: str
    description: Optional[str] = None

class Plugin(BaseModel):
    """插件模型"""
    id: str
    name: str
    description: str
    version: str
    category_id: Optional[int] = None
    tags: List[str] = []
    author: Optional[str] = None
    author_url: Optional[str] = None
    repository_url: Optional[str] = None
    download_url: Optional[str] = None
    icon: Optional[str] = None
    featured: bool = False
    rating: Optional[float] = None
    ratings_count: Optional[int] = None
    downloads: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    screenshots: List[str] = []
    readme: Optional[str] = None

class MarketplaceInfo(BaseModel):
    """市场信息模型"""
    version: str
    last_updated: str
    description: Optional[str] = None

class MarketplaceData(BaseModel):
    """市场数据模型"""
    marketplace_info: MarketplaceInfo
    categories: List[Category]
    tags: List[str]
    plugins: List[Plugin]

class SourceSettings(BaseModel):
    """数据源设置模型"""
    source: str = Field(..., description="数据源类型，'local' 或 'git'")
    git_repo: Optional[str] = Field(None, description="Git仓库地址 (仅当source为'git'时需要)")

@router.get("/", response_model=MarketplaceData)
def get_marketplace_data(
    force_refresh: bool = False,
    current_user: User = Depends(get_current_user)
):
    """
    获取完整的插件市场数据
    """
    try:
        data = marketplace_service.get_marketplace_data(force_refresh=force_refresh)
        if not data:
            logger.error("插件市场数据为空")
            raise HTTPException(status_code=404, detail="插件市场数据不可用")
        return data
    except Exception as e:
        logger.exception(f"获取插件市场数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取插件市场数据失败: {str(e)}")

@router.get("/info", response_model=MarketplaceInfo)
def get_marketplace_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取插件市场信息
    """
    try:
        info = marketplace_service.get_marketplace_info()
        if not info:
            logger.error("插件市场信息为空")
            raise HTTPException(status_code=404, detail="插件市场信息不可用")
        return info
    except Exception as e:
        logger.exception(f"获取插件市场信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取插件市场信息失败: {str(e)}")

@router.get("/plugins", response_model=List[Plugin])
def get_plugins(
    category_id: Optional[int] = None,
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取插件列表，支持筛选
    """
    try:
        logger.info(f"获取插件列表: category_id={category_id}, tags={tags}, search={search}, featured={featured}")
        plugins = marketplace_service.get_plugins(
            category_id=category_id,
            tags=tags,
            search_term=search,
            featured=featured
        )
        logger.info(f"成功获取插件列表，共{len(plugins)}个插件")
        return plugins
    except Exception as e:
        logger.exception(f"获取插件列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取插件列表失败: {str(e)}")

@router.get("/plugins/{plugin_id}", response_model=Plugin)
def get_plugin(
    plugin_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取插件详情
    """
    try:
        plugin = marketplace_service.get_plugin_by_id(plugin_id)
        if not plugin:
            logger.warning(f"未找到插件: {plugin_id}")
            raise HTTPException(status_code=404, detail=f"未找到ID为'{plugin_id}'的插件")
        return plugin
    except Exception as e:
        logger.exception(f"获取插件详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取插件详情失败: {str(e)}")

@router.get("/categories", response_model=List[Category])
def get_categories(
    current_user: User = Depends(get_current_user)
):
    """
    获取所有分类
    """
    try:
        categories = marketplace_service.get_categories()
        logger.info(f"成功获取分类列表，共{len(categories)}个分类")
        return categories
    except Exception as e:
        logger.exception(f"获取分类列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取分类列表失败: {str(e)}")

@router.get("/tags", response_model=List[str])
def get_tags(
    current_user: User = Depends(get_current_user)
):
    """
    获取所有标签
    """
    try:
        tags = marketplace_service.get_tags()
        logger.info(f"成功获取标签列表，共{len(tags)}个标签")
        return tags
    except Exception as e:
        logger.exception(f"获取标签列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取标签列表失败: {str(e)}")

@router.post("/refresh", response_model=dict)
def refresh_marketplace_data(
    current_user: User = Depends(get_current_admin_user)
):
    """
    强制刷新插件市场数据（仅管理员）
    """
    try:
        # 如果是本地数据源，先检查配置文件路径
        if settings.PLUGIN_MARKETPLACE_SOURCE.lower() == "local":
            # 检查配置文件是否存在
            local_path = os.path.abspath(settings.PLUGIN_MARKETPLACE_LOCAL_PATH)
            if not os.path.exists(local_path):
                logger.warning(f"刷新前检查: 配置文件不存在: {local_path}")
                
                # 获取当前工作目录和项目根目录
                cwd = os.getcwd()
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
                
                # 尝试在几个常见位置查找配置文件
                possible_paths = [
                    os.path.join(cwd, "marketplace_config.json"),
                    os.path.join(project_root, "marketplace_config.json"),
                    os.path.join(project_root, "src", "lat_lab", "marketplace_config.json"),
                    os.path.join(os.path.dirname(__file__), "../marketplace_config.json")
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        logger.info(f"刷新前检查: 找到配置文件: {path}")
                        settings.PLUGIN_MARKETPLACE_LOCAL_PATH = path
                        break
        
        # 强制刷新数据
        marketplace_service.get_marketplace_data(force_refresh=True)
        logger.info("插件市场数据已刷新")
        return {"status": "success", "message": "插件市场数据已刷新"}
    except Exception as e:
        logger.exception(f"刷新插件市场数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"刷新插件市场数据失败: {str(e)}")

@router.get("/source", response_model=Dict[str, Any])
def get_source_settings(
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取当前插件市场数据源设置（仅管理员）
    """
    try:
        settings = marketplace_service.get_source_settings()
        logger.info(f"获取数据源设置: {settings}")
        return settings
    except Exception as e:
        logger.exception(f"获取数据源设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取数据源设置失败: {str(e)}")

@router.post("/source", response_model=Dict[str, Any])
def update_source_settings(
    settings: SourceSettings,
    current_user: User = Depends(get_current_admin_user)
):
    """
    更新插件市场数据源设置（仅管理员）
    """
    try:
        logger.info(f"更新数据源设置: source={settings.source}, git_repo={settings.git_repo}")
        
        # 验证Git仓库地址
        if settings.source == 'git' and not settings.git_repo:
            raise HTTPException(status_code=400, detail="选择Git数据源时必须提供仓库地址")
        
        # 更新设置
        updated_settings = marketplace_service.update_source_settings(
            source=settings.source,
            git_repo=settings.git_repo
        )
        
        # 刷新数据
        marketplace_service.get_marketplace_data(force_refresh=True)
        
        logger.info(f"数据源设置已更新: {updated_settings}")
        return updated_settings
    except ValueError as e:
        logger.exception(f"更新数据源设置失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"更新数据源设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新数据源设置失败: {str(e)}") 