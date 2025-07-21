# LAT-LAB 博客系统 v0.2.1 启用说明

## 项目介绍

LAT-LAB 博客系统是一个基于FastAPI和Vue.js的现代博客平台，支持文章发布、评论管理、分类管理、用户认证等功能，并提供插件系统扩展功能。

版本0.2.1升级了以下特性：
- 采用src项目结构，提高代码组织性
- 使用uv包管理工具，提升依赖管理效率
- 改进插件系统和市场功能
- 优化Docker部署配置

## 系统要求

- Python 3.8+
- Node.js 14+
- MySQL 8.0+ (可选，默认可使用SQLite)
- Docker和Docker Compose (可选，用于容器化部署)

## 安装与配置

### 方法一：直接安装（推荐用于开发）

1. **配置后端**：
   ```bash
   # 进入后端目录
   cd backend
   
   # 创建并配置环境变量
    cp ../env.example .env
    # 编辑.env文件，设置必要的配置项
   
   # 创建虚拟环境并安装依赖
   python scripts/setup_env.py
   
   # 激活虚拟环境
   # Windows:
   .\.venv\Scripts\activate
   # Linux/Mac:
   # source .venv/bin/activate
   
   # 创建数据目录(如果不存在)
   mkdir -p data
   
   # 运行数据库迁移(注意必须使用run参数)
   python scripts/run_migrations.py run
   
   # 初始化示例数据和插件
   python -m src.lat_lab.init_examples
   
   # 创建初始管理员用户 (默认用户名:admin 密码:admin123)(部署时必须修改init_db脚本内的管理员账密以及邮箱或自行使用sql命令修改)
   # 如遇到bcrypt警告可以忽略，只要看到"管理员用户创建成功"即可
   python scripts/init_db.py
   
   # 启动后端服务
   python -m src.lat_lab.main
   ```
   
2. **配置前端**：
   ```bash
   # 进入前端目录
   cd frontend
   
   # 安装依赖
   npm install
   
   # 开发环境: 启动开发服务器
   npm run dev
   
   # 生产环境: 构建前端项目
   npm run build
   # 构建完成后，dist目录包含所有静态文件，可部署到任何静态文件服务器
   ```

   **手动部署前端构建文件**:
   生产环境可以使用Nginx、Apache或其他Web服务器部署前端：
   ```bash
   # 例如，使用Nginx部署
   # 复制构建文件到Nginx网站目录
   cp -r frontend/dist/* /usr/share/nginx/html/
   
   # 配置Nginx代理后端API请求
   # 在Nginx配置中添加：
   # location /api {
   #     proxy_pass http://localhost:8000;
   # }
   ```

### 方法二：Docker部署（推荐用于生产）

1. **创建环境变量文件**：
   ```bash
   cp env.example backend/.env
   # 编辑.env文件，设置必要的配置项
   ```

2. **启动服务**：
   ```bash
   docker-compose up -d
   ```
   这将：
   - 启动数据库服务
   - 构建并启动后端服务
   - 构建前端生产版本并通过nginx服务
   - 自动配置前端与后端的连接

3. **初始化数据和创建管理员用户**（首次部署时）：
   ```bash
   # 复制配置文件
   docker-compose exec backend python scripts/copy_config.py
   
   # 运行数据库迁移
   docker-compose exec backend python scripts/run_migrations.py run
   
   # 初始化示例插件
   docker-compose exec backend python -m src.lat_lab.init_examples
   
   # 创建管理员用户 (默认用户名:admin 密码:admin123)
   # 如遇到bcrypt警告可以忽略，只要看到"管理员用户创建成功"即可
   docker-compose exec backend python scripts/init_db.py
   ```
   
   > ⚠️ **注意**：这些命令的执行顺序很重要，请按顺序执行。如果数据库文件被删除或需要重置，也需要按照这个顺序重新执行这些步骤。

4. **访问应用**：
   在浏览器中访问 http://localhost (默认端口80)
   - 前端: http://localhost
   - 后端API: http://localhost/api
   - API文档: http://localhost/api/docs

## 目录结构说明

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

