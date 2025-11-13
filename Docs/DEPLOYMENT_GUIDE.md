# LAT-Lab 跨平台部署指南

<div align="center">

**🌍 Languages / 语言选择**

[![简体中文](https://img.shields.io/badge/DEPLOYMENT-简体中文-blue.svg)](./DEPLOYMENT_GUIDE.md) [![English](https://img.shields.io/badge/DEPLOYMENT-English-red.svg)](./DEPLOYMENT_GUIDE_EN.md)

</div>

本文档详细介绍 LAT-Lab 的跨平台部署脚本使用方法，包括 Linux/macOS 和 Windows 环境下的部署流程。

---

## 🚀 快速开始

### 系统要求

#### 基础要求
- **Docker**: 20.10 或更高版本
- **Docker Compose**: 2.0 或更高版本
- **内存**: 至少 1GB 可用内存
- **磁盘空间**: 至少 500MB 可用空间
- **网络**: 稳定的网络连接

#### 操作系统支持
- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+
- **macOS**: 10.15+ (Catalina)
- **Windows**: Windows 10 1809+ / Windows Server 2019+

---

## 🐧 Linux/macOS 部署

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab

# 给部署脚本添加执行权限
chmod +x deploy.sh
```

### 2. 配置环境变量

```bash
# 复制环境配置模板
cp docker.env.example .env

# 编辑配置文件
nano .env
```

> ℹ️ 如需进行传统安装，请复制 `env.traditional.example`，并参考 `Docs/TRADITIONAL_INSTALLATION.md` 中的步骤。

**关键配置项**:
```bash
# 数据库配置
DB_TYPE=mysql
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_USER=lat_lab_user
MYSQL_PASSWORD=your_db_password

# 安全配置
SECRET_KEY=your_very_long_and_secure_secret_key_here_minimum_32_chars
DEBUG=False

# 邮件配置
MAIL_SERVER=smtp.your-email-provider.com
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```

### 3. 启动服务

```bash
# 启动所有服务
./deploy.sh start

# 查看实时日志
./deploy.sh logs
```

### 4. 部署脚本命令

```bash
# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看日志
./deploy.sh logs

# 帮助信息
./deploy.sh help

# 传统安装辅助
./deploy.sh traditional
```

---

## 🪟 Windows 部署

### 1. 环境准备

```powershell
# 克隆项目
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab

# 检查 PowerShell 执行策略
Get-ExecutionPolicy

# 如果需要，临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. 配置环境变量

```powershell
# 复制环境配置模板
Copy-Item docker.env.example .env

# 使用记事本编辑配置文件
notepad .env
```

> ℹ️ 若准备进行传统安装，请改为复制 `env.traditional.example` 并参考 `Docs/TRADITIONAL_INSTALLATION.md`。

**关键配置项** (与 Linux 相同):
```bash
# 数据库配置
DB_TYPE=mysql
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_USER=lat_lab_user
MYSQL_PASSWORD=your_db_password

# 安全配置
SECRET_KEY=your_very_long_and_secure_secret_key_here_minimum_32_chars
DEBUG=False

# 邮件配置
MAIL_SERVER=smtp.your-email-provider.com
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```

### 3. 启动服务

```powershell
# 启动所有服务
.\deploy.ps1 start

# 查看服务状态
.\deploy.ps1 status

# 查看实时日志
.\deploy.ps1 logs
```

### 4. 部署脚本命令

```powershell
# 启动服务
.\deploy.ps1 start

# 停止服务
.\deploy.ps1 stop

# 重启服务
.\deploy.ps1 restart

# 查看日志
.\deploy.ps1 logs

# 帮助信息
.\deploy.ps1 help
```

---

## 🔧 高级配置

### 1. 资源限制配置

在 `.env` 文件中可以配置容器资源限制：

```bash
# 数据库资源限制
DB_CPU_LIMIT=1
DB_MEMORY_LIMIT=512M
DB_MEMORY_RESERVATION=384M

# 后端资源限制
BACKEND_CPU_LIMIT=1
BACKEND_MEMORY_LIMIT=384M
BACKEND_MEMORY_RESERVATION=256M
```

### 2. 健康检查配置

```bash
# 数据库健康检查
DB_HEALTH_TIMEOUT=20s
DB_HEALTH_RETRIES=10
DB_HEALTH_INTERVAL=30s
DB_HEALTH_START_PERIOD=40s

# 后端健康检查
BACKEND_HEALTH_TIMEOUT=30s
BACKEND_HEALTH_RETRIES=10
BACKEND_HEALTH_INTERVAL=30s
```

### 3. 日志配置

```bash
# 日志文件大小和数量限制
LOG_MAX_SIZE=10m
LOG_MAX_FILES=3
```

---

## 📊 监控和管理

### 1. 服务状态监控

```bash
# 查看容器状态
docker-compose ps

# 检查容器健康状态（以 backend 为例）
docker inspect --format '{{ .State.Health.Status }}' lat-lab_backend_1

# 查看实时资源使用
docker stats
```

### 2. 健康检查

```bash
# 后端心跳接口
curl -f http://localhost:8000/healthz

# 前端可用性
curl -I http://localhost
```

### 3. 日志查看

```bash
# 查看所有服务日志
./deploy.sh logs

# 跟踪单个服务日志
docker-compose logs -f backend
```

---

## 🚨 故障排除

### 1. 常见问题

#### 问题: Docker 服务未启动
```bash
# 检查 Docker 状态
sudo systemctl status docker

# 启动 Docker 服务
sudo systemctl start docker

# 设置开机自启
sudo systemctl enable docker
```

#### 问题: 端口被占用
```bash
# 查看端口占用
netstat -tulpn | grep :8000

# 杀死占用进程
sudo kill -9 <PID>
```

#### 问题: 内存不足
```bash
# 查看内存使用
free -h

# 清理 Docker 资源
docker system prune -a
```

### 2. 服务重启

```bash
# 重启特定服务
docker-compose restart backend

# 重启所有服务
./deploy.sh restart
```

### 3. 数据备份

```bash
# 备份数据库 (MySQL)
docker-compose exec db mysqldump -u root -p lat_lab_db > backup.sql

# 备份上传文件
tar -czf uploads_backup.tar.gz uploads/
```

---

## 🔄 更新和升级

### 1. 代码更新

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动服务
./deploy.sh restart
```

### 2. 版本升级

```bash
# 停止服务
./deploy.sh stop

# 备份数据
docker-compose exec db mysqldump -u root -p lat_lab_db > backup_$(date +%Y%m%d).sql
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# 更新代码
git pull origin main

# 重新启动服务
./deploy.sh start
```

---

## 📚 相关文档

- [Docker 部署详解](./DOCKER_DEPLOYMENT.md) - Docker 容器化部署详细说明
- [传统安装指南](./TRADITIONAL_INSTALLATION.md) - 非 Docker 环境安装指南
- [安全配置指南](./SECURITY.md) - 安全配置和最佳实践
- [更新日志](./CHANGELOG.md) - 版本更新记录

---

## 🤝 获取帮助

如果在部署过程中遇到问题，可以通过以下方式获取帮助：

- 📖 **文档**: 查看 [Docs](./) 目录了解详细信息
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/A-Dawn/LAT-Lab/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/A-Dawn/LAT-Lab/discussions)
- 📧 **邮件联系**: contact@luminarc.tech

---

<div align="center">

**🌟 如果这个部署指南对您有帮助，请给项目一个 Star ⭐**

Made with ❤️ by [Dawn_ARC](https://github.com/A-Dawn)

</div> 