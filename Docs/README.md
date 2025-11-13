# 📚 LAT-Lab 项目文档

欢迎来到 LAT-Lab 项目的文档中心！这里包含了项目的所有重要文档和说明。

## 🆕 最新更新亮点（v1.1.0）

- **身份安全**：新增 `must_change_password` 标记与相关接口，管理员可要求特定账号在下次登录时强制修改密码。
- **管理端开发者工具重构**：后台开发工具新增状态面板、元素导航、修改历史与导出页，并通过全新的内容净化工具保障安全。
- **部署脚本统一**：`deploy.sh` / `deploy.ps1` 覆盖 Docker 与传统部署，集成健康检查、日志流与资源清理等运维能力。
- **环境模板扩展**：`docker.env.example` 与 `env.traditional.example` 增补资源配额、日志策略以及 `VITE_ENABLE_DEV_TOOLS` 等前端开关。

## 📋 文档分类

### 🚀 部署指南
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - 跨平台部署脚本使用指南 (中文)
- **[DEPLOYMENT_GUIDE_EN.md](./DEPLOYMENT_GUIDE_EN.md)** - 跨平台部署脚本使用指南 (English)
- **[DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)** - Docker容器化部署指南 (中文)
- **[DOCKER_DEPLOYMENT_EN.md](./DOCKER_DEPLOYMENT_EN.md)** - Docker容器化部署指南 (English)
- **[TRADITIONAL_INSTALLATION.md](./TRADITIONAL_INSTALLATION.md)** - 传统安装部署指南 (中文)
- **[TRADITIONAL_INSTALLATION_EN.md](./TRADITIONAL_INSTALLATION_EN.md)** - 传统安装部署指南 (English)

### 🔐 安全相关
- **[SECURITY.md](./SECURITY.md)** - 安全政策 (中文)
- **[SECURITY_EN.md](./SECURITY_EN.md)** - 安全政策 (English)
- **[SECURITY_CONTRIBUTORS.md](./SECURITY_CONTRIBUTORS.md)** - 安全贡献者指南 (中文)
- **[SECURITY_CONTRIBUTORS_EN.md](./SECURITY_CONTRIBUTORS_EN.md)** - 安全贡献者指南 (English)

### 📝 功能说明
- **[GUEST_MODE_README.md](./GUEST_MODE_README.md)** - 访客模式功能说明
- **[FAQ.md](./FAQ.md)** - 常见问题解答 (中文)
- **[FAQ_EN.md](./FAQ_EN.md)** - 常见问题解答 (English)

### 📄 许可证相关
- **[LICENSE-MAPPING.md](./LICENSE-MAPPING.md)** - 许可证映射说明 (中文)
- **[LICENSE-MAPPING_EN.md](./LICENSE-MAPPING_EN.md)** - 许可证映射说明 (English)
- **[CONTRIBUTOR_LICENSE_AGREEMENT.md](./CONTRIBUTOR_LICENSE_AGREEMENT.md)** - 贡献者许可协议 (中文)
- **[CONTRIBUTOR_LICENSE_AGREEMENT_EN.md](./CONTRIBUTOR_LICENSE_AGREEMENT_EN.md)** - 贡献者许可协议 (English)

### 👥 贡献相关
- **[CONTRIBUTORS.md](./CONTRIBUTORS.md)** - 贡献者列表 (中文)
- **[CONTRIBUTORS_EN.md](./CONTRIBUTORS_EN.md)** - 贡献者列表 (English)

### 📈 更新记录
- **[CHANGELOG.md](./CHANGELOG.md)** - 更新日志 (中文)
- **[CHANGELOG_EN.md](./CHANGELOG_EN.md)** - 更新日志 (English)

## 🎯 快速导航

### 新用户入门
1. 查看 [项目概述](../README.md) 了解项目
2. 选择部署方式：
   - **推荐**: 使用 [跨平台部署脚本](./DEPLOYMENT_GUIDE.md) (支持一键部署)
   - 开发环境：使用 [传统安装](./TRADITIONAL_INSTALLATION.md) | [English](./TRADITIONAL_INSTALLATION_EN.md)
   - 生产环境：使用 [Docker部署](./DOCKER_DEPLOYMENT.md) | [English](./DOCKER_DEPLOYMENT_EN.md)

### 开发者指南
1. 阅读 [贡献指南](../README.md#-贡献指南)
2. 了解 [安全政策](./SECURITY.md) | [English](./SECURITY_EN.md)
3. 查看 [更新日志](./CHANGELOG.md) | [English](./CHANGELOG_EN.md)

### 功能使用
1. 了解 [访客模式](./GUEST_MODE_README.md) 功能
2. 查看前端使用指南：
   - [导出文件使用指南](../frontend/导出文件使用指南.md)
   - [导出文件快速使用参考](../frontend/导出文件快速使用参考.md)
3. 查看常见问题： [FAQ](./FAQ.md) | [English](./FAQ_EN.md)

## 🔗 相关链接

- **项目主页**: [README.md](../README.md) | [English](../README_EN.md)
- **后端说明**: [backend/README.md](../backend/README.md)
- **前端说明**: [frontend/README.md](../frontend/README.md)

### 🌍 多语言文档
- **部署指南**: [中文](./DEPLOYMENT_GUIDE.md) | [English](./DEPLOYMENT_GUIDE_EN.md)
- **Docker部署**: [中文](./DOCKER_DEPLOYMENT.md) | [English](./DOCKER_DEPLOYMENT_EN.md)
- **传统安装**: [中文](./TRADITIONAL_INSTALLATION.md) | [English](./TRADITIONAL_INSTALLATION_EN.md)
- **安全政策**: [中文](./SECURITY.md) | [English](./SECURITY_EN.md)
- **常见问题**: [中文](./FAQ.md) | [English](./FAQ_EN.md)
- **许可证说明**: [中文](./LICENSE-MAPPING.md) | [English](./LICENSE-MAPPING_EN.md)
- **贡献指南**: [中文](./CONTRIBUTORS.md) | [English](./CONTRIBUTORS_EN.md)
- **更新日志**: [中文](./CHANGELOG.md) | [English](./CHANGELOG_EN.md)

## 📞 获取帮助

如果您需要帮助或有疑问：

1. 查看相关文档
2. 在项目 Issues 中搜索
3. 创建新的 Issue 描述问题
4. 参与项目讨论

---

**注意**: 本文档会随着项目发展持续更新，建议定期查看最新版本。 