frontend/
├── public/                # 静态资源
└── src/                   # 源代码
    ├── assets/           # 资源文件
    ├── components/       # Vue组件
    ├── router/           # 路由配置
    ├── services/         # API服务
    ├── store/            # Vuex状态管理
    └── views/            # 页面视图
```

## 插件系统

LAT-LAB博客系统提供了强大的插件扩展功能：

1. 内置插件示例位于 `backend/plugin_examples/` 目录
2. 用户可以开发自定义插件并放置于 `backend/plugins/` 目录
3. 通过管理界面可启用/禁用已安装的插件

## 常见问题

1. **数据库连接问题**：
   - 检查.env文件中的数据库配置
   - 确认MySQL服务正常运行
   - 查看日志以获取详细错误信息

2. **插件加载失败**：
   - 检查插件代码是否符合插件接口规范
   - 查看系统日志以获取详细错误信息
   - 确认插件目录权限正确

3. **邮件发送问题**：
   - 检查.env文件中的邮件服务器配置
   - 确认邮箱账号和密码正确

4. **创建新的数据库迁移**：
   - 首先确保已应用了所有现有迁移: `python scripts/run_migrations.py run`
   - 然后再创建新的迁移: `python scripts/run_migrations.py create -m "迁移说明"`
   - 如果遇到"Target database is not up to date"错误，请先运行现有迁移
   
5. **数据库表结构错误**：
   - 如果遇到"no such table"错误，说明数据库表结构未创建
   - 确保已运行数据库迁移: `python scripts/run_migrations.py run`
   - 如果删除了数据库文件，必须重新运行迁移才能创建表结构
   - 正确的初始化顺序: 运行迁移 → 初始化示例 → 创建管理员

6. **marketplace_config.json缺失**：
   - 运行 `python scripts/copy_config.py` 复制配置文件到所有需要的位置
   - 确保data目录已创建: `mkdir -p data`
   - 检查data目录中是否存在此文件

7. **bcrypt警告信息**：
   - 在创建管理员用户时可能出现"error reading bcrypt version"警告
   - 这是`passlib`库与`bcrypt`版本兼容性的问题，可以安全忽略
   - 只要看到"管理员用户创建成功"的信息，表示操作已完成

8. **重置/恢复数据库**：
   如果需要重置数据库或者数据库文件被删除后需要重新初始化，请按照以下步骤操作：
   ```bash
   # 1. 确保data目录存在
   mkdir -p data
   
   # 2. 复制必要的配置文件
   python scripts/copy_config.py
   
   # 3. 运行数据库迁移创建表结构
   python scripts/run_migrations.py run
   
   # 4. 初始化示例数据
   python -m src.lat_lab.init_examples
   
   # 5. 创建管理员账户
   python scripts/init_db.py
   ```
   这个顺序非常重要，否则可能会出现"no such table"错误
   
9. **前端开发环境API代理错误**：
   如果在开发模式下遇到 "connect ECONNREFUSED ::1:8000" 错误，请检查：
   - 确保后端服务器正在运行
   - 如果后端运行在不同主机/端口，请修改`frontend/vite.config.js`中的代理配置：
   ```javascript
   // 将 localhost 改为 127.0.0.1 可以解决部分连接问题
   server: {
     proxy: {
       '/api': {
         target: 'http://127.0.0.1:8000',  // 或修改为正确的后端地址
         changeOrigin: true
       }
     }
   }
   ```

## 安全配置建议

1. 在生产环境中，修改所有默认密码
2. 为SECRET_KEY设置强随机密钥
3. 限制数据库用户权限
4. 配置HTTPS以加密传输
5. 定期备份数据
6. **XSS防护**: 前端项目已集成DOMPurify库，对所有使用v-html的内容进行净化。详细的安全实践请参考`frontend/SECURITY.md`文件。
7. **内容安全策略(CSP)**: 在生产环境的Web服务器中配置适当的CSP头，限制脚本执行来源。

## 版本更新说明

v0.2.1相较于v0.2.0:
- 优化了src项目结构
- 增加了uv包管理工具支持
- 改进了Docker部署配置
- 优化了插件市场功能

## 技术支持

如有问题，请提交issue或联系开发团队，邮箱见contact@luminarc.tech。 