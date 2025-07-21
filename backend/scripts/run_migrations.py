#!/usr/bin/env python3
"""
LAT-LAB 数据库迁移脚本
用于运行数据库迁移
"""
import os
import sys
import subprocess
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()


def run_command(command, check=True):
    """运行shell命令"""
    print(f"执行: {' '.join(command)}")
    return subprocess.run(command, check=check)


def setup_alembic():
    """设置Alembic"""
    alembic_ini = PROJECT_ROOT / "alembic.ini"
    migrations_dir = PROJECT_ROOT / "migrations"
    
    # 检查alembic配置是否存在
    if not alembic_ini.exists():
        print("创建alembic.ini配置文件...")
        run_command(["alembic", "init", "migrations"])
        
        # 修改alembic.ini文件
        with open(alembic_ini, "r") as f:
            content = f.read()
        
        # 更新数据库URL
        content = content.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname",
            "sqlalchemy.url = sqlite:///./data/blog.db"
        )
        
        with open(alembic_ini, "w") as f:
            f.write(content)
    
    # 检查migrations目录
    if not migrations_dir.exists():
        os.makedirs(migrations_dir)
    
    return alembic_ini


def create_migration(message=None):
    """创建新的数据库迁移"""
    setup_alembic()
    
    cmd = ["alembic", "revision", "--autogenerate"]
    if message:
        cmd.extend(["-m", message])
    
    run_command(cmd)
    print("已创建数据库迁移文件")


def run_migrations():
    """运行数据库迁移"""
    setup_alembic()
    run_command(["alembic", "upgrade", "head"])
    print("数据库迁移完成")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LAT-LAB 数据库迁移工具")
    parser.add_argument("action", choices=["create", "run"], help="创建迁移或运行迁移")
    parser.add_argument("-m", "--message", help="迁移消息")
    
    args = parser.parse_args()
    
    if args.action == "create":
        create_migration(args.message)
    elif args.action == "run":
        run_migrations()


if __name__ == "__main__":
    main() 