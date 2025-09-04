# LAT-Lab Docker 部署指南

## 📋 概述

本文档详细说明如何使用 Docker 部署 LAT-Lab 项目。Docker 部署提供了环境一致性、快速部署和易于管理的优势。

## 🚀 快速开始

### 1. 环境要求

- Docker Desktop 4.0+ 或 Docker Engine 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 2. 一键部署

#### Linux/macOS
```bash
# 克隆项目
git clone <repository-url>
cd LAT-Lab

# 设置执行权限
chmod +x docker-deploy.sh

# 启动服务
./docker-deploy.sh start
```

#### Windows PowerShell
```powershell
# 克隆项目
git clone <repository-url>
cd LAT-Lab

# 启动服务
.\docker-deploy.ps1 start
```

#### 手动部署
```bash
# 复制环境配置文件
cp docker.env.example .env

# 编辑配置文件
nano .env

# 启动服务
docker-compose up -d

# 等待MySQL容器启动完成后，初始化示例数据（可选）
docker-compose exec backend python scripts/init-db-mysql.py
```

## ⚙️ 配置说明

### 环境变量配置

编辑 `.env` 文件，设置以下关键配置：

```bash
# 数据库配置
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_USER=lat_lab_user
MYSQL_PASSWORD=your_secure_user_password
MYSQL_DB=lat_lab_db

# JWT密钥 (至少32字符)
SECRET_KEY=your_very_long_and_secure_secret_key_here_minimum_32_chars

# 网站URL
BASE_URL=http://localhost

# 调试模式 (生产环境设为False)
DEBUG=False
```

### 端口配置

- **前端**: http://localhost (端口80)
- **后端API**: http://localhost:8000 (端口8000)
- **数据库**: localhost:3306 (端口3306)

## 🐳 服务架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Nginx)       │◄──►│   (FastAPI)     │◄──►│   (MySQL 8.0)   │
│   Port: 80      │    │   Port: 8000    │    │   Port: 3306    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🗄️ 数据库初始化

Docker部署使用MySQL数据库，初始化过程如下：

1. **自动初始化**: MySQL容器启动时自动执行 `init-db-mysql.sql` 创建数据库和用户
2. **手动初始化**: 容器启动后，可手动运行 `init-db-mysql.py` 创建示例数据
3. **数据持久化**: 数据库数据存储在Docker卷 `db_data` 中

## 📁 目录结构

```
LAT-Lab/
├── docker-compose.yml          # Docker Compose 配置
├── docker.env.example          # Docker 环境变量模板
├── .env                        # 环境变量配置 (需创建)
├── docker-deploy.sh            # Linux/macOS 部署脚本
├── docker-deploy.ps1           # Windows PowerShell 部署脚本
├── backend/
│   ├── Dockerfile              # 后端镜像构建文件
│   └── scripts/
│       ├── init-db-mysql.sql   # MySQL数据库初始化SQL脚本
│       └── init-db-mysql.py    # MySQL数据库初始化Python脚本
└── frontend/
    ├── Dockerfile              # 前端镜像构建文件
    └── nginx.conf              # Nginx 配置文件
```

## 🔧 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]
```

### 使用部署脚本

```bash
# 启动服务
./docker-deploy.sh start

# 停止服务
./docker-deploy.sh stop

# 重启服务
./docker-deploy.sh restart

# 查看日志
./docker-deploy.sh logs

# 查看状态
./docker-deploy.sh status

# 清理资源
./docker-deploy.sh clean
```

## 🚨 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
netstat -tulpn | grep :80
netstat -tulpn | grep :8000

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8080:80"      # 前端使用8080端口
  - "8001:8000"    # 后端使用8001端口
```

#### 2. 数据库连接失败
```bash
# 检查数据库容器状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 手动连接数据库
docker-compose exec db mysql -u root -p
```

#### 3. 前端无法访问后端API
```bash
# 检查后端服务状态
docker-compose ps backend

# 查看后端日志
docker-compose logs backend

# 测试API连接
curl http://localhost:8000/api/health
```

#### 4. 权限问题
```bash
# 修复文件权限
sudo chown -R $USER:$USER .
chmod +x docker-deploy.sh

# 修复Docker权限
sudo usermod -aG docker $USER
```

### 日志分析

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# 实时跟踪日志
docker-compose logs -f backend
```

## 🔒 安全配置

### 生产环境安全

1. **修改默认密码**
   - 数据库密码
   - JWT密钥
   - 管理员账户密码

2. **网络安全**
   - 使用HTTPS
   - 配置防火墙
   - 限制端口访问

3. **数据备份**
   ```bash
   # 备份数据库
   docker-compose exec db mysqldump -u root -p lat_lab_db > backup.sql
   
   # 备份上传文件
   tar -czf uploads-backup.tar.gz backend/uploads/
   ```

## 📊 性能优化

### 资源限制

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

### 缓存优化

```yaml
services:
  frontend:
    volumes:
      - ./frontend/dist:/usr/share/nginx/html:ro
      - nginx_cache:/var/cache/nginx

volumes:
  nginx_cache:
```

## 🔄 更新部署

### 代码更新

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build --no-cache

# 重启服务
docker-compose up -d
```

### 数据库迁移

```bash
# 进入后端容器
docker-compose exec backend bash

# 执行数据库迁移
alembic upgrade head
```

## 📚 相关文档

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [MySQL Docker 镜像](https://hub.docker.com/_/mysql)
- [Nginx 配置指南](https://nginx.org/en/docs/)

## 🆘 获取帮助

如果遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查服务日志
3. 在项目 Issues 中搜索相关问题
4. 创建新的 Issue 描述问题

---

**注意**: 生产环境部署前，请务必：
- 修改所有默认密码
- 配置HTTPS证书
- 设置防火墙规则
- 配置数据备份策略
- 测试所有功能 