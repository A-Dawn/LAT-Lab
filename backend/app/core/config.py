import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "LAT-Lab博客系统API"
    VERSION: str = "0.1.0"
    
    # 数据库设置
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")  # "sqlite" 或 "mysql"
    MYSQL_USER: str = os.getenv("MYSQL_USER", "lat_lab_user")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "your_db_password")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_DB: str = os.getenv("MYSQL_DB", "lat_lab_db")
    
    # JWT设置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secure_random_string_replace_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1天
    
    # 插件设置
    PLUGIN_SANDBOX_ENABLED: bool = True  # 重新启用沙箱模式
    PLUGIN_TIMEOUT_SECONDS: int = 5
    PLUGIN_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "plugins")
    PLUGIN_EXAMPLES_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "plugin_examples")
    PLUGIN_MARKETPLACE_CONFIG: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "marketplace_config.json")

    # 邮件设置
    # 邮箱配置 - 请设置自己的邮箱服务
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.example.com") 
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 25))  
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "your-email@example.com")  
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "your-password")  
    MAIL_FROM: str = os.getenv("MAIL_FROM", "your-email@example.com")  
    
    # Outlook配置 - 示例
    # MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.office365.com")
    # MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    # MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "your-email@outlook.com")
    # MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "your-password")
    # MAIL_FROM: str = os.getenv("MAIL_FROM", "your-email@outlook.com")
    
    # Gmail配置 - 示例
    # MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    # MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    # MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
    # MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "your-app-password")
    # MAIL_FROM: str = os.getenv("MAIL_FROM", "your-email@gmail.com")
    
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    
    # 验证令牌设置
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24  # 验证令牌24小时过期
    
    # 网站基础URL
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:5173")

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.DB_TYPE == "sqlite":
            return "sqlite:///./blog.db"
        else:
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"

settings = Settings() 