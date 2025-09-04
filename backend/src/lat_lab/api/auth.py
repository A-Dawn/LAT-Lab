from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from src.lat_lab.core.deps import get_db, get_current_user, get_current_admin_user
from src.lat_lab.core.security import create_access_token
from src.lat_lab.core.rate_limiter import create_rate_limit_dependency
from src.lat_lab.core.config import settings
from src.lat_lab.schemas.user import Token, UserCreate, UserOut, EmailVerification
from src.lat_lab.crud.user import authenticate_user, create_user, get_user_by_email, get_user_by_username, verify_email, regenerate_verification_token
from src.lat_lab.models.user import RoleEnum, User as UserModel
from src.lat_lab.core.email import send_verification_email, generate_verification_token
from src.lat_lab.utils.username_validator import validate_username
import logging

router = APIRouter(prefix="/auth", tags=["authentication"])

logger = logging.getLogger(__name__)

# 创建速率限制依赖
login_rate_limit = create_rate_limit_dependency(
    "auth_login", 
    settings.RATE_LIMIT_LOGIN_REQUESTS, 
    settings.RATE_LIMIT_LOGIN_WINDOW
)

register_rate_limit = create_rate_limit_dependency(
    "auth_register", 
    settings.RATE_LIMIT_LOGIN_REQUESTS,  
    settings.RATE_LIMIT_LOGIN_WINDOW
)

resend_verification_rate_limit = create_rate_limit_dependency(
    "auth_resend_verification", 
    settings.RATE_LIMIT_RESEND_VERIFICATION_REQUESTS,  
    settings.RATE_LIMIT_RESEND_VERIFICATION_WINDOW
)

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(login_rate_limit)
):
    """
    用户登录接口，支持邮箱或用户名登录
    
    使用邮箱作为JWT token的subject，确保token的稳定性
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱/用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 使用邮箱作为token的subject，确保token的稳定性
    # 即使用户修改用户名，token仍然有效
    access_token = create_access_token(subject=user.email)
    
    # 在响应中添加验证状态信息
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "is_verified": user.is_verified,
        "email": user.email,
        "username": user.username
    }

@router.post("/register", response_model=UserOut)
def register(
    user: UserCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(register_rate_limit)
):
    # 验证用户名是否符合规范
    is_valid, error_message = validate_username(user.username)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # 统一错误提示，避免基于差异的账号枚举
    username_exists = get_user_by_username(db, user.username) is not None
    email_exists = get_user_by_email(db, user.email) is not None
    if username_exists or email_exists:
        raise HTTPException(status_code=400, detail="注册信息无效或已存在")
    
    # First user is automatically an admin
    is_first_user = db.query(UserModel).count() == 0
    role = RoleEnum.admin if is_first_user else RoleEnum.user
    
    # 创建用户
    db_user = create_user(db, user, role=role)
    
    # 如果不是管理员，发送验证邮件
    if not is_first_user:
        # 使用后台任务发送邮件，避免阻塞用户注册流程
        background_tasks.add_task(
            send_verification_email,
            email=db_user.email,
            username=db_user.username,
            token=db_user.verification_token
        )
        logger.info(f"验证邮件已加入后台任务队列，用户ID: {db_user.id}, 邮箱: {db_user.email}")
    
    return db_user

@router.post("/verify-email", response_model=UserOut)
def verify_user_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
):
    """验证用户邮箱"""
    logger.info(f"收到验证请求，令牌: {verification_data.token[:10]}...")
    
    user = verify_email(db, verification_data.token)
    if not user:
        logger.warning(f"验证失败，无效或已过期的令牌: {verification_data.token[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效或已过期的验证链接"
        )
    
    logger.info(f"邮箱验证成功，用户: {user.username}, ID: {user.id}")
    return user

@router.post("/resend-verification", response_model=dict)
def resend_verification_email(
    background_tasks: BackgroundTasks,
    email: str,
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(resend_verification_rate_limit)
):
    """重新发送验证邮件 - 无需用户认证"""
    # 通过邮箱查找用户
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该邮箱对应的用户"
        )
    
    # 检查用户是否已验证
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您的邮箱已验证"
        )
    
    # 重新生成验证令牌
    user = regenerate_verification_token(db, user.id)
    
    # 发送验证邮件
    background_tasks.add_task(
        send_verification_email,
        email=user.email,
        username=user.username,
        token=user.verification_token
    )
    
    return {"message": "验证邮件已重新发送，请稍等片刻并查收"}

@router.get("/me", response_model=UserOut)
def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user

@router.post("/test-email", response_model=dict)
def test_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)  # 只有管理员可以使用此功能
):
    """测试邮件发送功能（仅管理员可用）"""
    # 生成测试令牌
    test_token = "test_" + generate_verification_token(32)
    
    # 尝试发送测试邮件
    success = send_verification_email(
        email=email,
        username=current_user.username,
        token=test_token
    )
    
    if success:
        return {"status": "success", "message": f"测试邮件已成功发送至 {email}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送测试邮件失败，请检查SMTP配置和日志"
        ) 