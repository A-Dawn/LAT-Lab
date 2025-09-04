"""
管理员专用API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Dict, Any
import json
from datetime import datetime

from src.lat_lab.core.deps import get_db, get_current_admin_user
from src.lat_lab.core.rate_limiter import rate_limiter
from src.lat_lab.models.user import User
from src.lat_lab.models.system import SystemConfig

router = APIRouter(prefix="/admin", tags=["admin"])

# 创建一个公开的API路由，用于获取系统配置
public_router = APIRouter(prefix="/public", tags=["public"])

@public_router.get("/about-section", response_model=Dict[str, Any])
def get_public_about_section(db: Session = Depends(get_db)):
    """获取关于博主区域的配置内容（公开API，不需要权限）"""
    try:
        # 查询系统配置中的关于博主信息
        config = db.query(SystemConfig).filter(SystemConfig.key == "about_section").first()
        
        if config:
            about_data = json.loads(config.value)
            # 数据兼容性处理：如果存在旧的socialLinks字段，转换为social_links
            if "socialLinks" in about_data and "social_links" not in about_data:
                about_data["social_links"] = about_data["socialLinks"]
                del about_data["socialLinks"]
        else:
            # 默认配置 - 统一使用下划线命名
            about_data = {
                "title": "关于博主",
                "description": "欢迎来到我的博客！这里记录了我的学习、思考和分享。",
                "social_links": [
                    {"name": "GitHub", "url": "#", "icon": "github"},
                    {"name": "Twitter", "url": "#", "icon": "twitter"},
                    {"name": "知乎", "url": "#", "icon": "zhihu"}
                ]
            }
        
        return {
            "success": True,
            "data": about_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取配置失败"
        )

@public_router.get("/blog-owner", response_model=Dict[str, Any])
def get_public_blog_owner(db: Session = Depends(get_db)):
    """获取博主信息（第一个用户，公开API，不需要权限）"""
    try:
        # 获取第一个用户作为博主
        first_user = db.query(User).order_by(User.id).first()
        
        if first_user:
            return {
                "success": True,
                "data": {
                    "id": first_user.id,
                    "username": first_user.username,
                    "avatar": first_user.avatar,
                    "bio": first_user.bio
                }
            }
        else:
            # 如果没有用户，返回默认信息
            return {
                "success": True,
                "data": {
                    "id": None,
                    "username": "LAT-Lab",
                    "avatar": None,
                    "bio": None
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取博主信息失败"
        )


@router.get("/rate-limit/stats", response_model=Dict[str, Any])
def get_rate_limit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取速率限制统计信息（仅管理员）"""
    try:
        stats = rate_limiter.get_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取速率限制统计失败"
        )


@router.post("/rate-limit/clear", response_model=Dict[str, Any])
def clear_rate_limit_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """清空速率限制记录（仅管理员）"""
    try:
        # 清空记录
        rate_limiter._requests.clear()
        rate_limiter._banned_ips.clear()
        
        return {
            "success": True,
            "message": "速率限制记录已清空"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清空速率限制记录失败"
        )


