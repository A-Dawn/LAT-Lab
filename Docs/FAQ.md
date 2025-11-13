# LAT-Lab 常见问题解答 (FAQ)

本文档收集了 LAT-Lab 项目使用过程中的常见问题和解答。

---

## 🚀 部署相关

### Q: 如何修改默认管理员账户？
**A**: 运行 `python scripts/init_db.py` 时会创建默认管理员账户 (admin/admin123)，建议立即在管理后台修改密码。

### Q: 如何配置邮件服务？
**A**: 在 `.env`（或 `docker.env.example`）中填写 SMTP 凭据即可完成配置。详细变量说明可参考 [Docker 部署指南](./DOCKER_DEPLOYMENT.md) 与 [传统安装指南](./TRADITIONAL_INSTALLATION.md) 中的配置章节。

### Q: Docker 部署时端口被占用怎么办？
**A**: 可以通过以下方式解决：
1. 修改 `docker-compose.yml` 中的端口映射
2. 使用 `netstat -tulpn | grep :端口号` 查看占用进程
3. 使用 `sudo kill -9 <PID>` 杀死占用进程

### Q: 生产环境部署需要注意什么？
**A**: 生产环境部署时：
1. 绝对不要使用 `npm run dev`，必须使用 `npm run build`
2. 配置 HTTPS 证书
3. 设置强密码和安全的 SECRET_KEY
4. 配置防火墙和访问控制
5. 定期备份数据

---

## 🔧 功能使用

### Q: 可以自定义主题吗？
**A**: 可以。您可以直接修改 `frontend/src/assets` 下的主题样式文件（如 `theme-light.css`、`theme-dark.css`、`theme-neon.css`），或调整相关的 Vue 组件。修改后请按照 `frontend/README.md` 提供的构建命令重新打包前端。

### Q: 如何添加新的插件？
**A**: 可以先查看 `backend/plugin_examples` 中的示例插件以及 `backend/src/lat_lab/marketplace_config.json` 中的元数据格式。按照同样的结构实现后，可本地加载或提交到 [插件市场](https://github.com/A-Dawn/LAT-Lab-marketplace)。

### Q: 支持哪些数据库？
**A**: 默认支持 SQLite，生产环境推荐使用 MySQL 8.0+。具体的配置示例可参见 [Docker 部署指南](./DOCKER_DEPLOYMENT.md) 和 [传统安装指南](./TRADITIONAL_INSTALLATION.md)。

### Q: 如何备份和恢复数据？
**A**: 数据备份方法：
1. **数据库备份**: `docker-compose exec db mysqldump -u root -p lat_lab_db > backup.sql`
2. **文件备份**: `tar -czf uploads_backup.tar.gz uploads/`
3. **完整备份**: 同时保留数据库导出与上传文件压缩包（或对 Docker 卷进行快照）

---

## 🐛 故障排除

### Q: 服务启动失败怎么办？
**A**: 按以下步骤排查：
1. 检查日志: `./deploy.sh logs` 或 `docker-compose logs`
2. 检查环境配置: 确认 `.env` 文件配置正确
3. 检查端口占用: 确认所需端口未被占用
4. 检查资源: 确认内存和磁盘空间充足

### Q: 前端页面显示异常？
**A**: 可能的原因和解决方法：
1. **API 连接失败**: 检查后端服务是否正常运行
2. **静态资源加载失败**: 检查前端构建是否正确
3. **浏览器兼容性**: 建议使用现代浏览器

### Q: 邮件发送失败？
**A**: 邮件发送问题排查：
1. 检查 SMTP 配置是否正确
2. 确认邮箱服务商是否支持 SMTP
3. 检查网络连接和防火墙设置
4. 查看邮件服务日志

---

## 🔒 安全相关

### Q: 如何提高系统安全性？
**A**: 安全建议：
1. 定期更新密码和 SECRET_KEY
2. 启用 HTTPS
3. 配置防火墙规则
4. 定期备份数据
5. 监控系统日志
6. 及时更新依赖包

### Q: 发现安全漏洞怎么办？
**A**: 请通过以下方式报告安全漏洞：
1. 发送邮件到 security@luminarc.tech
2. 在 GitHub 上创建私有 Issue
3. 详细描述漏洞情况和复现步骤

---

## 📱 移动端支持

### Q: 支持移动端访问吗？
**A**: 是的，LAT-Lab 采用响应式设计，支持各种移动设备访问。建议在移动端使用现代浏览器以获得最佳体验。

### Q: 移动端功能是否完整？
**A**: 移动端支持所有核心功能，包括：
- 文章浏览和搜索
- 用户登录和注册
- 评论发布和回复
- 管理后台操作

---

## 🔌 插件开发

### Q: 如何开发自定义插件？
**A**: 建议流程如下：
1. 阅读 `backend/plugin_examples` 中的参考插件
2. 将示例复制到 `backend/plugins`（或自建仓库），并按 `backend/src/lat_lab/marketplace_config.json` 定义元数据
3. 本地实现并测试插件功能
4. 打包后提交到 [插件市场](https://github.com/A-Dawn/LAT-Lab-marketplace)（可选）

### Q: 插件开发需要什么技能？
**A**: 插件开发需要：
- 基本的 Python 编程知识
- 了解 FastAPI 框架
- 熟悉 HTML/CSS/JavaScript
- 了解 Vue.js 组件开发

---

## 📊 性能优化

### Q: 如何提高系统性能？
**A**: 性能优化建议：
1. 使用 CDN 加速静态资源
2. 配置数据库索引
3. 启用缓存机制
4. 优化图片和媒体文件
5. 使用负载均衡

### Q: 支持高并发访问吗？
**A**: LAT-Lab 采用异步架构，支持高并发访问。建议在生产环境使用：
- 多实例部署
- 负载均衡
- 数据库读写分离
- 缓存策略

---

## 🌐 国际化

### Q: 支持多语言吗？
**A**: 目前支持中文和英文，更多语言正在规划中。如需新增语言，可参考 `frontend/src` 中现有的翻译资源结构，补充对应的文案与界面，并通过 Pull Request 提交。

### Q: 如何切换语言？
**A**: 语言切换方式：
1. 在用户设置中选择语言
2. 通过 URL 参数指定语言
3. 根据浏览器语言自动选择

---

## 📞 获取帮助

如果本文档没有解决您的问题，可以通过以下方式获取帮助：

1. **查看文档**: [文档中心](./README.md)
2. **搜索问题**: 在 [GitHub Issues](https://github.com/A-Dawn/LAT-Lab/issues) 中搜索
3. **创建问题**: 创建新的 Issue 描述问题
4. **参与讨论**: 在 [GitHub Discussions](https://github.com/A-Dawn/LAT-Lab/discussions) 中交流
5. **邮件联系**: contact@luminarc.tech

---

<div align="center">

**🌟 如果这个FAQ对您有帮助，请给项目一个 Star ⭐**

Made with ❤️ by [Dawn_ARC](https://github.com/A-Dawn)

</div> 