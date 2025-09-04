# LAT-Lab Backend

LAT-Lab 博客平台的后端服务，基于 FastAPI 构建。

## 功能特性

- 基于 FastAPI 的高性能 API 服务
- JWT 用户认证和授权
- 博客文章管理
- 插件系统支持
- 文件上传管理
- SQLAlchemy ORM 数据库操作
- 安全增强功能

## 技术栈

- **Web框架**: FastAPI
- **数据库**: SQLAlchemy + MySQL/SQLite
- **认证**: JWT + Passlib
- **文件处理**: Python-multipart
- **数据验证**: Pydantic
- **数据库迁移**: Alembic

## 快速开始

### 环境要求

- Python >= 3.8
- MySQL (可选，默认使用 SQLite)
- Node.js 14+ (如需完整部署前端)

### 完整安装步骤

#### 1. 配置环境变量
```bash
# 复制环境配置文件 (传统安装推荐使用SQLite)
cp env.traditional.example .env
# 编辑.env文件，设置必要的配置项
# 注意：传统安装默认使用SQLite数据库，无需额外配置
```

#### 2. 创建虚拟环境并安装依赖
```bash
# 使用 uv (推荐)
python scripts/setup_env.py

# 激活虚拟环境
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
# source .venv/bin/activate
```

#### 3. 初始化数据库和配置
```bash
# 创建数据目录(如果不存在)
mkdir -p data

# 运行数据库迁移(注意必须使用run参数)
python scripts/run_migrations.py run

# 初始化示例数据和插件
python -m src.lat_lab.init_examples

# 创建管理员用户
python scripts/init_db.py
# 注：若出现bcrypt警告可以忽略，只要看到"管理员用户创建成功"即可
```

#### 4. 启动服务
```bash
# 开发模式
python -m src.lat_lab.main

# 或使用uvicorn直接启动
uvicorn src.lat_lab.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档将在 http://localhost:8000/docs 可用。

### Docker 部署

```bash
# 从项目根目录执行
docker-compose up -d

# 初始化数据库（首次部署）
docker-compose exec backend python scripts/run_migrations.py run
docker-compose exec backend python -m src.lat_lab.init_examples
docker-compose exec backend python scripts/init_db.py
```

### 常见问题

1. **"Target database is not up to date"错误**:
   - 必须先运行现有迁移: `python scripts/run_migrations.py run`
   - 然后才能创建新的迁移: `python scripts/run_migrations.py create -m "迁移说明"`

2. **"no such table"错误**:
   - 说明数据库表结构未创建或数据库文件被删除
   - 确保已运行数据库迁移: `python scripts/run_migrations.py run`
   - 按照正确顺序初始化: 运行迁移 → 初始化示例 → 创建管理员

3. **marketplace_config.json缺失**:
   - 确保data目录已创建: `mkdir -p data`
   - 配置文件会在应用启动时自动创建

4. **bcrypt警告信息**:
   - 创建管理员时的"error reading bcrypt version"警告可以安全忽略
   - 只要看到"管理员用户创建成功"的信息，表示操作已完成

> ⚠️ **重要提示**：初始化命令的执行顺序非常关键，请务必按顺序执行。

## 开发

### 开发环境配置

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 或使用 pip
pip install -e ".[dev]"
```

### 代码格式化

```bash
# 格式化代码
black src/
isort src/

# 检查代码风格
flake8 src/
```

### 类型检查

```bash
mypy src/
```

### 运行测试

```bash
pytest
```

### 数据库迁移

```bash
# 创建新的迁移
python scripts/run_migrations.py create -m "迁移描述"

# 应用迁移
python scripts/run_migrations.py run

# 查看迁移历史
python scripts/run_migrations.py history
```

### 插件开发

1. 参考 `plugin_examples/` 目录中的示例插件
2. 编写插件代码并放置在 `plugins/` 目录
3. 通过管理界面或配置文件注册插件

### 安全配置

生产环境部署时，请注意：
- 修改 `config.py` 中的默认 SECRET_KEY
- 设置强密码策略
- 配置数据库连接安全
- 启用 HTTPS

## 项目结构

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

## 许可证

本项目采用混合许可策略：
- **核心后端代码**: 专有许可证
- **插件系统**: MIT 许可证 ([LAT-Lab-marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace))
- **开发工具**: MIT 许可证

详见项目根目录的 README.md 中的详细许可证说明。
