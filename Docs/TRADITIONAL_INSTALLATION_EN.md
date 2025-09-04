# LAT-Lab Traditional Installation Guide

## 📋 Overview

This document provides detailed instructions on how to deploy the LAT-Lab project using traditional installation methods. Traditional installation is suitable for development environments, learning research, and personal use, using SQLite database without requiring additional database services.

## 🚀 Quick Start

### 1. Requirements

- **Python**: 3.8 or higher version
- **Node.js**: 14 or higher version
- **Git**: For cloning code
- **Operating System**: Windows, macOS, Linux all supported

### 2. One-Click Deployment

#### Clone the Project
```bash
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab
```

---

## 🔧 Backend Deployment

### 1. Enter Backend Directory
```bash
cd backend
```

### 2. Configure Environment Variables
```bash
# Copy traditional installation specific environment configuration file
cp env.traditional.example .env

# Edit configuration file (optional)
# Windows: notepad .env
# Linux/macOS: nano .env
```

**Important**: Traditional installation uses SQLite database by default, no additional configuration needed. The `DB_TYPE=sqlite` in the `.env` file is already correctly set.

### 3. Create Virtual Environment and Install Dependencies
```bash
# Run environment setup script
python scripts/setup_env.py

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 4. Initialize Database
```bash
# Create data directory
mkdir -p data

# Run database migrations
python scripts/run_migrations.py

# Initialize SQLite database and sample data
python scripts/init-db-sqlite.py

# Initialize sample plugins
python -m src.lat_lab.init_examples
```

**Default Administrator Account**:
- Username: `admin`
- Password: `admin123`
- Email: `admin@example.com`

### 5. Start Backend Service
```bash
# Start main application
python -m src.lat_lab.main

# Or use uvicorn directly
uvicorn src.lat_lab.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎨 Frontend Deployment

### 1. Enter Frontend Directory
```bash
# Open new terminal window
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start Development Server
```bash
npm run dev
```

---

## 🌐 Access the System

After successful startup, you can access through the following addresses:

- **Frontend Interface**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:5173/admin

---

## ⚙️ Configuration

### Environment Variables

The traditional installation `.env` file contains the following key configurations:

```bash
# Database settings (SQLite)
DB_TYPE=sqlite  # Traditional installation uses SQLite

# Development environment configuration
DEBUG=True       # Recommended True for development, False for production
HOST=0.0.0.0    # Listen on all network interfaces
PORT=8000        # Backend service port

# Frontend configuration
BASE_URL=http://localhost:5173  # Frontend address

# Security configuration
SECRET_KEY=your_secret_key_here_for_traditional_installation_minimum_32_chars
```

### Database Configuration

- **Type**: SQLite (default)
- **File Location**: `backend/data/blog.db`
- **Advantages**: No need to install database service, file-based database, suitable for development and personal use

---

## 🗂️ Directory Structure

```
LAT-Lab/
├── backend/                   # Backend service
│   ├── .env                  # Environment configuration (copied from env.traditional.example)
│   ├── data/                 # SQLite database files
│   ├── uploads/              # Upload files
│   ├── plugins/              # Installed plugins
│   └── src/lat_lab/         # Application core code
├── frontend/                 # Frontend application
│   ├── src/                  # Vue.js source code
│   └── package.json          # Dependency configuration
└── README.md                 # Project description
```

---

## 🔒 Security Considerations

### Production Environment Deployment

If you want to deploy traditional installation to production environment:

1. **Change Default Passwords**: Immediately change administrator account password
2. **Environment Variables**: Set `DEBUG=False`
3. **JWT Secret Key**: Use strong random secret key
4. **Network Security**: Configure firewall, restrict port access
5. **HTTPS**: Configure SSL certificates

### Development Environment Security

- `DEBUG=True`: Display detailed error information for debugging
- `CORS_ORIGINS`: Allow frontend cross-origin access
- Rate Limiting: Use more relaxed limits for development environment

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Failure
```bash
# Check if data directory exists
ls -la backend/data/

# Check .env file configuration
cat backend/.env | grep DB_TYPE
```

#### 2. Dependency Installation Failure
```bash
# Recreate virtual environment
rm -rf backend/.venv
cd backend
python scripts/setup_env.py
```

#### 3. Port Occupied
```bash
# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :5173

# Modify port configuration
# Change PORT value in .env file
```

#### 4. Permission Issues
```bash
# Fix file permissions
chmod -R 755 backend/data/
chmod -R 755 backend/uploads/
```

### View Logs

```bash
# View backend logs
tail -f backend/data/lat_lab.log

# View frontend build logs
cd frontend
npm run dev
```

---

## 📚 Related Documentation

- [Docker Deployment Guide](./DOCKER_DEPLOYMENT_EN.md)
- [Project Overview](../README_EN.md)
- [Backend Description](../backend/README.md)
- [Frontend Description](../frontend/README.md)

---

## 🆘 Getting Help

If you encounter issues, please:

1. Check the troubleshooting section of this document
2. Check service logs
3. Search for related issues in project Issues
4. Create a new Issue describing the problem

---

## 📝 Deployment Checklist

- [ ] Environment requirements met (Python 3.8+, Node.js 14+)
- [ ] Project code cloned
- [ ] Environment configuration file copied and edited
- [ ] Virtual environment created and dependencies installed
- [ ] Database initialized and migrated
- [ ] Administrator user created
- [ ] Backend service started successfully
- [ ] Frontend service started successfully
- [ ] System functionality tested and passed

---

**Note**: Traditional installation is suitable for development and learning. For production environment, it's recommended to use Docker deployment for better stability and maintainability. 