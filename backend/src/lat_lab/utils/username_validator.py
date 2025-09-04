"""
用户名验证工具
用于验证用户名是否符合规范，并阻止使用保留词汇
"""

# 禁止使用的用户名列表
RESERVED_USERNAMES = {
    # 管理类词汇
    'admin', 'administrator', 'root', 'superuser', 'super', 'master', 'owner', 'manager',
    'moderator', 'mod', 'operator', 'op', 'staff', 'support', 'help', 'service',
    
    # 系统保留词汇
    'system', 'sys', 'server', 'host', 'localhost', 'local', 'test', 'testing', 'demo',
    'guest', 'anonymous', 'unknown', 'null', 'undefined', 'none', 'nobody',
    'api', 'app', 'web', 'www', 'site', 'website', 'portal', 'platform',
    
    # 技术性词汇
    'user', 'users', 'account', 'accounts', 'login', 'logout', 'register', 'signup',
    'signin', 'auth', 'authentication', 'authorization', 'session', 'token',
    'password', 'passwd', 'pwd', 'secret', 'private', 'public', 'secure',
    'database', 'db', 'data', 'config', 'configuration', 'settings', 'preferences',
    'profile', 'avatar', 'image', 'file', 'upload', 'download', 'media',
    
    # 常见功能词汇
    'home', 'index', 'main', 'default', 'start', 'welcome', 'about', 'contact',
    'help', 'faq', 'support', 'feedback', 'report', 'bug', 'error', '404', '500',
    'search', 'find', 'browse', 'view', 'edit', 'create', 'delete', 'remove',
    'add', 'new', 'old', 'current', 'previous', 'next', 'back', 'forward',
    
    # 严重不雅词汇（中文）
    '傻逼', '狗屎', '混蛋', '王八蛋', '贱人', '婊子', '妓女', '嫖客', '强奸', '轮奸',
    '鸡巴', '屌', '逼', '操', '干', '日', '肏', '屄', '屌丝', '屌毛',
    
    # 严重不雅词汇（英文）
    'fuck', 'shit', 'bitch', 'whore', 'slut', 'cunt', 'dick', 'cock', 'pussy',
    'asshole', 'bastard', 'motherfucker', 'fucker', 'fucking', 'shitty',
    'nigger', 'nigga', 'faggot', 'dyke', 'queer', 'retard', 'idiot', 'moron',
    
    # 其他常见禁止词汇
    'hack', 'hacker', 'crack', 'cracker', 'virus', 'malware', 'spam', 'bot',
    'robot', 'automation', 'script', 'program', 'code', 'developer', 'dev',
    'admin123', 'password123', '123456', 'qwerty', 'abc123', 'test123',
}

def is_username_reserved(username: str) -> bool:
    """
    检查用户名是否为保留词汇
    
    Args:
        username: 要检查的用户名
        
    Returns:
        bool: 如果是保留词汇返回True，否则返回False
    """
    if not username:
        return False
    
    # 转换为小写进行比较
    username_lower = username.lower().strip()
    
    # 检查是否在保留列表中（完全匹配）
    if username_lower in RESERVED_USERNAMES:
        return True
    
    return False

def validate_username(username: str, allow_reserved: bool = False) -> tuple[bool, str]:
    """
    验证用户名是否符合规范
    
    Args:
        username: 要验证的用户名
        allow_reserved: 是否允许使用保留词汇（管理员特权）
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if not username:
        return False, "用户名不能为空"
    
    username = username.strip()
    
    # 检查长度
    if len(username) < 3:
        return False, "用户名长度不能少于3个字符"
    
    if len(username) > 32:
        return False, "用户名长度不能超过32个字符"
    
    # 检查是否为保留词汇（除非明确允许）
    if not allow_reserved and is_username_reserved(username):
        return False, "该用户名已被保留或禁止注册"
    
    # 检查格式（只允许字母、数字、下划线）
    if not username.replace("_", "").isalnum():
        return False, "用户名只能包含字母、数字和下划线"
    
    # 检查是否以数字开头
    if username[0].isdigit():
        return False, "用户名不能以数字开头"
    
    # 检查是否包含连续下划线
    if "__" in username:
        return False, "用户名不能包含连续的下划线"
    
    # 检查是否以下划线开头或结尾
    if username.startswith("_") or username.endswith("_"):
        return False, "用户名不能以下划线开头或结尾"
    
    return True, ""

def get_reserved_usernames() -> set:
    """
    获取保留用户名列表
    
    Returns:
        set: 保留用户名集合
    """
    return RESERVED_USERNAMES.copy() 