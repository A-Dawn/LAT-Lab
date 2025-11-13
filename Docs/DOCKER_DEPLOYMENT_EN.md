# LAT-Lab Docker Deployment Guide

## 📋 Overview

This document provides detailed instructions on how to deploy the LAT-Lab project using Docker. Docker deployment offers advantages of environment consistency, rapid deployment, and easy management.

## 🆕 What's New (v1.1.0)

- **Unified deployment scripts**: The new `deploy.sh` (Linux/macOS) and `deploy.ps1` (Windows) replace the legacy `docker-deploy` helpers with guided environment setup, health checks, log streaming, and cleanup utilities.
- **Service health probes**: `docker-compose.yml` now defines health checks for MySQL, backend, and frontend containers so the stack only boots when dependencies are ready.
- **Resource & feature toggles**: Expanded environment templates (`docker.env.example`) expose CPU/memory limits, log rotation options, and the `VITE_ENABLE_DEV_TOOLS` frontend flag.

## 🚀 Quick Start

### 1. Requirements

- Docker Desktop 4.0+ or Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB available memory
- At least 10GB available disk space

### 2. One-Click Deployment

#### Linux/macOS
```bash
# Clone the project
git clone <repository-url>
cd LAT-Lab

# Set execution permissions
chmod +x deploy.sh

# Start services with guided setup
./deploy.sh start
```

#### Windows PowerShell
```powershell
# Clone the project
git clone <repository-url>
cd LAT-Lab

# Start services with guided setup
.\deploy.ps1 start
```

#### Manual Deployment
```bash
# Copy environment configuration file
cp docker.env.example .env

# Edit configuration file
nano .env

# Start services
docker-compose up -d

# Wait for MySQL container to start, then initialize sample data (optional)
docker-compose exec backend python scripts/init-db-mysql.py
```

## ⚙️ Configuration

### Environment Variables

Edit the `.env` file and set the following key configurations:

```bash
# Database configuration
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_USER=lat_lab_user
MYSQL_PASSWORD=your_secure_user_password
MYSQL_DB=lat_lab_db

# JWT Secret Key (minimum 32 characters)
SECRET_KEY=your_very_long_and_secure_secret_key_here_minimum_32_chars

# Website URL
BASE_URL=http://localhost

# Debug mode (set to False for production)
DEBUG=False
```

### Port Configuration

- **Frontend**: http://localhost (port 80)
- **Backend API**: http://localhost:8000 (port 8000)
- **Database**: localhost:3306 (port 3306)

## 🐳 Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Nginx)       │◄──►│   (FastAPI)     │◄──►│   (MySQL 8.0)   │
│   Port: 80      │    │   Port: 8000    │    │   Port: 3306    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🗄️ Database Initialization

Docker deployment uses MySQL database with the following initialization process:

1. **Automatic Initialization**: MySQL container automatically executes `init-db-mysql.sql` to create database and user on startup
2. **Manual Initialization**: After container startup, you can manually run `init-db-mysql.py` to create sample data
3. **Data Persistence**: Database data is stored in Docker volume `db_data`

## 📁 Directory Structure

```
LAT-Lab/
├── docker-compose.yml          # Docker Compose configuration
├── docker.env.example          # Docker environment variables template
├── .env                        # Environment variables configuration (needs to be created)
├── deploy.sh                   # Cross-platform deployment script (Linux/macOS)
├── deploy.ps1                  # Cross-platform deployment script (Windows PowerShell)
├── backend/
│   ├── Dockerfile              # Backend image build file
│   └── scripts/
│       ├── init-db-mysql.sql   # MySQL database initialization SQL script
│       └── init-db-mysql.py    # MySQL database initialization Python script
└── frontend/
    ├── Dockerfile              # Frontend image build file
    └── nginx.conf              # Nginx configuration file
```

## 🔧 Common Commands

### Service Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service_name]
```

### Using Deployment Scripts

```bash
# Start services (Docker)
./deploy.sh start

# Start traditional installation bootstrap
./deploy.sh traditional

# Stop services
./deploy.sh stop

# Restart services
./deploy.sh restart

# View combined logs
./deploy.sh logs

# Clean up containers and volumes
./deploy.sh clean
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :80
netstat -tulpn | grep :8000

# Modify port mapping in docker-compose.yml
ports:
  - "8080:80"      # Frontend uses port 8080
  - "8001:8000"    # Backend uses port 8001
```

#### 2. Database Connection Failure
```bash
# Check database container status
docker-compose ps db

# View database logs
docker-compose logs db

# Manually connect to database
docker-compose exec db mysql -u root -p
```

#### 3. Frontend Cannot Access Backend API
```bash
# Check backend service status
docker-compose ps backend

# View backend logs
docker-compose logs backend

# Test API connection
curl http://localhost:8000/api/health
```

#### 4. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x deploy.sh

# Fix Docker permissions
sudo usermod -aG docker $USER
```

### Log Analysis

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Real-time log tracking
docker-compose logs -f backend
```

## 🔒 Security Configuration

### Production Environment Security

1. **Change Default Passwords**
   - Database passwords
   - JWT secret key
   - Administrator account password

2. **Network Security**
   - Use HTTPS
   - Configure firewall
   - Restrict port access

3. **Data Backup**
   ```bash
   # Backup database
   docker-compose exec db mysqldump -u root -p lat_lab_db > backup.sql
   
   # Backup upload files
   tar -czf uploads-backup.tar.gz backend/uploads/
   ```

## 📊 Performance Optimization

### Resource Limits

Add resource limits in `docker-compose.yml`:

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

### Cache Optimization

```yaml
services:
  frontend:
    volumes:
      - ./frontend/dist:/usr/share/nginx/html:ro
      - nginx_cache:/var/cache/nginx

volumes:
  nginx_cache:
```

## 🔄 Update Deployment

### Code Updates

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

### Database Migration

```bash
# Enter backend container
docker-compose exec backend bash

# Execute database migration
alembic upgrade head
```

## 📚 Related Documentation

- [Docker Official Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MySQL Docker Image](https://hub.docker.com/_/mysql)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)

## 🆘 Getting Help

If you encounter issues, please:

1. Check the troubleshooting section of this document
2. Check service logs
3. Search for related issues in project Issues
4. Create a new Issue describing the problem

---

**Note**: Before deploying to production environment, please ensure:
- Change all default passwords
- Configure HTTPS certificates
- Set firewall rules
- Configure data backup strategy
- Test all functionality 