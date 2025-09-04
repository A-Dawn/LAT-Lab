import os
import secrets
from typing import Optional, List
from pydantic_settings import BaseSettings
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent.parent.absolute()
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
PLUGIN_EXAMPLES_DIR = BASE_DIR / "plugin_examples"

class Settings(BaseSettings):
    PROJECT_NAME: str = "LAT-Lab博客系统API"
    VERSION: str = "0.3.1"
    
    # 基础配置
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库设置
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")  # "sqlite" 或 "mysql"
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "db")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_DB: str = os.getenv("MYSQL_DB", "blog_db")
    
    # JWT设置
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1天
    
    # 插件设置
    PLUGIN_SANDBOX_ENABLED: bool = True  # 沙箱模式
    PLUGIN_TIMEOUT_SECONDS: int = 5
    PLUGIN_DIR: Path = BASE_DIR / "plugins"
    PLUGIN_EXAMPLES_DIR: Path = PLUGIN_EXAMPLES_DIR
    PLUGIN_MARKETPLACE_CONFIG: Path = BASE_DIR / "marketplace_config.json"

    # 邮件设置
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.example.com") 
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 25))  
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "your-email@example.com")  
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "your-password")  
    MAIL_FROM: str = os.getenv("MAIL_FROM", "your-email@example.com")  
    MAIL_TLS: bool = os.getenv("MAIL_TLS", "true").lower() == "true"
    MAIL_SSL: bool = os.getenv("MAIL_SSL", "false").lower() == "true"
    
    # 验证令牌设置
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24  # 验证令牌24小时过期
    
    # 网站基础URL
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost")
    
    # CORS设置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 上传文件配置
    UPLOADS_DIR: Path = UPLOADS_DIR
    AVATARS_DIR: Path = UPLOADS_DIR / "avatars"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    # 速率限制配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_LOGIN_REQUESTS: int = 50   # 登录每分钟最多50次（从10次增加）
    RATE_LIMIT_LOGIN_WINDOW: int = 60     # 时间窗口60秒
    RATE_LIMIT_API_REQUESTS: int = 1000   # API每分钟最多1000次（从100次增加）
    RATE_LIMIT_API_WINDOW: int = 60       # 时间窗口60秒
    RATE_LIMIT_UPLOAD_REQUESTS: int = 50  # 上传每分钟最多50次（从10次增加）
    RATE_LIMIT_UPLOAD_WINDOW: int = 60    # 时间窗口60秒
    RATE_LIMIT_PLUGIN_REQUESTS: int = 100 # 插件运行每分钟最多100次（从20次增加）
    RATE_LIMIT_PLUGIN_WINDOW: int = 60    # 时间窗口60秒
    RATE_LIMIT_RESEND_VERIFICATION_REQUESTS: int = 1  # 验证邮件重发每180秒最多1次
    RATE_LIMIT_RESEND_VERIFICATION_WINDOW: int = 180  # 时间窗口180秒

    # 插件市场配置
    PLUGIN_MARKETPLACE_SOURCE: str = "local"  # local 或 git
    PLUGIN_MARKETPLACE_LOCAL_PATH: Path = PLUGIN_MARKETPLACE_CONFIG
    PLUGIN_MARKETPLACE_GIT_REPO: str = ""
    PLUGIN_MARKETPLACE_GIT_BRANCH: str = "main"
    PLUGIN_MARKETPLACE_GIT_PATH: str = "marketplace_config.json"
    PLUGIN_MARKETPLACE_GIT_TOKEN: str = ""
    PLUGIN_MARKETPLACE_CACHE_TTL: int = 3600  # 缓存时间，单位秒

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.DB_TYPE == "sqlite":
            return f"sqlite:///{DATA_DIR}/blog.db"
        else:
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

# 实例化设置
settings = Settings() 

# 确保必要的目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.AVATARS_DIR, exist_ok=True)
os.makedirs(settings.PLUGIN_EXAMPLES_DIR, exist_ok=True)
os.makedirs(settings.PLUGIN_DIR, exist_ok=True)

# 打印调试信息
import logging
logger = logging.getLogger(__name__)
logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"PLUGIN_MARKETPLACE_CONFIG: {settings.PLUGIN_MARKETPLACE_CONFIG}")
logger.info(f"配置文件是否存在: {os.path.exists(settings.PLUGIN_MARKETPLACE_CONFIG)}")

# 如果配置文件不存在，尝试使用替代路径
if not os.path.exists(settings.PLUGIN_MARKETPLACE_CONFIG):
    logger.warning(f"配置文件不存在: {settings.PLUGIN_MARKETPLACE_CONFIG}")
    
    # 尝试在不同位置查找配置文件
    possible_paths = [
        Path(os.getcwd()) / "marketplace_config.json",
        BASE_DIR / "data" / "marketplace_config.json",
        BASE_DIR / "src" / "lat_lab" / "marketplace_config.json"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"找到替代配置文件: {path}")
            settings.PLUGIN_MARKETPLACE_LOCAL_PATH = path
            break
    else:
        logger.warning("未找到有效的插件市场配置文件，请确保配置文件存在") 