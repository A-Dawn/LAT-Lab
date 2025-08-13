FROM python:3.11-slim

WORKDIR /app

# 安装uv包管理工具
RUN pip install --no-cache-dir uv

# 复制项目文件
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# 安装项目依赖（使用uv）
RUN uv pip install -e .

# 创建头像目录
RUN mkdir -p uploads/avatars plugins

# 暴露端口
EXPOSE 8000

# 设置默认命令
CMD ["python", "-m", "src.lat_lab.main"] 