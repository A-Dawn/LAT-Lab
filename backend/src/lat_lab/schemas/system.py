"""
系统配置相关的数据验证模式
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Optional, Any
from datetime import datetime


class SocialLinkSchema(BaseModel):
    """社交链接数据模式"""
    name: str = Field(..., min_length=1, max_length=50, description="平台名称")
    url: HttpUrl = Field(..., description="链接地址")
    icon: Optional[str] = Field(None, max_length=50, description="图标名称")


class AboutSectionSchema(BaseModel):
    """关于博主配置数据模式"""
    title: str = Field(..., min_length=1, max_length=50, description="标题")
    description: str = Field("", max_length=500, description="描述")
    social_links: List[SocialLinkSchema] = Field(default_factory=list, description="社交链接")

    @validator('title', 'description')
    def validate_text_fields(cls, v):
        """验证文本字段，防止XSS攻击"""
        if v:
            # 移除潜在的HTML标签和脚本
            import re
            v = re.sub(r'<[^>]*>', '', v)
            v = re.sub(r'javascript:', '', v, flags=re.IGNORECASE)
        return v.strip()

    @validator('social_links')
    def validate_social_links(cls, v):
        """验证社交链接数量"""
        if len(v) > 10:
            raise ValueError('社交链接数量不能超过10个')
        return v


class SystemConfigCreate(BaseModel):
    """系统配置创建模式"""
    key: str = Field(..., min_length=1, max_length=64, description="配置键")
    value: Any = Field(..., description="配置值")
    description: Optional[str] = Field(None, max_length=255, description="配置描述")


class SystemConfigUpdate(BaseModel):
    """系统配置更新模式"""
    value: Any = Field(..., description="配置值")
    description: Optional[str] = Field(None, max_length=255, description="配置描述")


class SystemConfigResponse(BaseModel):
    """系统配置响应模式"""
    id: int
    key: str
    value: Any
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 