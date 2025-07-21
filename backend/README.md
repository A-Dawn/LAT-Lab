# LAT-LAB 博客系统

LAT-LAB是一个现代化的博客系统，基于前后端分离架构，使用FastAPI和SQLite数据库构建，提供丰富的功能和插件扩展能力。

## 项目概述

LAT-LAB博客系统是一个完整的博客解决方案，包含文章管理、用户管理、分类标签、评论系统和强大的插件机制。系统采用前后端分离架构，后端使用FastAPI构建RESTful API，前端使用Vue.js提供现代化的用户界面。

### 版本信息
- 当前版本: v0.1.0
- 发布日期: 2025-07-16

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
- 点赞功能

### 插件系统
- 可扩展的插件架构
- 插件市场集成
- 自定义前端小部件
- 插件安装和管理

## 技术栈

### 后端
- FastAPI - 高性能Python Web框架
- SQLAlchemy - ORM框架
- Alembic - 数据库迁移工具
- Pydantic - 数据验证
- JWT - 认证机制
- SQLite - 轻量级数据库

### 前端
- Vue.js - 渐进式JavaScript框架
- Vue Router - 路由管理
- Vuex - 状态管理
- Axios - HTTP客户端
- Marked - Markdown渲染

## 现代开发模式

LAT-LAB采用现代Python项目结构和开发工具，包括：

- **pyproject.toml**：作为项目唯一配置入口，简化依赖管理
- **虚拟环境（.venv）**：隔离项目依赖，避免污染系统环境
- **UV包管理工具**：替代传统pip，提供更快的依赖安装和版本管理
- **模块化结构**：清晰的代码组织，提高可维护性
- **类型提示**：通过类型注解提升代码质量和开发体验

## 快速开始

### 环境设置

```bash
# 克隆代码
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab

# 设置环境（创建虚拟环境并安装依赖）
python scripts/setup_env.py
# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 初始化与运行

```bash
# 运行数据库迁移
python scripts/run_migrations.py run

# 初始化数据库（创建管理员用户和基础数据）
python scripts/init_db.py

# 启动服务
python -m src.lat_lab.main

# 或使用命令行入口点
lat-lab
```

## 项目结构

```
backend/
├── .venv/                      # 虚拟环境目录
├── pyproject.toml              # 项目配置和依赖管理
├── README.md                   # 项目文档
├── src/                        # 源代码目录
│   └── lat_lab/                # 项目包
│       ├── __init__.py
│       ├── main.py             # 应用入口
│       ├── api/                # API模块
│       ├── core/               # 核心配置
│       ├── crud/               # 数据库操作
│       ├── models/             # 数据模型
│       ├── schemas/            # Pydantic模式
│       ├── services/           # 服务层
│       ├── tasks/              # 任务和后台作业
│       └── utils/              # 工具函数
├── alembic.ini                 # Alembic配置
├── migrations/                 # 数据库迁移
├── data/                       # 数据文件
│   └── blog.db                 # SQLite数据库
├── tests/                      # 测试目录
├── marketplace_config.json     # 市场配置
├── plugin_examples/            # 插件示例
├── uploads/                    # 上传文件目录
└── scripts/                    # 实用脚本
    ├── setup_env.py            # 环境设置脚本
    ├── init_db.py              # 数据库初始化脚本
    └── run_migrations.py       # 数据库迁移脚本
```

## 开发指南

### 数据库迁移

创建新的迁移：

```bash
python scripts/run_migrations.py create -m "迁移描述"
```

应用迁移：

```bash
python scripts/run_migrations.py run
```

### 添加新依赖

使用UV添加依赖：

```bash
# 激活虚拟环境后
uv pip install package-name
```

然后更新pyproject.toml文件，可以使用以下命令：

```bash
# 自动更新pyproject.toml
uv pip freeze > requirements.txt
# 然后手动将新依赖添加到pyproject.toml
```

### 插件开发

1. 查看`plugin_examples`目录下的示例插件
2. 创建新的Python文件实现插件功能
3. 确保插件结果存储在`result`变量中
4. 使用管理面板上传和激活插件

### 插件市场

LAT-LAB博客系统提供了插件市场功能，可以浏览和安装社区贡献的插件：

1. 访问管理面板的插件市场
2. 浏览可用插件并按分类/标签筛选
3. 查看插件详情和文档
4. 一键安装并激活插件

## 配置说明

主要配置在`src/lat_lab/core/config.py`文件中，可以通过环境变量或`.env`文件覆盖默认配置：

- 数据库连接
- JWT密钥和过期时间
- 邮件服务器配置
- 插件系统设置
- CORS设置

## 联系方式

- 项目主页：[https://github.com/A-Dawn/LAT-Lab](https://github.com/A-Dawn/LAT-Lab)
- 电子邮件：contact@luminarc.tech

## 许可证
LAT-Lab博客系统 © 2025，保留所有权利。

本人对LAT-Lab博客系统的代码、设计、文档及相关组件拥有知识产权和所有权。使用本项目内容前，请先获取许可。

所有权说明：

本项目的代码、设计和文档均为本人创作成果。
相关知识产权，包括著作权、专利权和商标权归本人所有。
如需使用本项目内容，请事先联系获取许可。
计划在标准制作完成并开放基于git仓库的插件市场后，考虑采用开源许可证进行部分内容授权。