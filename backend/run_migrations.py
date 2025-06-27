#!/usr/bin/env python3
"""
数据库迁移脚本，用于运行Alembic迁移
"""

import os
import sys
import subprocess
import argparse

def run_migrations(revision=None, downgrade=False):
    """运行数据库迁移"""
    # 确保我们在正确的目录中
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 构建命令
    cmd = ["alembic"]
    
    if downgrade:
        cmd.extend(["downgrade", revision or "base"])
    else:
        if revision:
            cmd.extend(["upgrade", revision])
        else:
            cmd.extend(["upgrade", "head"])
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行迁移命令
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print("迁移成功完成!")
        else:
            print(f"迁移失败，返回代码: {result.returncode}")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"迁移执行错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="运行数据库迁移")
    parser.add_argument(
        "--revision", "-r",
        help="指定要迁移到的版本 (默认: head)",
        default=None
    )
    parser.add_argument(
        "--downgrade", "-d",
        help="降级而不是升级",
        action="store_true"
    )
    
    args = parser.parse_args()
    run_migrations(args.revision, args.downgrade)

if __name__ == "__main__":
    main() 