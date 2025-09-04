FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置Python环境变量
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 复制依赖文件
COPY pyproject.toml README.md ./

# 安装项目依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# 复制项目文件
COPY src/ ./src/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY migrations/ ./migrations/
COPY alembic.ini ./
COPY start.sh ./

# 设置启动脚本权限
RUN chmod +x /app/start.sh

# 创建必要的目录
RUN mkdir -p uploads/avatars uploads/articles plugins

# 设置权限
RUN chmod -R 755 uploads/ plugins/

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 设置默认命令
CMD ["/app/start.sh"] 