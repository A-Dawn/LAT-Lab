# LAT-Lab 博客系统

LAT-Lab是一个现代化的个人博客系统，基于前后端分离架构，提供丰富的功能和插件扩展能力。

## 项目概述

LAT-Lab博客系统是一个完整的博客解决方案，包含文章管理、用户管理、分类标签、评论系统和强大的插件机制。系统采用前后端分离架构，后端使用FastAPI构建RESTful API，前端使用Vue.js提供现代化的用户界面。

### 版本信息
- 当前版本: v0.1.0
- 发布日期: 2025-06-28

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

### 后端安装
1. 进入backend目录
```bash
cd backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行数据库迁移
```bash
python run_migrations.py
```

4. 初始化示例数据和插件
```bash
python init_examples.py
python init_plugin_examples.py
python init_plugin_marketplace.py
```

5. 创建管理员用户
```bash
# 使用交互式Python脚本创建管理员
python setup_tools/create_admin_user.py

# 或者使用SQL脚本创建默认管理员 (用户名: admin, 密码: admin123)
# ⚠️ 强烈建议在生产环境中立即修改默认密码
sqlite3 blog.db < setup_tools/add_admin.sql
```

> 💡 更多管理工具说明请查看 `backend/setup_tools/README.md`

6. 启动后端服务
```bash
python run.py
```

### 前端安装
1. 进入frontend目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 开发模式运行
```bash
npm run dev
```

4. 构建生产版本
```bash
npm run build
```

### 使用Docker部署
可以使用Docker Compose快速部署整个系统：
```bash
docker-compose up -d
```

## 插件市场

LAT-Lab博客系统提供了强大的插件市场功能，允许管理员浏览、安装和管理各种插件。插件市场基于JSON配置文件，开发者可以通过编辑配置文件来添加新的插件。

### 插件功能
- 浏览可用插件
- 按分类和标签筛选
- 查看插件详情和截图
- 一键安装插件

## 配置说明

### 后端配置
主要配置文件位于`backend/app/core/config.py`，可以通过环境变量覆盖默认设置：
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
1. 参考`backend/app/plugin_examples`目录中的示例插件
2. 编写插件代码并放置在适当位置
3. 通过管理界面或配置文件注册插件

### 贡献代码
在标准制作完成并开放git插件市场后，计划接受社区贡献。

## 许可证
LAT-Lab博客系统 © 2025，保留所有权利。

本项目目前不开放源代码许可。未经明确授权，不得复制、修改或分发本软件。
计划于标准制作完成并开放基于git仓库的插件市场后，采用合适的开源许可证。

## 联系方式
如有问题或建议，请通过以下方式联系我们：
- 项目主页：[https://github.com/A-Dawn/LAT-Lab](https://github.com/A-Dawn/LAT-Lab)
- 电子邮件：your-email@example.com

---
LAT-Lab博客系统 © 2025 