@router.get("/about-section", response_model=Dict[str, Any])
def get_about_section(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取关于博主区域的配置内容"""
    try:
        # 查询系统配置中的关于博主信息
        config = db.query(SystemConfig).filter(SystemConfig.key == "about_section").first()
        
        if config:
            about_data = json.loads(config.value)
            # 数据兼容性处理：如果存在旧的socialLinks字段，转换为social_links
            if "socialLinks" in about_data and "social_links" not in about_data:
                about_data["social_links"] = about_data["socialLinks"]
                del about_data["socialLinks"]
        else:
            # 默认配置 - 统一使用下划线命名
            about_data = {
                "title": "关于博主",
                "description": "欢迎来到我的博客！这里记录了我的学习、思考和分享。",
                "social_links": [
                    {"name": "GitHub", "url": "#", "icon": "github"},
                    {"name": "Twitter", "url": "#", "icon": "twitter"},
                    {"name": "知乎", "url": "#", "icon": "zhihu"}
                ]
            }
        
        return {
            "success": True,
            "data": about_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取配置失败"
        )


@router.put("/about-section", response_model=Dict[str, Any])
def update_about_section(
    about_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新关于博主区域的配置内容"""
    try:
        # 数据兼容性处理：支持两种字段名格式，但统一存储为social_links
        if "socialLinks" in about_data and "social_links" not in about_data:
            about_data["social_links"] = about_data["socialLinks"]
            del about_data["socialLinks"]
        
        # 验证数据格式 - 更新为使用下划线命名
        required_fields = ["title", "description", "social_links"]
        for field in required_fields:
            if field not in about_data:
                raise HTTPException(status_code=400, detail=f"缺少必需字段: {field}")
        
        # 查询是否存在配置
        config = db.query(SystemConfig).filter(SystemConfig.key == "about_section").first()
        
        if config:
            # 更新现有配置
            config.value = json.dumps(about_data, ensure_ascii=False)
            config.updated_at = datetime.utcnow()
        else:
            # 创建新配置
            config = SystemConfig(
                key="about_section",
                value=json.dumps(about_data, ensure_ascii=False),
                description="关于博主区域配置"
            )
            db.add(config)
        
        db.commit()
        
        return {
            "success": True,
            "message": "更新成功",
            "data": about_data
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新配置失败"
        ) 


@router.get("/dev-tools-config", response_model=Dict[str, Any])
def get_dev_tools_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取开发工具配置"""
    try:
        # 查询系统配置中的开发工具信息
        config = db.query(SystemConfig).filter(SystemConfig.key == "dev_tools_config").first()
        
        if config:
            dev_tools_data = json.loads(config.value)
        else:
            # 默认配置
            dev_tools_data = {
                "styles": [],
                "texts": [],
                "layouts": [],
                "page_data": {},
                "current_page": "current"
            }
        
        return {
            "success": True,
            "data": dev_tools_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取开发工具配置失败"
        )


@router.put("/dev-tools-config", response_model=Dict[str, Any])
def update_dev_tools_config(
    config_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新开发工具配置"""
    try:
        # 验证数据格式
        required_fields = ["styles", "texts", "layouts"]
        for field in required_fields:
            if field not in config_data:
                config_data[field] = []
        
        # 添加时间戳
        config_data["last_updated"] = datetime.utcnow().isoformat()
        
        # 查询是否存在配置
        config = db.query(SystemConfig).filter(SystemConfig.key == "dev_tools_config").first()
        
        if config:
            # 更新现有配置
            config.value = json.dumps(config_data, ensure_ascii=False)
            config.updated_at = datetime.utcnow()
        else:
            # 创建新配置
            config = SystemConfig(
                key="dev_tools_config",
                value=json.dumps(config_data, ensure_ascii=False),
                description="开发工具配置"
            )
            db.add(config)
        
        db.commit()
        
        return {
            "success": True,
            "message": "开发工具配置更新成功",
            "data": config_data
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新开发工具配置失败"
        )


@router.delete("/dev-tools-config", response_model=Dict[str, Any])
def clear_dev_tools_config(
    page: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """清除开发工具配置"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.key == "dev_tools_config").first()
        
        if config:
            if page:
                # 清除特定页面的配置
                dev_tools_data = json.loads(config.value)
                if "page_data" in dev_tools_data and page in dev_tools_data["page_data"]:
                    del dev_tools_data["page_data"][page]
                    config.value = json.dumps(dev_tools_data, ensure_ascii=False)
                    config.updated_at = datetime.utcnow()
                    db.commit()
                    message = f"页面 {page} 的配置已清除"
                else:
                    message = f"页面 {page} 的配置不存在"
            else:
                # 清除所有配置
                db.delete(config)
                db.commit()
                message = "所有开发工具配置已清除"
        else:
            message = "配置不存在"
        
        return {
            "success": True,
            "message": message
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清除开发工具配置失败"
        )