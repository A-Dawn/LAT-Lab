# LAT-Lab 数据库脚本说明

本目录包含LAT-Lab项目的数据库初始化和管理脚本。

## 📁 脚本文件说明

### Docker部署专用脚本
- **`init-db-mysql.sql`** - MySQL数据库初始化SQL脚本，用于Docker容器首次启动
- **`init-db-mysql.py`** - MySQL数据库初始化Python脚本，用于Docker部署后的数据初始化

### 传统安装专用脚本
- **`init-db-sqlite.py`** - SQLite数据库初始化脚本，用于传统安装方式
- **`run_migrations.py`** - 数据库迁移脚本，适用于所有数据库类型

### 通用脚本
- **`init_db.py`** - 通用数据库初始化脚本（已废弃，建议使用专用脚本）
- **`create_user.py`** - 用户创建脚本
- **`setup_env.py`** - 环境设置脚本

## 🚀 使用方法

### Docker部署
1. MySQL容器启动时会自动执行 `init-db-mysql.sql`
2. 容器启动后，可手动运行 `init-db-mysql.py` 初始化示例数据

### 传统安装
1. 运行 `setup_env.py` 设置环境
2. 运行 `init-db-sqlite.py` 初始化SQLite数据库

## ⚠️ 注意事项

- **不要混用脚本**：Docker部署使用MySQL脚本，传统安装使用SQLite脚本
- **环境变量**：确保使用正确的环境配置文件（`docker.env.example` 或 `env.traditional.example`）
- **数据库类型**：脚本会根据 `DB_TYPE` 环境变量自动选择正确的数据库类型

## 🔧 故障排除

如果遇到数据库初始化问题：
1. 检查环境变量配置
2. 确认数据库服务是否正常运行
3. 查看日志输出获取详细错误信息 