"""
速率限制器模块
使用内存存储实现基于IP的速率限制
"""

import time
import logging
from typing import Dict, Tuple, Optional
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from functools import wraps

logger = logging.getLogger(__name__)


class RateLimiter:
    """基于滑动窗口的速率限制器"""
    
    def __init__(self):
        # 存储每个IP的请求记录: {ip: {endpoint: deque(timestamps)}}
        self._requests: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
        # 存储被封禁的IP: {ip: ban_until_timestamp}
        self._banned_ips: Dict[str, float] = {}
        # 清理间隔（秒）
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5分钟清理一次
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP地址"""
        # 从代理头获取真实IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 取第一个
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # 使用客户端IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _cleanup_old_requests(self, current_time: float):
        """清理过期的请求记录"""
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        logger.debug("开始清理过期的速率限制记录")
        
        # 清理请求记录（保留最近1小时的记录）
        cutoff_time = current_time - 3600
        for ip in list(self._requests.keys()):
            for endpoint in list(self._requests[ip].keys()):
                # 移除过期的时间戳
                while (self._requests[ip][endpoint] and 
                       self._requests[ip][endpoint][0] < cutoff_time):
                    self._requests[ip][endpoint].popleft()
                
                # 如果队列为空，删除记录
                if not self._requests[ip][endpoint]:
                    del self._requests[ip][endpoint]
            
            if not self._requests[ip]:
                del self._requests[ip]
        
        # 清理过期的封禁记录
        expired_bans = [ip for ip, ban_time in self._banned_ips.items() 
                       if current_time > ban_time]
        for ip in expired_bans:
            del self._banned_ips[ip]
            logger.info(f"IP {ip} 封禁已解除")
        
        self._last_cleanup = current_time
        logger.debug(f"清理完成，当前记录数: {len(self._requests)}")
    
    def is_allowed(self, request: Request, endpoint: str, max_requests: int, 
                   window_seconds: int) -> Tuple[bool, Optional[int]]:
        current_time = time.time()
        ip = self._get_client_ip(request)
        
        # 定期清理过期记录
        self._cleanup_old_requests(current_time)
        
        # 检查IP是否被封禁
        if ip in self._banned_ips:
            if current_time < self._banned_ips[ip]:
                retry_after = int(self._banned_ips[ip] - current_time)
                logger.warning(f"封禁IP {ip} 尝试访问 {endpoint}")
                return False, retry_after
            else:
                # 封禁已过期，移除记录
                del self._banned_ips[ip]
        
        # 获取IP在端点的请求记录
        request_times = self._requests[ip][endpoint]
        
        # 移除窗口外的请求
        window_start = current_time - window_seconds
        while request_times and request_times[0] < window_start:
            request_times.popleft()
        
        # 检查是否超过限制
        if len(request_times) >= max_requests:
            # 计算等待时间
            oldest_request = request_times[0]
            retry_after = int(oldest_request + window_seconds - current_time) + 1
            
            logger.warning(f"IP {ip} 在端点 {endpoint} 达到速率限制: "
                         f"{len(request_times)}/{max_requests} 请求")
            
            # 如果频繁违规，临时封禁IP（
            violation_count = len([t for t in request_times if t > current_time - 60])
            if violation_count >= max_requests:
                ban_duration = min(600, violation_count * 60)  # 最多封禁10分钟
                self._banned_ips[ip] = current_time + ban_duration
                logger.warning(f"IP {ip} 被临时封禁 {ban_duration} 秒")
                return False, ban_duration
            
            return False, retry_after
        
        # 记录当前请求
        request_times.append(current_time)
        
        return True, None
    
    def get_stats(self) -> Dict:
        """获取速率限制统计信息"""
        current_time = time.time()
        return {
            "tracked_ips": len(self._requests),
            "banned_ips": len(self._banned_ips),
            "active_bans": [
                {
                    "ip": ip, 
                    "remaining_seconds": int(ban_time - current_time)
                }
                for ip, ban_time in self._banned_ips.items()
                if ban_time > current_time
            ]
        }


rate_limiter = RateLimiter()


def rate_limit(endpoint: str, max_requests: int, window_seconds: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中找到Request
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # 如果没有Request，检查kwargs
                request = kwargs.get('request')
            
            if not request:
                logger.warning(f"无法获取Request，跳过速率限制检查: {endpoint}")
                return await func(*args, **kwargs)
            
            # 检查速率限制
            allowed, retry_after = rate_limiter.is_allowed(
                request, endpoint, max_requests, window_seconds
            )
            
            if not allowed:
                headers = {}
                if retry_after:
                    headers["Retry-After"] = str(retry_after)
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="请求过于频繁，请稍后重试",
                    headers=headers
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def create_rate_limit_dependency(endpoint: str, max_requests: int, window_seconds: int):
    def rate_limit_dependency(request: Request):
        allowed, retry_after = rate_limiter.is_allowed(
            request, endpoint, max_requests, window_seconds
        )
        
        if not allowed:
            headers = {}
            if retry_after:
                headers["Retry-After"] = str(retry_after)
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后重试",
                headers=headers
            )
        
        return True
    
    return rate_limit_dependency 