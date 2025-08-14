# 📜 许可证映射

<div align="center">

**🌍 Languages / 语言选择**

[![简体中文](https://img.shields.io/badge/License_Mapping-简体中文-blue.svg)](./LICENSE-MAPPING.md) [![English](https://img.shields.io/badge/License_Mapping-English-red.svg)](./LICENSE-MAPPING_EN.md)

</div>

本文件详细说明了 LAT-Lab 项目中各个组件的许可证分布。

## 🔒 专有许可证 (Proprietary License)

### 后端核心业务代码
```
backend/src/lat_lab/
├── api/
│   ├── auth.py           # 用户认证API
│   ├── article.py        # 文章管理API
│   ├── user.py          # 用户管理API
│   ├── comment.py       # 评论管理API
│   ├── category.py      # 分类管理API
│   ├── tag.py           # 标签管理API
│   └── upload.py        # 文件上传API
├── models/
│   ├── user.py          # 用户数据模型
│   ├── article.py       # 文章数据模型
│   ├── comment.py       # 评论数据模型
│   ├── category.py      # 分类数据模型
│   └── tag.py           # 标签数据模型
├── crud/                # 所有CRUD操作
├── core/
│   ├── auth.py          # 认证核心逻辑
│   ├── config.py        # 核心配置
│   ├── database.py      # 数据库连接
│   └── security.py      # 安全功能
├── schemas/             # 数据验证模式
└── main.py              # 应用入口
```

### 前端核心业务组件
```
frontend/src/
├── views/
│   ├── Login.vue        # 登录页面
│   ├── Register.vue     # 注册页面
│   ├── Home.vue         # 首页
│   ├── ArticleDetail.vue # 文章详情
│   ├── ArticleEditor.vue # 文章编辑器
│   ├── UserProfile.vue  # 用户资料
│   └── admin/           # 管理后台所有页面
├── router/index.js      # 路由配置
├── store/               # 状态管理
└── App.vue              # 主应用组件
```

## 🆓 MIT 许可证 (MIT License)

### 插件系统 (已迁移到独立仓库)
- **仓库**: [LAT-Lab-marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace)
- **许可证**: MIT License
- **内容**: 完整的插件生态系统

### 后端开源组件
```
backend/src/lat_lab/
├── api/plugin.py        # 插件API框架
├── models/plugin.py     # 插件数据模型
├── services/
│   └── marketplace.py   # 插件市场服务
├── utils/
│   ├── plugin_manager.py # 插件管理器
│   ├── security.py      # 安全工具函数
│   └── config_loader.py # 配置加载器
└── marketplace_config.json # 市场配置
```

### 前端开发工具系统
```
frontend/src/components/dev-tools/
├── StyleEditor.vue      # CSS变量编辑器
├── TextEditor.vue       # 文本内容编辑器
├── LayoutEditor.vue     # 布局调整器
├── PageSelector.vue     # 页面选择器
├── FileExporter.vue     # 代码导出工具
├── ChangeHistory.vue    # 变更历史
└── StatusIndicator.vue  # 状态指示器
```

### 前端通用组件
```
frontend/src/components/
├── ThemeSwitch.vue      # 主题切换
├── Toast.vue            # 消息提示
├── ConfirmDialog.vue    # 确认对话框
├── MarkdownEditor.vue   # Markdown编辑器
└── PluginWidget.vue     # 插件小部件
```

### 工具类和实用程序
```
frontend/src/utils/
├── crypto.js            # 加密工具
├── highlight.js         # 代码高亮
├── sanitize.js          # 内容过滤
└── toast.js             # 消息提示工具
```

### 部署和配置脚本
```
backend/scripts/         # 所有安装脚本
├── setup_env.py
├── init_db.py
├── run_migrations.py
└── create_user.py

配置文件:
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── package.json
```

### 文档和示例
```
docs/                    # 所有文档
examples/                # 示例代码
*.md                     # 除核心README外的文档
```

## 📋 许可证头部标记

### 专有许可证文件头部
```python
"""
LAT-Lab - 核心业务模块
版权所有 (c) 2025 Dawn_ARC
保留所有权利。本文件受专有软件许可证保护。

LAT-Lab - Core Business Module
Copyright (c) 2025 Dawn_ARC
All rights reserved. This file is protected by proprietary software license.
"""
```

### MIT许可证文件头部
```python
"""
LAT-Lab - 开源组件
MIT License

Copyright (c) 2025 Dawn_ARC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
```

## 🤝 贡献指南

### 开源组件贡献 (推荐)
1. **插件开发**: 直接向 [LAT-Lab-marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace) 贡献
2. **开发工具改进**: 提交PR到本仓库的开发工具组件
3. **通用组件优化**: 改进工具函数和通用UI组件
4. **文档完善**: 改进开源组件的文档

### 核心代码贡献
1. 需要签署 [贡献者许可协议](./CONTRIBUTOR_LICENSE_AGREEMENT.md)
2. 适用于核心功能的Bug修复和安全改进
3. 重大功能变更需要事先讨论

## 📞 联系方式

- **技术支持**: GitHub Issues
- **商业授权**: contact@luminarc.tech
- **安全问题**: security@luminarc.tech

**注：A-Dawn以及Dawn_ARC为同一人**

---

最后更新: 2025年8月
版本: v1.0.0 