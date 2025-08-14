import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from src.lat_lab.core.config import settings
import secrets
import string
from datetime import datetime, timedelta

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_verification_token(length=64):
    """生成随机验证令牌"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def is_token_expired(token_created_at):
    """检查令牌是否过期"""
    if not token_created_at:
        return True
    
    expiry_time = token_created_at + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
    return datetime.now() > expiry_time

def send_verification_email(email, username, token):
    """发送验证邮件"""
    try:
        # 创建邮件内容
        verification_link = f"{settings.BASE_URL}/verify-email?token={token}"
        
        message = MIMEMultipart()
        message["From"] = settings.MAIL_FROM
        message["To"] = email
        message["Subject"] = "验证您的LAT-Lab账号"
        
        # 邮件HTML内容
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4c84ff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 10px 20px; background-color: #4c84ff; color: white; 
                          text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>LAT-Lab 邮箱验证</h1>
                </div>
                <div class="content">
                    <p>尊敬的 {username}，</p>
                    <p>感谢您注册LAT-Lab！请点击下面的按钮验证您的邮箱地址：</p>
                    <p style="text-align: center;">
                        <a href="{verification_link}" class="button">验证邮箱</a>
                    </p>
                    <p>或者，您可以复制以下链接到浏览器地址栏：</p>
                    <p>{verification_link}</p>
                    <p>此链接将在24小时后过期。</p>
                    <p>如果您没有注册LAT-Lab账号，请忽略此邮件。</p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复。</p>
                    <p>&copy; {datetime.now().year} LAT-Lab. 保留所有权利。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 添加HTML内容
        message.attach(MIMEText(html, "html"))
        
        # 连接SMTP服务器并发送
        logger.info(f"尝试连接SMTP服务器: {settings.MAIL_SERVER}:{settings.MAIL_PORT}")
        
        # 根据邮箱类型选择合适的连接方式
        mail_domain = settings.MAIL_USERNAME.split('@')[-1].lower()
        
        if mail_domain == '163.com':
            # 163邮箱推荐使用25端口
            logger.info("检测到163邮箱，使用标准SMTP连接")
            server = smtplib.SMTP(settings.MAIL_SERVER, 25)
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            
        elif mail_domain in ['gmail.com', 'googlemail.com']:
            # Gmail推荐使用587端口+TLS
            logger.info("检测到Gmail邮箱，使用TLS连接")
            server = smtplib.SMTP(settings.MAIL_SERVER, 587)
            server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            
        else:
            # 其他邮箱尝试标准连接方式
            logger.info(f"使用配置的连接方式: {settings.MAIL_SERVER}:{settings.MAIL_PORT}")
            server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT)
            
            if settings.MAIL_TLS:
                logger.info("启用TLS加密")
                server.starttls()
                
            logger.info(f"尝试登录邮箱: {settings.MAIL_USERNAME}")
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        
        # 发送邮件
        logger.info(f"发送邮件到: {email}")
        server.send_message(message)
        server.quit()
        
        logger.info(f"验证邮件已成功发送至 {email}")
        return True
            
    except Exception as e:
        logger.error(f"发送验证邮件失败: {str(e)}", exc_info=True)
        
        # 尝试使用SSL连接作为备选方案
        try:
            logger.info("尝试使用SSL连接作为备选方案")
            server_ssl = smtplib.SMTP_SSL(settings.MAIL_SERVER, 465)  # 使用465端口的SSL连接
            server_ssl.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            
            server_ssl.send_message(message)
            server_ssl.quit()
            
            logger.info(f"使用SSL连接成功发送验证邮件至 {email}")
            return True
        except Exception as ssl_error:
            logger.error(f"SSL连接发送邮件也失败: {str(ssl_error)}", exc_info=True)
            return False 