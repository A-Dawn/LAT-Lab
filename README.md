# LAT-Lab 博客系统

LAT-Lab是一个现代化的个人博客系统，基于前后端分离架构，提供丰富的功能和插件扩展能力。

## 安全更新报告 (2025-07-25)

本次更新对系统进行了全面的安全审查和加固，修复了多个安全漏洞，显著提升了系统整体安全性，具体详见

[v0.2.3_DevOps.md](https://github.com/A-Dawn/LAT-Lab/blob/main/Docs/v0.2.3_DevOps.md)	"0.2.3更新"



## 项目概述

LAT-Lab博客系统是一个完整的博客解决方案，包含文章管理、用户管理、分类标签、评论系统和强大的插件机制。系统采用前后端分离架构，后端使用FastAPI构建RESTful API，前端使用Vue.js提供现代化的用户界面。

### 版本信息
- 当前版本: v0.2.3
- 发布日期: 2025-07-25

## 主要功能

### 内容管理
- 文章撰写、编辑和发布
- Markdown编辑器支持
- 分类和标签管理
- 文章状态管理（草稿、已发布）
- 文章可见性控制

### 用户系统
- 用户注册和登录
- 邮箱验证
- 用户资料管理
- 基于JWT的认证

### 评论系统
- 多级评论支持
- 评论管理

### 插件系统
- 可扩展的插件架构
- 插件市场
- 自定义前端小部件
- 插件安装和管理

## 技术栈

### 后端
- FastAPI - 高性能Python Web框架
- SQLAlchemy - ORM框架
- Alembic - 数据库迁移工具
- Pydantic - 数据验证
- JWT - 认证机制

### 前端
- Vue.js - 渐进式JavaScript框架
- Vue Router - 路由管理
- Vuex - 状态管理
- Axios - HTTP客户端
- Marked - Markdown渲染

## 安装指南

### 环境要求
- Python 3.8+
- Node.js 14+
- SQLite (默认) 或 MySQL

### 安装方法一：直接安装（推荐用于开发）

1. **配置后端**
```bash
# 进入后端目录
cd backend

# 创建并配置环境变量
cp ../env.example .env
# 编辑.env文件，设置必要的配置项

# 创建虚拟环境并安装依赖（使用uv）
python scripts/setup_env.py

# 激活虚拟环境
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
# source .venv/bin/activate

# 创建数据目录(如果不存在)
mkdir -p data

# 复制配置文件
python scripts/copy_config.py

# 运行数据库迁移(注意必须使用run参数)
python scripts/run_migrations.py run

# 初始化示例数据和插件
python -m src.lat_lab.init_examples

# 创建管理员用户
python scripts/init_db.py
# 注：若出现bcrypt警告可以忽略，只要看到"管理员用户创建成功"即可

# 启动后端服务
python -m src.lat_lab.main
```

2. **配置前端**
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 开发环境: 启动开发服务器
npm run dev

# 生产环境: 构建前端项目
npm run build
# 构建完成后，dist目录包含所有静态文件
```

### 安装方法二：Docker部署（推荐用于生产）

1. **创建环境变量文件**:
```bash
cp env.example backend/.env
# 编辑.env文件，设置必要的配置项
```

2. **启动服务**:
```bash
docker-compose up -d
```

3. **初始化数据库和创建管理员用户**（首次部署时）:
```bash
# 复制配置文件
docker-compose exec backend python scripts/copy_config.py

# 运行数据库迁移
docker-compose exec backend python scripts/run_migrations.py run

# 初始化示例插件
docker-compose exec backend python -m src.lat_lab.init_examples

# 创建管理员用户
docker-compose exec backend python scripts/init_db.py
```
> ⚠️ **重要提示**：这些命令的执行顺序非常关键，请务必按顺序执行。

4. **访问应用**:
   - 前端: http://localhost (默认端口80)
   - 后端API: http://localhost/api
   - API文档: http://localhost/api/docs (仅在调试模式下可用)

## 常见问题解决方案

1. **"Target database is not up to date"错误**:
   - 必须先运行现有迁移: `python scripts/run_migrations.py run`
   - 然后才能创建新的迁移: `python scripts/run_migrations.py create -m "迁移说明"`

2. **"no such table"错误**:
   - 说明数据库表结构未创建或数据库文件被删除
   - 确保已运行数据库迁移: `python scripts/run_migrations.py run`
   - 按照正确顺序初始化: 运行迁移 → 初始化示例 → 创建管理员

3. **marketplace_config.json缺失**:
   - 运行 `python scripts/copy_config.py` 复制配置文件
   - 确保data目录已创建: `mkdir -p data`

4. **bcrypt警告信息**:
   - 创建管理员时的"error reading bcrypt version"警告可以安全忽略
   - 只要看到"管理员用户创建成功"的信息，表示操作已完成

5. **前端开发环境API代理错误**:
   - 如果遇到 "connect ECONNREFUSED ::1:8000" 错误，可能是IPv6/IPv4问题
   - 修改`frontend/vite.config.js`中的代理配置，使用`127.0.0.1`而非`localhost`

## 安全说明

LAT-Lab博客系统已实施多层安全措施:

1. **XSS防护**: 前端集成了DOMPurify库，对所有使用v-html的内容进行净化。详细说明请参考`frontend/SECURITY.md`。

2. **URL参数验证**: 所有从URL获取的参数都经过严格验证，防止参数注入攻击。

3. **文件路径安全**: 所有涉及文件路径操作的功能均经过严格的安全验证，防止路径遍历攻击，详情请参考本文档的"安全更新报告"部分。

4. **安全配置建议**:
   - 修改所有默认密码
   - 为SECRET_KEY设置强随机密钥
   - 限制数据库用户权限
   - 配置HTTPS加密传输
   - 定期备份数据
   - 生产环境配置内容安全策略(CSP)头

## 插件市场

LAT-Lab博客系统提供了强大的插件市场功能，允许管理员浏览、安装和管理各种插件。插件市场基于JSON配置文件，开发者可以通过编辑配置文件来添加新的插件。

### 插件功能
- 浏览可用插件
- 按分类和标签筛选
- 查看插件详情和截图
- 一键安装插件

## 项目目录结构

v0.2.1版本采用了src目录结构，项目结构如下：

```
backend/
├── data/                  # 数据存储目录
│   ├── blog.db           # SQLite数据库(如果使用)
│   └── marketplace_config.json  # 插件市场配置
├── plugins/               # 已安装的插件
├── plugin_examples/       # 示例插件
├── scripts/               # 管理脚本
├── src/                   # 源代码
│   └── lat_lab/          # 主应用包
│       ├── api/          # API接口
│       ├── core/         # 核心配置
│       ├── crud/         # 数据库操作
│       ├── models/       # 数据模型
│       ├── schemas/      # 数据架构
│       ├── services/     # 服务层
│       ├── utils/        # 工具函数
│       └── main.py       # 应用入口
├── uploads/               # 上传文件存储
└── pyproject.toml         # 项目配置
```

## 配置说明

### 后端配置
主要配置文件位于`backend/src/lat_lab/core/config.py`，可以通过环境变量覆盖默认设置：
- 数据库设置
- JWT密钥
- 邮件服务器配置
- 插件系统设置

### 安全配置
- **管理员账户**：首次安装后必须创建管理员账户。如使用`setup_tools`目录下的默认脚本，请立即修改默认密码
- **JWT密钥**：在生产环境中应修改`config.py`中的默认密钥
- **数据库密码**：修改`docker-compose.yml`中的默认数据库密码

> 💡 系统管理和安装工具位于 `backend/setup_tools/` 目录下

### 前端配置
前端配置位于`.env.development`和`.env.production`文件中，可以根据需要调整API基础URL等设置。

## 开发指南

### 创建新插件
1. 参考`backend/plugin_examples`目录中的示例插件
2. 编写插件代码并放置在适当位置
3. 通过管理界面或配置文件注册插件

### 贡献代码
在标准制作完成并开放git插件市场后，计划接受社区贡献。

## 所有权与使用许可
LAT-Lab博客系统 © 2025，保留所有权利。

本人对LAT-Lab博客系统的代码、设计、文档及相关组件拥有知识产权和所有权。使用本项目内容前，请先获取许可。

**所有权说明**：
- 本项目的代码、设计和文档均为本人创作成果。
- 相关知识产权，包括著作权、专利权和商标权归本人所有。
- 如需使用本项目内容，请事先联系获取许可。

计划在标准制作完成并开放基于git仓库的插件市场后，考虑采用开源许可证进行部分内容授权。

## 更新日志

### v0.2.3 (2025-07-28)
- 【安全更新】修复了多个潜在的路径遍历漏洞
- 【安全更新】增强了敏感数据安全存储机制
- 【安全更新】加强了前端登录认证机制
- 【安全更新】增强了用户管理工具安全性
- 新增Web Crypto API安全存储功能
- 添加用户创建和登录验证工具
- 更新crypto-js依赖至4.2.0版本
- 增强了文件名和路径处理的安全性
- 实现了统一的安全文件名处理机制
- 完善了插件系统的路径安全验证

### v0.2.1 (2025-07-22)
- 添加插件市场功能
- 优化了前端用户界面
- 增强了Markdown编辑器功能
- 修复了多个已知问题

### v0.2.0 (2025-06-15)
- 重构项目结构，使用src目录结构
- 添加了插件系统
- 增加了主题切换功能
- 完善用户权限管理

### v0.1.1 (2025-05-20)
- 添加邮箱验证功能
- 增强用户资料管理
- 完善评论系统
- 修复若干Bug

### v0.1.0 (2025-05-01)
- 首次发布
- 实现基础博客功能
- 支持文章管理、用户系统
- 基础分类和标签功能

## 联系方式
如有问题或建议，请通过以下方式联系我们：
- 项目主页：[https://github.com/A-Dawn/LAT-Lab](https://github.com/A-Dawn/LAT-Lab)
- 电子邮件：contact@luminarc.tech

---
LAT-Lab博客系统 © 2025 - 保留所有权利，使用前请先获取许可。
