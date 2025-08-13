#!/usr/bin/env python3
"""
安全工具类 - 提供安全的错误处理和信息过滤功能
"""

import logging
import traceback
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from src.lat_lab.core.config import settings

logger = logging.getLogger("lat_lab.security")

class SecurityError:
    """安全错误处理类"""
    
    # 预定义的安全错误消息
    GENERIC_ERROR = "操作失败，请稍后重试"
    DATABASE_ERROR = "数据库操作失败"
    FILE_ERROR = "文件操作失败"
    PLUGIN_ERROR = "插件运行失败"
    NETWORK_ERROR = "网络请求失败"
    VALIDATION_ERROR = "数据验证失败"
    PERMISSION_ERROR = "权限不足"
    NOT_FOUND_ERROR = "请求的资源不存在"
    RATE_LIMIT_ERROR = "请求过于频繁，请稍后重试"
    
    @staticmethod
    def log_and_raise_safe_error(
        error: Exception,
        user_message: str = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        context: Dict[str, Any] = None
    ) -> None:
        """
        记录详细错误信息到日志，但只向用户返回安全的错误消息
        
        Args:
            error: 原始异常
            user_message: 显示给用户的安全消息
            status_code: HTTP状态码
            context: 额外的上下文信息用于日志记录
        """
        # 记录详细的错误信息到日志
        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "status_code": status_code,
        }
        
        if context:
            error_context.update(context)
        
        # 在开发环境记录堆栈跟踪
        if settings.DEBUG:
            logger.error(
                f"错误详情: {error_context}",
                exc_info=True
            )
        else:
            logger.error(f"操作失败: {error_context}")
        
        # 确定向用户显示的消息
        safe_message = user_message or SecurityError.GENERIC_ERROR
        
        # 在开发环境可以显示更多信息
        if settings.DEBUG and not user_message:
            safe_message = f"{SecurityError.GENERIC_ERROR}: {str(error)}"
        
        raise HTTPException(
            status_code=status_code,
            detail=safe_message
        )
    
    @staticmethod
    def log_error_safe(
        error: Exception,
        operation: str = "未知操作",
        context: Dict[str, Any] = None
    ) -> None:
        """
        安全地记录错误信息到日志，不暴露敏感信息
        
        Args:
            error: 异常对象
            operation: 操作描述
            context: 额外上下文信息
        """
        error_info = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error)[:200],  # 限制错误消息长度
        }
        
        if context:
            # 过滤敏感信息
            safe_context = SecurityError._filter_sensitive_info(context)
            error_info.update(safe_context)
        
        if settings.DEBUG:
            logger.error(f"{operation}失败: {error_info}", exc_info=True)
        else:
            logger.error(f"{operation}失败: {error_info}")
    
    @staticmethod
    def _filter_sensitive_info(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        过滤敏感信息，如密码、token等
        
        Args:
            data: 原始数据字典
            
        Returns:
            过滤后的安全数据字典
        """
        if not isinstance(data, dict):
            return {}
        
        sensitive_keys = {
            'password', 'pwd', 'passwd', 'secret', 'token', 'key', 
            'api_key', 'access_token', 'refresh_token', 'auth',
            'authorization', 'credential', 'private'
        }
        
        filtered_data = {}
        for key, value in data.items():
            if isinstance(key, str) and any(sensitive in key.lower() for sensitive in sensitive_keys):
                filtered_data[key] = "[已过滤]"
            elif isinstance(value, dict):
                filtered_data[key] = SecurityError._filter_sensitive_info(value)
            elif isinstance(value, str) and len(value) > 100:
                # 截断过长的字符串
                filtered_data[key] = value[:100] + "...[已截断]"
            else:
                filtered_data[key] = value
        
        return filtered_data
    
    @staticmethod
    def create_safe_http_exception(
        status_code: int,
        error_type: str = "generic",
        custom_message: str = None,
        context: Dict[str, Any] = None
    ) -> HTTPException:
        """
        创建安全的HTTP异常
        
        Args:
            status_code: HTTP状态码
            error_type: 错误类型
            custom_message: 自定义消息
            context: 上下文信息
            
        Returns:
            HTTPException实例
        """
        # 预定义错误消息映射
        error_messages = {
            "database": SecurityError.DATABASE_ERROR,
            "file": SecurityError.FILE_ERROR,
            "plugin": SecurityError.PLUGIN_ERROR,
            "network": SecurityError.NETWORK_ERROR,
            "validation": SecurityError.VALIDATION_ERROR,
            "permission": SecurityError.PERMISSION_ERROR,
            "not_found": SecurityError.NOT_FOUND_ERROR,
            "rate_limit": SecurityError.RATE_LIMIT_ERROR,
            "generic": SecurityError.GENERIC_ERROR
        }
        
        user_message = custom_message or error_messages.get(error_type, SecurityError.GENERIC_ERROR)
        
        # 记录错误上下文
        if context:
            SecurityError.log_error_safe(
                Exception(f"{error_type}错误"),
                f"HTTP异常 - {status_code}",
                context
            )
        
        return HTTPException(
            status_code=status_code,
            detail=user_message
        )


def safe_error_handler(
    error_type: str = "generic",
    custom_message: str = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
):
    """
    装饰器：为函数提供安全的错误处理
    
    Args:
        error_type: 错误类型
        custom_message: 自定义用户消息
        status_code: HTTP状态码
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                # 重新抛出HTTP异常
                raise
            except Exception as e:
                # 捕获所有其他异常并安全处理
                SecurityError.log_and_raise_safe_error(
                    error=e,
                    user_message=custom_message,
                    status_code=status_code,
                    context={
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()) if kwargs else []
                    }
                )
        
        # 保持装饰器的async特性
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except HTTPException:
                    raise
                except Exception as e:
                    SecurityError.log_and_raise_safe_error(
                        error=e,
                        user_message=custom_message,
                        status_code=status_code,
                        context={
                            "function": func.__name__,
                            "args_count": len(args),
                            "kwargs_keys": list(kwargs.keys()) if kwargs else []
                        }
                    )
            return async_wrapper
        else:
            return wrapper
    
    return decorator


# 常用的错误处理装饰器
database_safe = lambda func: safe_error_handler("database", SecurityError.DATABASE_ERROR)(func)
file_safe = lambda func: safe_error_handler("file", SecurityError.FILE_ERROR)(func)
plugin_safe = lambda func: safe_error_handler("plugin", SecurityError.PLUGIN_ERROR)(func)
network_safe = lambda func: safe_error_handler("network", SecurityError.NETWORK_ERROR)(func)


def secure_filename(filename):
    """安全地验证文件名，防止路径遍历攻击
    
    Args:
        filename (str): 要验证的文件名
        
    Returns:
        str: 安全的文件名（移除路径分隔符和特殊字符）
    """
    import os
    import re
    
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