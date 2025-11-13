from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
import bcrypt
from src.lat_lab.core.config import settings
import logging

logger = logging.getLogger(__name__)

# JWT设置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    直接使用 bcrypt 库验证密码，避免 passlib 的兼容性问题
    """
    try:
        # bcrypt 有 72 字节的密码长度限制
        if len(plain_password.encode('utf-8')) > 72:
            logger.warning("密码长度超过 72 字节，将被截断")
            plain_password = plain_password[:72]
        
        # 使用 bcrypt.checkpw 直接验证
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"密码验证异常: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    直接使用 bcrypt 库生成密码哈希，避免 passlib 的兼容性问题
    """
    # bcrypt 有 72 字节的密码长度限制
    if len(password.encode('utf-8')) > 72:
        logger.warning("密码长度超过 72 字节，将被截断")
        password = password[:72]
    
    # 使用 bcrypt.hashpw 直接生成哈希
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt 