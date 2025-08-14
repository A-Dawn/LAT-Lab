# LAT-Lab v1.0.1 - 现代博客系统

<div align="center">

**🌍 Languages / 语言选择**

[![简体中文](https://img.shields.io/badge/README-简体中文-blue.svg)](./README.md) [![English](https://img.shields.io/badge/README-English-red.svg)](./README_EN.md)

---

</div>

<div align="center">

![LAT-Lab Logo](https://img.shields.io/badge/LAT--Lab-v1.0.1-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red.svg)
![License](https://img.shields.io/badge/License-Hybrid-orange.svg)

**一个基于 FastAPI + Vue.js 构建的现代个人博客系统**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [技术架构](#-技术架构) • [开发工具](#-开发工具) • [部署指南](#-部署指南) • [贡献指南](#-贡献指南) • [安全](#️-安全) • [API文档](#-api文档)

</div>

---

## 📖 项目概述

LAT-Lab 是一个功能强大、架构现代的个人博客系统，采用前后端分离设计，提供完整的内容管理、用户系统、插件扩展和开发工具支持。系统不仅适合个人博客搭建，也为开发者提供了强大的二次开发能力。

### 🏷️ 版本信息
- **当前版本**: v1.0.1
- **发布日期**: 2025-08-15
- **Python**: 3.8+
- **Node.js**: 14+
- **数据库**: SQLite/MySQL

详细更新日志请查看 [CHANGELOG.md](./CHANGELOG.md)

---

## 🚀 功能特性

### 📝 内容管理系统
- **文章编辑**: 内置 Markdown 编辑器，支持实时预览
- **内容状态**: 草稿、已发布、私密文章管理
- **分类标签**: 灵活的分类和标签系统
- **可见性控制**: 公开、私密、密码保护文章
- **文章统计**: 浏览量、点赞数、评论数统计
- **文章置顶**: 重要文章置顶显示
- **RSS订阅**: 自动生成 RSS/Atom 订阅源

### 👥 用户管理系统
- **多角色管理**: 访客、用户、管理员三级权限
- **用户认证**: JWT 令牌认证，安全可靠
- **邮箱验证**: 用户注册邮箱验证机制
- **个人资料**: 头像、简介、个性化设置
- **安全增强**: 登录频率限制、密码加密存储

### 💬 评论互动系统
- **多级评论**: 支持无限层级评论回复
- **评论管理**: 管理员可审核、删除评论
- **实时更新**: 新评论实时显示
- **反垃圾**: 内置反垃圾评论机制

### 🔌 插件扩展系统
- **插件架构**: 可扩展的插件系统
- **插件市场**: 内置插件市场，支持一键安装 ([LAT-Lab-marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace))
- **自定义组件**: 支持前端自定义小部件
- **动态加载**: 插件热加载，无需重启
- **配置管理**: 插件独立配置系统
- **开源插件**: 插件生态采用 MIT 许可证，完全开源

### 🛠️ 开发工具系统
- **可视化编辑**: 实时页面编辑和预览
- **样式调试**: CSS 变量实时调整工具
- **文本编辑**: 批量文本内容编辑
- **布局工具**: 响应式布局可视化调整
- **代码导出**: 修改内容导出为代码
- **变更历史**: 完整的修改历史追踪
- **多页面支持**: 支持15种不同页面类型编辑

### 🔒 安全防护系统
- **错误处理**: 全局安全错误处理，防止信息泄露
- **敏感信息过滤**: 自动过滤密码、密钥等敏感信息
- **速率限制**: 多层级速率限制保护
- **安全装饰器**: 数据库、文件、网络操作安全包装
- **环境适配**: 开发/生产环境安全策略区分

---

## 🏗️ 技术架构

### 后端架构
基于 FastAPI 的后端，使用 SQLAlchemy ORM、JWT 认证和强大的安全特性。

### 前端架构
基于 Vue.js 3 的前端，采用现代组件架构和响应式设计。

### 数据库模型
采用关系型数据库设计，包含用户、文章、分类、标签、评论等核心表，支持完整的数据关联。

---

## 🚀 快速开始

### 环境准备
确保您的系统满足以下要求：
- Python 3.8 或更高版本
- Node.js 14 或更高版本
- MySQL 8.0+ (可选，默认使用 SQLite)
- Git (用于克隆代码)

### 方法一：传统安装 (推荐开发环境)

#### 1. 克隆项目
```bash
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab
```

#### 2. 后端配置
```bash
# 进入后端目录
cd backend

# 复制并编辑环境配置
cp ../env.example .env
# 编辑 .env 文件，设置必要的配置项

# 创建虚拟环境并安装依赖
python scripts/setup_env.py

# 激活虚拟环境
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 初始化数据库
mkdir -p data
python scripts/run_migrations.py run

# 初始化示例数据和插件
python -m src.lat_lab.init_examples

# 创建用户（-a参数为管理员） 
python scripts/create_user.py
# 启动后端服务
python -m src.lat_lab.main
```

#### 3. 前端配置
```bash
# 新开终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 访问系统
- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs (开发环境)
- **管理后台**: http://localhost:5173/admin

### 方法二：Docker 部署 (推荐生产环境)

#### 1. 准备配置
```bash
# 克隆项目
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab

# 复制并编辑环境配置
cp env.example .env
# 根据需要修改数据库密码等配置
```

#### 2. 构建并启动服务
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 初始化数据库 (首次部署)
docker-compose exec backend python scripts/run_migrations.py run
docker-compose exec backend python -m src.lat_lab.init_examples
docker-compose exec backend python scripts/init_db.py
```

#### 3. 访问系统
- **前端界面**: http://localhost (80端口)
- **后端API**: http://localhost:45609
- **管理后台**: http://localhost/admin

---

## 🛠️ 开发工具

LAT-Lab v1.0.0 引入了强大的前端开发工具系统，让您可以在浏览器中直接进行可视化开发和调试。

### 🎨 开发工具功能

#### 1. 页面选择器
- 支持15种不同页面类型的实时编辑
- iframe 嵌入式预览，真实模拟用户访问
- 跨域消息通信，实现即时同步

#### 2. 样式编辑器
- CSS 变量实时调整
- 颜色选择器集成
- 数值滑块控制
- 变更预览和一键撤销

#### 3. 文本编辑器
- 页面文本内容批量编辑
- 元素精确定位和高亮
- 多语言内容支持
- 修改内容实时预览

#### 4. 布局编辑器
- 元素尺寸可视化调整
- 位置属性直观编辑
- 响应式布局支持
- Grid/Flexbox 布局工具

#### 5. 代码导出器
- CSS 变量修改导出
- Vue 组件模板生成
- 配置文件自动生成
- 完整项目文件导出

#### 6. 变更历史
- 详细的操作时间轴
- 修改前后对比显示
- 一键回滚到任意历史点
- 批量操作撤销支持

### 🔧 开发工具使用

#### 启用开发工具
开发工具仅在开发环境下可用，确保您使用 `npm run dev` 启动前端服务。

#### 访问开发工具
1. 以管理员身份登录系统
2. 进入管理后台 (`/admin`)
3. 在左侧菜单中找到"开发工具"选项
4. 开始可视化编辑之旅！

#### 工作流程
```
选择页面 → 实时编辑 → 预览效果 → 导出代码 → 应用到项目
```

---

## 🔧 配置说明

### 环境变量配置

#### 基础配置
```env
# 应用配置
DEBUG=False                    # 生产环境设为False
HOST=0.0.0.0
PORT=8000

# 安全配置
SECRET_KEY=your_secret_key_here  # 请修改为随机密钥

# 数据库配置
DB_TYPE=sqlite                 # sqlite 或 mysql
MYSQL_USER=lat_lab_user
MYSQL_PASSWORD=your_db_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=lat_lab_db
```

#### 邮件服务配置
```env
# 邮件设置 (用于用户注册验证)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_FROM=your-email@example.com
MAIL_TLS=True
MAIL_SSL=False
```

#### 速率限制配置
```env
# 速率限制 (防止恶意请求)
RATE_LIMIT_ENABLED=True
RATE_LIMIT_LOGIN_REQUESTS=20      # 登录每分钟最多20次
RATE_LIMIT_API_REQUESTS=200       # API每分钟最多200次
RATE_LIMIT_UPLOAD_REQUESTS=20     # 上传每分钟最多20次
RATE_LIMIT_PLUGIN_REQUESTS=100    # 插件运行每分钟最多100次
```

#### 插件市场配置
```env
# 插件市场数据源
PLUGIN_MARKETPLACE_SOURCE=local        # local 或 git
PLUGIN_MARKETPLACE_GIT_REPO=           # Git仓库地址
PLUGIN_MARKETPLACE_GIT_BRANCH=main     # Git分支
PLUGIN_MARKETPLACE_GIT_TOKEN=          # Git访问令牌
```

### 数据库配置

#### SQLite (默认)
无需额外配置，系统会自动在 `backend/data/` 目录创建数据库文件。

#### MySQL
1. 创建数据库和用户：
```sql
CREATE DATABASE lat_lab_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lat_lab_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON lat_lab_db.* TO 'lat_lab_user'@'localhost';
FLUSH PRIVILEGES;
```

2. 更新 `.env` 文件中的数据库配置

### 插件配置

#### 插件目录结构
```
backend/
├── plugins/                   # 已安装的插件
├── plugin_examples/           # 示例插件
└── data/
    └── marketplace_config.json  # 插件市场配置
```

#### 创建自定义插件
参考 `backend/plugin_examples/` 目录中的示例插件，创建您的自定义插件。

## 🏗️ 项目结构

```
LAT-Lab/
├── backend/                   # 后端服务
│   ├── src/
│   │   └── lat_lab/
│   │       ├── api/           # API接口
│   │       ├── core/          # 核心配置
│   │       ├── crud/          # 数据库操作
│   │       ├── models/        # 数据模型
│   │       ├── schemas/       # 数据架构
│   │       ├── services/      # 服务层
│   │       ├── utils/         # 工具函数
│   │       └── main.py        # 应用入口
│   ├── scripts/               # 管理脚本
│   ├── data/                  # 数据存储
│   ├── uploads/               # 上传文件
│   ├── plugins/               # 已安装插件
│   ├── plugin_examples/       # 示例插件
│   └── pyproject.toml         # 项目配置
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/        # Vue组件
│   │   │   └── dev-tools/     # 开发工具组件
│   │   ├── views/             # 页面视图
│   │   │   └── admin/         # 管理后台
│   │   ├── store/             # Vuex状态管理
│   │   ├── services/          # API服务
│   │   ├── router/            # 路由配置
│   │   └── App.vue            # 根组件
│   ├── public/                # 静态资源
│   └── package.json           # 依赖配置
├── docs/                      # 文档
├── docker-compose.yml         # Docker配置
├── env.example                # 环境变量示例
└── README.md                  # 项目说明
```

---

## 🔐 安全最佳实践

### 生产环境安全配置

#### 1. 环境变量安全
```env
# 必须修改的配置项
SECRET_KEY=YOUR_RANDOM_SECRET_KEY_HERE
MYSQL_PASSWORD=YOUR_STRONG_DB_PASSWORD
DEBUG=False

# 邮件安全配置
MAIL_PASSWORD=YOUR_EMAIL_APP_PASSWORD
```

#### 2. 数据库安全
- 使用强密码
- 定期备份数据
- 限制数据库访问权限
- 启用 SSL 连接

#### 3. 文件上传安全
- 限制文件类型和大小
- 扫描上传文件
- 隔离存储上传文件

#### 4. 网络安全
- 使用 HTTPS
- 配置防火墙
- 启用速率限制
- 定期更新依赖

### 安全功能特性

#### 1. 错误处理
系统实现了全局安全错误处理，确保不会向用户泄露敏感的内部错误信息。

#### 2. 敏感信息过滤
自动过滤和隐藏以下类型的敏感信息：
- 密码 (password, pwd, passwd)
- 密钥 (secret, token, key, api_key)
- 认证信息 (access_token, refresh_token)

#### 3. 速率限制
多层级速率限制保护：
- 登录尝试限制
- API 请求频率限制
- 文件上传限制
- 插件执行限制

---

## 🚀 部署指南

### 生产环境部署 (Docker)

#### 1. 服务器准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 部署应用
```bash
# 克隆项目
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab

# 配置环境变量
cp env.example .env
nano .env  # 编辑配置

# 构建并启动
docker-compose up -d

# 初始化数据库（首次部署时）
docker-compose exec backend python scripts/run_migrations.py run
docker-compose exec backend python -m src.lat_lab.init_examples
docker-compose exec backend python scripts/create_user.py
```

> ⚠️ **注意事项**：
> - MySQL 8.0 配置使用 `mysql_native_password` 认证插件以确保兼容性
> - 执行初始化命令的顺序很重要，请严格按照上述顺序执行
> - 如果遇到 bcrypt 警告信息，可以安全忽略，只需确认看到"管理员用户创建成功"提示

#### 3. 反向代理配置 (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端API
    location /api/ {
        proxy_pass http://localhost:45609;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 文件上传
    location /uploads/ {
        proxy_pass http://localhost:45609;
        proxy_set_header Host $host;
        client_max_body_size 100M;
    }
}
```

### 性能优化

#### 1. 数据库优化
- 创建适当的索引
- 定期分析和优化查询
- 配置数据库连接池

#### 2. 缓存策略
- Redis 缓存热点数据
- 静态文件 CDN 加速
- 浏览器缓存配置

#### 3. 监控和日志
- 设置系统监控
- 配置日志轮转
- 性能指标追踪

---

## 🧪 开发指南

### 开发环境搭建

#### 1. 代码风格
后端使用 Black + isort + mypy 进行代码格式化和类型检查：
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 代码格式化
black src/
isort src/

# 类型检查
mypy src/
```

#### 2. 测试
```bash
# 运行测试
pytest

# 测试覆盖率
pytest --cov=src
```

### 插件开发

#### 1. 插件结构
```python
# plugin_info.json
{
    "id": "my_plugin",
    "name": "我的插件",
    "version": "1.0.0",
    "description": "插件描述",
    "author": "作者",
    "main": "main.py"
}

# main.py
def init_plugin():
    """插件初始化"""
    pass

def get_widget():
    """获取前端组件"""
    return {
        "name": "MyWidget",
        "component": "widget.vue"
    }
```

#### 2. 插件API
插件可以使用以下API：
- 数据库操作
- 用户认证
- 文件操作
- 邮件发送
- 缓存操作

### 前端开发

#### 1. 组件开发
```vue
<template>
  <div class="my-component">
    <!-- 组件内容 -->
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
// 组件逻辑
</script>

<style scoped>
/* 组件样式 */
</style>
```

#### 2. 状态管理
使用 Vuex 管理应用状态：
```javascript
// store/modules/myModule.js
const state = {
  // 状态定义
}

const mutations = {
  // 同步修改
}

const actions = {
  // 异步操作
}

const getters = {
  // 计算属性
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
```

---

## 🤝 贡献指南

### 参与贡献

⚠️ **重要提醒**: 本项目采用混合许可策略，插件和开发工具使用MIT许可，核心代码贡献需要签署 [贡献者许可协议](./CONTRIBUTOR_LICENSE_AGREEMENT.md)

我们欢迎以下形式的贡献：

#### 🆓 无需CLA的贡献
- 🐛 **Bug报告** - 发现问题并报告
- 💡 **功能建议** - 提出新功能想法
- 🔒 **安全漏洞** - 负责任披露（查看 [安全政策](./SECURITY.md)）
- 💬 **讨论参与** - 在Issues和Discussions中交流

#### 📝 需要CLA的贡献  
- 🔧 **代码提交** - 功能开发、Bug修复
- 📖 **文档改进** - 完善项目文档
- 🎨 **界面优化** - UI/UX改进

> 💡 **为什么需要CLA？** 由于核心代码采用专有许可证，需要明确代码版权归属，确保项目的法律合规性。开源组件（插件、开发工具）无需CLA。

### 提交规范

#### Commit 消息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type 类型
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 其他修改

#### 示例
```
feat(auth): 添加邮箱验证功能

- 实现邮箱验证令牌生成
- 添加验证邮件发送
- 完善用户注册流程

Closes #123
```

### 开发流程

#### 🔧 代码贡献流程
1. **阅读CLA** - 查看 [贡献者许可协议](./CONTRIBUTOR_LICENSE_AGREEMENT.md)
2. **Fork 项目** 到您的 GitHub 账户  
3. **创建分支** `git checkout -b feature/awesome-feature`
4. **开发功能** - 遵循代码规范进行开发
5. **提交更改** `git commit -m 'feat: add awesome-feature'`
6. **推送分支** `git push origin feature/awesome-feature`
7. **创建 Pull Request** 
8. **签署CLA** - 在PR中确认同意CLA条款
9. **代码审核** - 等待维护者审核
10. **合并代码** - 审核通过后合并

#### 🐛 Bug报告流程  
1. **搜索现有Issues** - 避免重复报告
2. **创建新Issue** - 使用Bug报告模板
3. **提供详细信息** - 复现步骤、环境信息等
4. **跟进处理** - 协助验证修复结果

> 📋 **CLA签署**: 小型代码贡献（<50行）可在PR中评论确认，大型贡献需要发送邮件，详情请查看许可协议。

---

## 🛡️ 安全政策

我们非常重视LAT-Lab的安全性，欢迎安全研究员报告漏洞：

- 🔒 **安全政策**: [SECURITY.md](./SECURITY.md) - 详细的安全报告指南
- 🏆 **安全贡献者**: [SECURITY_CONTRIBUTORS.md](./SECURITY_CONTRIBUTORS.md) - 安全研究员名单
- 📧 **安全邮箱**: security@luminarc.tech - 私密报告安全问题
- ⚡ **响应时间**: 24小时内确认，积极配合修复

我们承诺对善意的安全研究不采取法律行动，并会在安全贡献者名单中永久致谢。

---

## 📞 支持与反馈

### 获取帮助

- 📖 **文档**: 查看详细文档了解更多信息
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/A-Dawn/LAT-Lab/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/A-Dawn/LAT-Lab/discussions)
- 📧 **邮件联系**: contact@luminarc.tech

### 常见问题

#### Q: 如何修改默认管理员账户？
A: 运行 `python scripts/init_db.py` 时会创建默认管理员账户 (admin/admin123)，建议立即在管理后台修改密码。

#### Q: 如何配置邮件服务？
A: 在 `.env` 文件中配置 SMTP 服务器信息，支持大多数邮件服务提供商。

#### Q: 可以自定义主题吗？
A: 可以通过开发工具系统进行样式自定义，或直接修改前端源码。

#### Q: 如何备份数据？
A: 定期备份 `backend/data/` 目录和数据库文件，或使用数据库导出命令。

#### Q: 支持多语言吗？
A: 当前版本主要支持中文，多语言支持计划在后续版本中提供。

---

## 📜 许可证

**本项目采用混合许可策略，不同组件使用不同许可证。** 详细映射请查看 [LICENSE-MAPPING.md](./LICENSE-MAPPING.md)。

### 📋 许可证分布

#### 🔒 **核心业务代码** (专有许可证)
- **后端核心**: 用户认证、文章管理、数据库模型等
- **前端核心**: 管理后台、编辑器、用户界面等
- **配置文件**: 核心配置和路由系统

#### 🆓 **开放源码组件** (MIT 许可证)
- **插件系统**: 完整的插件架构和示例 ([LAT-Lab-marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace))
- **开发工具**: 可视化编辑器、样式调试工具等
- **通用组件**: 主题切换、消息提示、工具函数等
- **部署脚本**: Docker配置、安装脚本、环境设置等

### 📋 使用条款
- ✅ **个人学习**: 允许Fork用于个人学习和研究
- ✅ **插件开发**: 基于开源插件系统自由开发和分发插件
- ✅ **工具使用**: 开发工具可自由使用和修改
- ✅ **Bug报告**: 欢迎报告问题和提出建议  
- ✅ **安全研究**: 支持负责任的安全漏洞披露
- ❌ **核心商用**: 核心业务代码未经授权不得用于商业目的
- ❌ **核心分发**: 不得重新分发核心业务代码或创建完整衍生产品

### 🤝 贡献方式

#### 🔓 **开源组件贡献** (推荐)
- **插件开发**: 直接向 [LAT-Lab-marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace) 贡献插件
- **工具改进**: 提交开发工具和通用组件的改进
- **文档完善**: 帮助完善开源部分的文档

#### 🔒 **核心代码贡献**
- 需要签署 [贡献者许可协议](./CONTRIBUTOR_LICENSE_AGREEMENT.md)
- 适用于核心功能的Bug修复和改进

### 📞 商业授权
如需核心代码的商业使用授权，请联系：`contact@luminarc.tech`

---

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包
- [Element Plus](https://element-plus.org/) - Vue.js 组件库

特别感谢所有贡献者和使用者的支持！

---

<div align="center">

**🌟 如果这个项目对您有帮助，请给个 Star ⭐**

Made with ❤️ by [Dawn_ARC](https://github.com/A-Dawn)

</div>
