# LAT-Lab Cross-Platform Deployment Guide

<div align="center">

**🌍 Languages / 语言选择**

[![简体中文](https://img.shields.io/badge/DEPLOYMENT-简体中文-blue.svg)](./DEPLOYMENT_GUIDE.md) [![English](https://img.shields.io/badge/DEPLOYMENT-English-red.svg)](./DEPLOYMENT_GUIDE_EN.md)

</div>

This document provides detailed instructions for using LAT-Lab's cross-platform deployment scripts, including deployment processes for Linux/macOS and Windows environments.

---

## 🚀 Quick Start

### System Requirements

#### Basic Requirements
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Memory**: At least 1GB available memory
- **Disk Space**: At least 500MB available space
- **Network**: Stable network connection

#### Operating System Support
- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+
- **macOS**: 10.15+ (Catalina)
- **Windows**: Windows 10 1809+ / Windows Server 2019+

---

## 🐧 Linux/macOS Deployment

### 1. Environment Preparation

```bash
# Clone project
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab

# Add execution permission to deployment script
chmod +x deploy.sh
```

### 2. Configure Environment Variables

```bash
# Copy environment configuration template
cp docker.env.example .env

# Edit configuration file
nano .env
```

> ℹ️ For traditional (non-Docker) setup steps, copy `env.traditional.example` and follow `Docs/TRADITIONAL_INSTALLATION_EN.md`.

**Key Configuration Items**:
```bash
# Database configuration
DB_TYPE=mysql
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_USER=lat_lab_user
MYSQL_PASSWORD=your_db_password

# Security configuration
SECRET_KEY=your_very_long_and_secure_secret_key_here_minimum_32_chars
DEBUG=False

# Email configuration
MAIL_SERVER=smtp.your-email-provider.com
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```

### 3. Start Services

```bash
# Start all services
./deploy.sh start

# View real-time logs
./deploy.sh logs
```

### 4. Deployment Script Commands

```bash
# Start services
./deploy.sh start

# Stop services
./deploy.sh stop

# Restart services
./deploy.sh restart

# View logs
./deploy.sh logs

# Help information
./deploy.sh help

# Traditional installation helper
./deploy.sh traditional
```

---

## 🪟 Windows Deployment

### 1. Environment Preparation

```powershell
# Clone project
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab

# Check PowerShell execution policy
Get-ExecutionPolicy

# If needed, temporarily allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Configure Environment Variables

```powershell
# Copy environment configuration template
Copy-Item docker.env.example .env

# Edit configuration file with Notepad
notepad .env
```

> ℹ️ Preparing a traditional installation? Copy `env.traditional.example` instead and follow `Docs/TRADITIONAL_INSTALLATION_EN.md`.

**Key Configuration Items** (same as Linux):
```bash
# Database configuration
DB_TYPE=mysql
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_USER=lat_lab_user
MYSQL_PASSWORD=your_db_password

# Security configuration
SECRET_KEY=your_very_long_and_secure_secret_key_here_minimum_32_chars
DEBUG=False

# Email configuration
MAIL_SERVER=smtp.your-email-provider.com
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```

### 3. Start Services

```powershell
# Start all services
.\deploy.ps1 start

# Check service status
.\deploy.ps1 status

# View real-time logs
.\deploy.ps1 logs
```

### 4. Deployment Script Commands

```powershell
# Start services
.\deploy.ps1 start

# Stop services
.\deploy.ps1 stop

# Restart services
.\deploy.ps1 restart

# View logs
.\deploy.ps1 logs

# Help information
.\deploy.ps1 help
```

---

## 🔧 Advanced Configuration

### 1. Resource Limit Configuration

You can configure container resource limits in the `.env` file:

```bash
# Database resource limits
DB_CPU_LIMIT=1
DB_MEMORY_LIMIT=512M
DB_MEMORY_RESERVATION=384M

# Backend resource limits
BACKEND_CPU_LIMIT=1
BACKEND_MEMORY_LIMIT=384M
BACKEND_MEMORY_RESERVATION=256M
```

### 2. Health Check Configuration

```bash
# Database health check
DB_HEALTH_TIMEOUT=20s
DB_HEALTH_RETRIES=10
DB_HEALTH_INTERVAL=30s
DB_HEALTH_START_PERIOD=40s

# Backend health check
BACKEND_HEALTH_TIMEOUT=30s
BACKEND_HEALTH_RETRIES=10
BACKEND_HEALTH_INTERVAL=30s
```

### 3. Log Configuration

```bash
# Log file size and number limits
LOG_MAX_SIZE=10m
LOG_MAX_FILES=3
```

---

## 📊 Monitoring and Management

### 1. Service Status Monitoring

```bash
# Show running containers
docker-compose ps

# Inspect health status (example for backend)
docker inspect --format '{{ .State.Health.Status }}' lat-lab_backend_1

# View resource usage
docker stats
```

### 2. Health Check

```bash
# Backend heartbeat
curl -f http://localhost:8000/healthz

# Frontend availability
curl -I http://localhost
```

### 3. Log Viewing

```bash
# View all service logs
./deploy.sh logs

# Tail a single service
docker-compose logs -f backend
```

---

## 🚨 Troubleshooting

### 1. Common Issues

#### Issue: Docker Service Not Started
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker service
sudo systemctl start docker

# Set auto-start
sudo systemctl enable docker
```

#### Issue: Port Occupied
```bash
# Check port usage
netstat -tulpn | grep :8000

# Kill occupying process
sudo kill -9 <PID>
```

#### Issue: Insufficient Memory
```bash
# Check memory usage
free -h

# Clean Docker resources
docker system prune -a
```

### 2. Service Restart

```bash
# Restart specific service
docker-compose restart backend

# Restart all services
./deploy.sh restart
```

### 3. Data Backup

```bash
# Backup database (MySQL)
docker-compose exec db mysqldump -u root -p lat_lab_db > backup.sql

# Backup upload files
tar -czf uploads_backup.tar.gz uploads/
```

---

## 🔄 Updates and Upgrades

### 1. Code Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart services
./deploy.sh restart
```

### 2. Version Upgrades

```bash
# Stop services
./deploy.sh stop

# Backup data
docker-compose exec db mysqldump -u root -p lat_lab_db > backup_$(date +%Y%m%d).sql
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Update code
git pull origin main

# Restart services
./deploy.sh start
```

---

## 📚 Related Documentation

- [Docker Deployment Details](./DOCKER_DEPLOYMENT.md) - Detailed Docker containerized deployment instructions
- [Traditional Installation Guide](./TRADITIONAL_INSTALLATION.md) - Non-Docker environment installation guide
- [Security Configuration Guide](./SECURITY.md) - Security configuration and best practices
- [Changelog](./CHANGELOG_EN.md) - Version update records

---

## 🤝 Getting Help

If you encounter issues during deployment, you can get help through the following channels:

- 📖 **Documentation**: Check [Docs](./) directory for detailed information
- 🐛 **Issue Feedback**: [GitHub Issues](https://github.com/A-Dawn/LAT-Lab/issues)
- 💬 **Discussion**: [GitHub Discussions](https://github.com/A-Dawn/LAT-Lab/discussions)
- 📧 **Email Contact**: contact@luminarc.tech

---

<div align="center">

**🌟 If this deployment guide helps you, please give the project a Star ⭐**

Made with ❤️ by [Dawn_ARC](https://github.com/A-Dawn)

</div> 