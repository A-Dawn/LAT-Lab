#!/bin/bash

echo "=== LAT-LAB 后端服务启动脚本 ==="
echo "等待数据库服务启动..."

# 等待数据库完全启动
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    echo "尝试连接数据库... (第 $attempt 次)"
    
    # 简单的数据库连接测试
    if python -c "
import os
import sys
sys.path.insert(0, '/app/src')
try:
    from lat_lab.core.database import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    db.execute(text('SELECT 1'))
    db.close()
    print('数据库连接成功')
    exit(0)
except Exception as e:
    print(f'数据库连接失败: {e}')
    exit(1)
" 2>/dev/null; then
        echo "数据库连接成功！"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "错误：无法连接到数据库，已达到最大重试次数"
        exit 1
    fi
    
    echo "数据库尚未就绪，等待 5 秒后重试..."
    sleep 5
    attempt=$((attempt + 1))
done

echo "开始初始化数据库..."

# 运行数据库迁移
echo "运行数据库迁移..."
cd /app && python scripts/run_migrations.py

if [ $? -eq 0 ]; then
    echo "数据库迁移完成"
else
    echo "警告：数据库迁移失败，但继续执行..."
fi

# 初始化数据库和创建默认管理员
echo "初始化数据库..."
cd /app && python scripts/init_db.py

if [ $? -eq 0 ]; then
    echo "数据库初始化完成"
else
    echo "警告：数据库初始化失败，但继续执行..."
fi

echo "启动 LAT-LAB 后端服务..."

# 启动主应用
cd /app && exec python -m src.lat_lab.main 