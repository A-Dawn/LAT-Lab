-- LAT-Lab博客系统 - 添加管理员用户SQL脚本
-- 使用方法: 连接到SQLite数据库后执行此脚本: sqlite3 blog.db < add_admin.sql

-- 添加管理员用户
-- 默认用户名: admin
-- 默认密码: admin123
-- 密码哈希使用bcrypt算法生成，与系统保持一致
-- 提示: 这是一个示例密码哈希，实际部署时请立即修改密码

-- 检查数据库结构
PRAGMA table_info(users);

-- 插入管理员用户
INSERT INTO users (
    username, 
    email, 
    hashed_password, 
    role, 
    is_verified,
    created_at,
    updated_at
) SELECT 
    'admin', 
    'admin@latlab.example.com', 
    -- bcrypt算法加密的"admin123"密码
    '$2b$12$TmO/X.Y/FMJZmNAD/bcTuumgGPSmLXZQZ6bcv5oSzXFShYZgkbC4a', 
    'admin', 
    1,
    datetime('now'),
    datetime('now')
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username = 'admin' OR email = 'admin@latlab.example.com'
);

-- 显示插入结果
SELECT 'Admin user added successfully!' AS result 
WHERE changes() > 0
UNION ALL
SELECT 'Admin user already exists!' AS result
WHERE changes() = 0;

-- 显示管理员列表
SELECT id, username, email, role, is_verified FROM users WHERE role = 'admin'; 