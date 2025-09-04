# LAT-Lab 传统安装部署指南

## 📋 概述

本文档详细说明如何使用传统安装方式部署 LAT-Lab 项目。传统安装方式适合开发环境、学习研究和个人使用，使用 SQLite 数据库，无需额外的数据库服务。

## 🚀 快速开始

### 1. 环境要求

- **Python**: 3.8 或更高版本
- **Node.js**: 14 或更高版本
- **Git**: 用于克隆代码
- **操作系统**: Windows、macOS、Linux 均可

### 2. 一键部署

#### 克隆项目
```bash
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab
```

---

## 🔧 后端部署

### 1. 进入后端目录
```bash
cd backend
```

### 2. 配置环境变量
```bash
# 复制传统安装专用的环境配置文件
cp env.traditional.example .env

# 编辑配置文件 (可选)
# Windows: notepad .env
# Linux/macOS: nano .env
```

**重要**: 传统安装默认使用 SQLite 数据库，无需额外配置。`.env` 文件中的 `DB_TYPE=sqlite` 已经正确设置。

### 3. 创建虚拟环境并安装依赖
```bash
# 运行环境设置脚本
python scripts/setup_env.py

# 激活虚拟环境
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 4. 初始化数据库
```bash
# 创建数据目录
mkdir -p data

# 运行数据库迁移
python scripts/run_migrations.py

# 初始化SQLite数据库和示例数据
python scripts/init-db-sqlite.py

# 初始化示例插件
python -m src.lat_lab.init_examples
```

**默认管理员账户**:
- 用户名: `admin`
- 密码: `admin123`
- 邮箱: `admin@example.com`

### 5. 启动后端服务
```bash
# 启动主应用
python -m src.lat_lab.main

# 或使用 uvicorn 直接启动
uvicorn src.lat_lab.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎨 前端部署

### 1. 进入前端目录
```bash
# 新开终端窗口
cd frontend
```

### 2. 安装依赖
```bash
npm install
```

### 3. 启动开发服务器
```bash
npm run dev
```

---

## 🌐 访问系统

启动成功后，可以通过以下地址访问：

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **管理后台**: http://localhost:5173/admin

---

## ⚙️ 配置说明

### 环境变量配置

传统安装的 `.env` 文件包含以下关键配置：

```bash
# 数据库设置 (SQLite)
DB_TYPE=sqlite  # 传统安装使用SQLite

# 开发环境配置
DEBUG=True       # 开发环境建议True，生产环境False
HOST=0.0.0.0    # 监听所有网络接口
PORT=8000        # 后端服务端口

# 前端配置
BASE_URL=http://localhost:5173  # 前端地址

# 安全配置
SECRET_KEY=your_secret_key_here_for_traditional_installation_minimum_32_chars
```

### 数据库配置

- **类型**: SQLite (默认)
- **文件位置**: `backend/data/blog.db`
- **优势**: 无需安装数据库服务，文件型数据库，适合开发和个人使用

---

## 🗂️ 目录结构

```
LAT-Lab/
├── backend/                   # 后端服务
│   ├── .env                  # 环境配置 (从env.traditional.example复制)
│   ├── data/                 # SQLite数据库文件
│   ├── uploads/              # 上传文件
│   ├── plugins/              # 已安装插件
│   └── src/lat_lab/         # 应用核心代码
├── frontend/                 # 前端应用
│   ├── src/                  # Vue.js 源码
│   └── package.json          # 依赖配置
└── README.md                 # 项目说明
```

---

## 🔒 安全注意事项

### 生产环境部署

如果要将传统安装部署到生产环境：

1. **修改默认密码**: 立即修改管理员账户密码
2. **环境变量**: 设置 `DEBUG=False`
3. **JWT密钥**: 使用强随机密钥
4. **网络安全**: 配置防火墙，限制端口访问
5. **HTTPS**: 配置SSL证书

### 开发环境安全

- `DEBUG=True`: 显示详细错误信息，便于调试
- `CORS_ORIGINS`: 允许前端跨域访问
- 速率限制: 开发环境使用更宽松的限制

---

## 🚨 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查数据目录是否存在
ls -la backend/data/

# 检查.env文件配置
cat backend/.env | grep DB_TYPE
```

#### 2. 依赖安装失败
```bash
# 重新创建虚拟环境
rm -rf backend/.venv
cd backend
python scripts/setup_env.py
```

#### 3. 端口被占用
```bash
# 检查端口占用
netstat -tulpn | grep :8000
netstat -tulpn | grep :5173

# 修改端口配置
# 在.env文件中修改PORT值
```

#### 4. 权限问题
```bash
# 修复文件权限
chmod -R 755 backend/data/
chmod -R 755 backend/uploads/
```

### 日志查看

```bash
# 查看后端日志
tail -f backend/data/lat_lab.log

# 查看前端构建日志
cd frontend
npm run dev
```

---

## 📚 相关文档

- [Docker 部署指南](./DOCKER_DEPLOYMENT.md)
- [项目概述](../README.md)
- [后端说明](../backend/README.md)
- [前端说明](../frontend/README.md)

---

## 🆘 获取帮助

如果遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查服务日志
3. 在项目 Issues 中搜索相关问题
4. 创建新的 Issue 描述问题

---

## 📝 部署检查清单

- [ ] 环境要求满足 (Python 3.8+, Node.js 14+)
- [ ] 项目代码克隆完成
- [ ] 环境配置文件复制并编辑
- [ ] 虚拟环境创建和依赖安装
- [ ] 数据库初始化和迁移
- [ ] 管理员用户创建
- [ ] 后端服务启动成功
- [ ] 前端服务启动成功
- [ ] 系统功能测试通过

---

**注意**: 传统安装方式适合开发和学习，生产环境建议使用 Docker 部署方式以获得更好的稳定性和可维护性。 