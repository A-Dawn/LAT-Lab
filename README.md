# LAT-Lab v1.1.0 - 现代博客系统

<div align="center">

**🌍 Languages / 语言选择**

[![简体中文](https://img.shields.io/badge/README-简体中文-blue.svg)](./README.md) [![English](https://img.shields.io/badge/README-English-red.svg)](./README_EN.md)

---

</div>

<div align="center">

![LAT-Lab Logo](https://img.shields.io/badge/LAT--Lab-v1.1.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red.svg)
![License](https://img.shields.io/badge/License-Hybrid-orange.svg)

**一个基于 FastAPI + Vue.js 构建的现代个人博客系统**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [技术架构](#-技术架构) • [文档](#-文档) • [贡献指南](#-贡献指南) • [许可证](#-许可证)

</div>

---

## 📖 项目概述

LAT-Lab 是一个功能强大、架构现代的个人博客系统，采用前后端分离设计，提供完整的内容管理、用户系统、插件扩展和开发工具支持。系统不仅适合个人博客搭建，也为开发者提供了强大的二次开发能力。

### 🏷️ 版本信息
- **当前版本**: v1.1.0
- **发布日期**: 2025-08-15
- **Python**: 3.8+
- **Node.js**: 14+
- **数据库**: SQLite/MySQL

详细更新日志请查看 [CHANGELOG.md](./Docs/CHANGELOG.md)
- 🌍 **英文更新日志**: [CHANGELOG_EN.md](./Docs/CHANGELOG_EN.md)

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
- **用户名验证**: 完整的用户名验证系统，防止恶意注册和系统攻击
- **安全错误框架**: 统一的错误处理标准，防止敏感信息泄露
- **连接安全**: 邮件系统智能连接降级，支持SSL/TLS自动切换

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

### 🚀 一键部署 (推荐)

我们提供了快速部署脚本，自动检测环境并引导您完成部署：

#### Linux/macOS
```bash
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab
chmod +x deploy.sh
cp docker.env.example .env
# 根据实际环境更新 .env 配置
./deploy.sh start
# 可选：使用 `./deploy.sh logs` 观察启动日志
```

#### Windows PowerShell
```powershell
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab
Copy-Item docker.env.example .env
# 传统部署请复制 env.traditional.example
notepad .env
.\deploy.ps1 start
# 可选：执行 `.\deploy.ps1 logs` 查看启动日志
```

#### 部署脚本功能特性
- **跨平台支持**: 自动检测操作系统类型，提供相应的部署方案
- **环境检查**: 自动检查Docker、内存、磁盘空间等系统要求
- **健康监控**: 实时监控容器状态，自动重启失败的服务
- **智能部署**: 支持启动、停止、重启、状态查看、日志查看等操作
- **错误处理**: 完善的错误处理和重试机制，提高部署成功率

### 📚 详细部署指南
- **跨平台部署**: [DEPLOYMENT_GUIDE.md](./Docs/DEPLOYMENT_GUIDE.md) - 完整的部署脚本使用指南
- **Docker部署**: [DOCKER_DEPLOYMENT.md](./Docs/DOCKER_DEPLOYMENT.md) - Docker容器化部署详解
- **传统安装**: [TRADITIONAL_INSTALLATION.md](./Docs/TRADITIONAL_INSTALLATION.md) - 开发环境安装指南

---

## 🏗️ 项目结构

```
LAT-Lab/
├── backend/                   # 后端服务
│   ├── src/lat_lab/          # 应用核心代码
│   ├── scripts/              # 管理脚本
│   ├── data/                 # 数据存储
│   ├── uploads/              # 上传文件
│   ├── plugins/              # 已安装插件
│   └── plugin_examples/      # 示例插件
├── frontend/                 # 前端应用
│   ├── src/                  # Vue.js 源码
│   ├── public/               # 静态资源
│   └── package.json          # 依赖配置
├── Docs/                     # 项目文档
├── docker-compose.yml        # Docker配置
├── docker.env.example        # Docker 部署环境配置模板
├── env.traditional.example   # 传统部署环境配置模板
├── deploy.sh                 # Linux/macOS 跨平台部署脚本
├── deploy.ps1                # Windows PowerShell 跨平台部署脚本
└── README.md                 # 项目说明
```

---

## 📚 文档

### 📚 完整文档中心
- **[文档中心](./Docs/README.md)** - 查看所有项目文档和详细指南

### 核心文档
- 📖 **项目概述**: 您正在阅读的文件
- 📝 **更新日志**: [CHANGELOG.md](./Docs/CHANGELOG.md) - 版本更新记录
- 🔐 **安全政策**: [SECURITY.md](./Docs/SECURITY.md) - 安全报告指南

### 部署指南
- 🚀 **快速部署**: [DEPLOYMENT_GUIDE.md](./Docs/DEPLOYMENT_GUIDE.md) - 跨平台部署脚本使用指南
- 🐳 **Docker部署**: [DOCKER_DEPLOYMENT.md](./Docs/DOCKER_DEPLOYMENT.md) - Docker容器化部署详解

### 贡献相关
- 🤝 **贡献指南**: [CONTRIBUTORS.md](./Docs/CONTRIBUTORS.md) - 如何参与项目贡献
- 📄 **贡献者协议**: [CONTRIBUTOR_LICENSE_AGREEMENT.md](./Docs/CONTRIBUTOR_LICENSE_AGREEMENT.md) - 贡献者许可协议
- 🏆 **安全贡献者**: [SECURITY_CONTRIBUTORS.md](./Docs/SECURITY_CONTRIBUTORS.md) - 安全研究员名单

### 许可证相关
- 📜 **许可证映射**: [LICENSE-MAPPING.md](./Docs/LICENSE-MAPPING.md) - 详细的许可证说明
- 🔍 **英文文档**: 每个文档都提供对应的英文版本（文件名以_EN结尾）
- 🌍 **完整英文文档**: [查看所有英文文档](./Docs/README_EN.md)

---

## 🤝 贡献指南

⚠️ **重要提醒**: 本项目采用混合许可策略，插件和开发工具使用MIT许可，核心代码贡献需要签署 [贡献者许可协议](./Docs/CONTRIBUTOR_LICENSE_AGREEMENT.md)

### 快速参与方式

#### 🆓 无需CLA的贡献
- 🐛 **Bug报告** - 发现问题并报告
- 💡 **功能建议** - 提出新功能想法
- 🔒 **安全漏洞** - 负责任披露（查看 [安全政策](./Docs/SECURITY.md)）
- 💬 **讨论参与** - 在Issues和Discussions中交流

#### 📝 需要CLA的贡献  
- 🔧 **代码提交** - 功能开发、Bug修复
- 📖 **文档改进** - 完善项目文档
- 🎨 **界面优化** - UI/UX改进

### 提交流程
1. Fork 项目到您的 GitHub 账户
2. 创建功能分支 `git checkout -b feature/awesome-feature`
3. 提交更改 `git commit -m 'feat: add awesome-feature'`
4. 推送分支 `git push origin feature/awesome-feature`
5. 创建 Pull Request
6. 签署CLA（如需要）

详细的贡献指南请查看 [CONTRIBUTORS.md](./Docs/CONTRIBUTORS.md)
- 🌍 **英文贡献指南**: [CONTRIBUTORS_EN.md](./Docs/CONTRIBUTORS_EN.md)

---

## 🛡️ 安全政策

我们非常重视LAT-Lab的安全性，欢迎安全研究员报告漏洞：

- 🔒 **安全政策**: [SECURITY.md](./Docs/SECURITY.md) - 详细的安全报告指南
- 🌍 **英文安全政策**: [SECURITY_EN.md](./Docs/SECURITY_EN.md)
- 🏆 **安全贡献者**: [SECURITY_CONTRIBUTORS.md](./Docs/SECURITY_CONTRIBUTORS.md) - 安全研究员名单
- 🌍 **英文安全贡献者指南**: [SECURITY_CONTRIBUTORS_EN.md](./Docs/SECURITY_CONTRIBUTORS_EN.md)
- 📧 **安全邮箱**: security@luminarc.tech - 私密报告安全问题
- ⚡ **响应时间**: 24小时内确认，积极配合修复

---

## 📞 支持与反馈

### 获取帮助
- 📖 **文档**: 查看 [Docs](./Docs/) 目录了解详细信息
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/A-Dawn/LAT-Lab/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/A-Dawn/LAT-Lab/discussions)
- 📧 **邮件联系**: contact@luminarc.tech

### 常见问题
常见问题解答请查看 [FAQ.md](./Docs/FAQ.md) 或 [文档中心](./Docs/README.md)
- 🌍 **英文FAQ**: [FAQ_EN.md](./Docs/FAQ_EN.md)

---

## 📜 许可证

**本项目采用混合许可策略，不同组件使用不同许可证。** 

### 📋 许可证分布
- 🔒 **核心业务代码** (专有许可证): 后端核心、前端核心、配置文件
- 🆓 **开放源码组件** (MIT 许可证): 插件系统、开发工具、通用组件、部署脚本

### 📋 使用条款
- ✅ **个人学习**: 允许Fork用于个人学习和研究
- ✅ **插件开发**: 基于开源插件系统自由开发和分发插件
- ✅ **工具使用**: 开发工具可自由使用和修改
- ❌ **核心商用**: 核心业务代码未经授权不得用于商业目的

详细的许可证说明请查看 [LICENSE-MAPPING.md](./Docs/LICENSE-MAPPING.md)
- 🌍 **英文许可证说明**: [LICENSE-MAPPING_EN.md](./Docs/LICENSE-MAPPING_EN.md)

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
