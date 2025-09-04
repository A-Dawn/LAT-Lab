-- 数据库初始化脚本
-- 此脚本在MySQL容器首次启动时自动执行

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS `lat_lab_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE `lat_lab_db`;

-- 创建用户（如果不存在）
CREATE USER IF NOT EXISTS 'lat_lab_user'@'%' IDENTIFIED BY 'your_db_password';

-- 授予权限
GRANT ALL PRIVILEGES ON `lat_lab_db`.* TO 'lat_lab_user'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示创建结果
SELECT 'Database initialization completed successfully!' as status; 